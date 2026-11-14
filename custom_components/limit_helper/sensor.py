"""Sensor platform for Limit Helper."""
from __future__ import annotations

from collections import deque
from datetime import datetime
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_call_later, async_track_state_change_event
import homeassistant.util.dt as dt_util

from .const import (
    ATTR_ACTIVE_ZONE_INDEX,
    ATTR_ACTIVE_ZONE_LABEL,
    ATTR_CURRENT_VALUE,
    ATTR_GRADIENT,
    ATTR_GRADIENT_ALERT,
    ATTR_GRADIENT_THRESHOLD,
    ATTR_HOLD_TIME,
    ATTR_HYSTERESIS,
    ATTR_IN_RANGE,
    ATTR_IS_ABOVE,
    ATTR_IS_BELOW,
    ATTR_LABELS,
    ATTR_MODE,
    ATTR_OUTSIDE_RANGE,
    ATTR_PENDING_STATE,
    ATTR_PRESET,
    ATTR_RESOLVED_THRESHOLDS,
    ATTR_SOURCE_ENTITY,
    ATTR_THRESHOLDS,
    ATTR_TREND,
    CONF_GRADIENT_THRESHOLD,
    CONF_HOLD_TIME,
    CONF_HYSTERESIS,
    CONF_ICON,
    CONF_LABELS,
    CONF_MODE,
    CONF_PRESET,
    CONF_SOURCE_ENTITY,
    CONF_THRESHOLDS,
    DEFAULT_GRADIENT_THRESHOLD,
    DEFAULT_HOLD_TIME,
    DEFAULT_HYSTERESIS,
    DEFAULT_ICON,
    DEFAULT_MODE,
    DEFAULT_NAME,
    DEFAULT_PRESET,
    MODE_ABOVE_LIMIT,
    MODE_BELOW_LIMIT,
    MODE_INSIDE_RANGE,
    MODE_MULTI_ZONE,
    MODE_OUTSIDE_RANGE,
)

_LOGGER = logging.getLogger(__name__)


def parse_threshold_items(thresh_str: str) -> list[str]:
    """Parse comma-separated threshold items (can be numbers or entity IDs)."""
    return [p.strip() for p in str(thresh_str).split(",") if p.strip()]


def parse_labels(labels_str: str, required_count: int) -> list[str]:
    """Parse comma-separated labels string, padding if necessary."""
    parts = [l.strip() for l in str(labels_str).split(",") if l.strip()]
    while len(parts) < required_count:
        parts.append(f"zone_{len(parts) + 1}")
    return parts[:required_count]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Limit sensor from config entry."""
    async_add_entities([LimitSensor(entry)], True)


class LimitSensor(SensorEntity):
    """Representation of an advanced Limit & Multi-Tier Zone Helper Sensor."""

    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_translation_key = "limit_helper"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        self._entry = entry
        config = {**entry.data, **entry.options}

        custom_name = config.get(CONF_NAME)
        if custom_name and custom_name not in (
            DEFAULT_NAME,
            "Limit Helper",
            "Grenzwert-Helfer",
            "Pembantu Batas",
        ):
            self._attr_name = custom_name
        else:
            self._attr_name = None
        self._attr_unique_id = f"{entry.entry_id}_limit"

        self._source_entity: str = config.get(CONF_SOURCE_ENTITY, "")
        self._mode: str = config.get(CONF_MODE, DEFAULT_MODE)
        self._preset: str = config.get(CONF_PRESET, DEFAULT_PRESET)

        self._raw_threshold_items: list[str] = parse_threshold_items(
            config.get(CONF_THRESHOLDS, "20, 80")
        )
        self._dynamic_threshold_entities: list[str] = [
            item
            for item in self._raw_threshold_items
            if "." in item
            and not item.replace(".", "", 1).replace("-", "").isdigit()
        ]

        # Determine required labels based on mode
        raw_labels = config.get(CONF_LABELS, "low, normal, high")
        if self._mode in (
            MODE_INSIDE_RANGE,
            MODE_OUTSIDE_RANGE,
            MODE_ABOVE_LIMIT,
            MODE_BELOW_LIMIT,
        ):
            required_labels = 2
        else:
            required_labels = len(self._raw_threshold_items) + 1
        self._labels: list[str] = parse_labels(raw_labels, required_labels)

        self._hysteresis: float = float(config.get(CONF_HYSTERESIS, DEFAULT_HYSTERESIS))
        self._hold_time: float = float(config.get(CONF_HOLD_TIME, DEFAULT_HOLD_TIME))
        self._gradient_threshold: float = float(
            config.get(CONF_GRADIENT_THRESHOLD, DEFAULT_GRADIENT_THRESHOLD)
        )
        self._attr_icon = config.get(CONF_ICON) or DEFAULT_ICON

        # Runtime states
        self._current_value: float | None = None
        self._resolved_thresholds: list[float] = []
        self._active_zone_index: int | None = None
        self._active_zone_label: str | None = None

        self._in_range: bool | None = None
        self._outside_range: bool | None = None
        self._is_above: bool | None = None
        self._is_below: bool | None = None

        # Debounce / Hold time tracking
        self._pending_state: str | None = None
        self._pending_since: datetime | None = None
        self._cancel_hold_timer: Any | None = None

        # Gradient / Trend tracking
        self._last_time: datetime | None = None
        self._last_value: float | None = None
        self._gradient: float = 0.0
        self._trend: str = "stable"
        self._gradient_alert: bool = False

        self._attr_native_value: str | None = None
        self._attr_available: bool = True

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            ATTR_SOURCE_ENTITY: self._source_entity,
            ATTR_CURRENT_VALUE: self._current_value,
            ATTR_MODE: self._mode,
            ATTR_THRESHOLDS: self._raw_threshold_items,
            ATTR_RESOLVED_THRESHOLDS: self._resolved_thresholds,
            ATTR_LABELS: self._labels,
            ATTR_ACTIVE_ZONE_INDEX: self._active_zone_index,
            ATTR_ACTIVE_ZONE_LABEL: self._active_zone_label,
            ATTR_IN_RANGE: self._in_range,
            ATTR_OUTSIDE_RANGE: self._outside_range,
            ATTR_IS_ABOVE: self._is_above,
            ATTR_IS_BELOW: self._is_below,
            ATTR_HYSTERESIS: self._hysteresis,
            ATTR_HOLD_TIME: self._hold_time,
            ATTR_PENDING_STATE: self._pending_state,
            ATTR_GRADIENT: self._gradient,
            ATTR_TREND: self._trend,
            ATTR_GRADIENT_THRESHOLD: self._gradient_threshold,
            ATTR_GRADIENT_ALERT: self._gradient_alert,
            ATTR_PRESET: self._preset,
        }

    async def async_added_to_hass(self) -> None:
        """Register state listeners when added to hass."""
        tracked_entities = [self._source_entity] + self._dynamic_threshold_entities
        valid_tracked = [e for e in tracked_entities if e]
        if valid_tracked:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass,
                    valid_tracked,
                    self._async_state_changed,
                )
            )
        self._evaluate_state()

    async def async_will_remove_from_hass(self) -> None:
        """Clean up background timers on removal."""
        self._stop_hold_timer()

    @callback
    def _async_state_changed(self, event: Event) -> None:
        """Handle state change of source entity or threshold entities."""
        self._evaluate_state()
        self.async_write_ha_state()

    def _stop_hold_timer(self) -> None:
        """Stop hold timer if active."""
        if self._cancel_hold_timer:
            self._cancel_hold_timer()
            self._cancel_hold_timer = None

    def _resolve_numeric_thresholds(self) -> list[float]:
        """Resolve static numbers and dynamic entity IDs into sorted floats."""
        resolved: list[float] = []
        for item in self._raw_threshold_items:
            if "." in item and not item.replace(".", "", 1).replace("-", "").isdigit():
                # Dynamic entity ID
                state = self.hass.states.get(item) if self.hass else None
                if state and state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                    try:
                        resolved.append(float(state.state))
                    except (ValueError, TypeError):
                        pass
            else:
                try:
                    resolved.append(float(item))
                except (ValueError, TypeError):
                    pass
        return sorted(resolved)

    def _compute_gradient(self, val: float, now: datetime) -> None:
        """Compute rate of change (units per minute) and trend."""
        if self._last_time is not None and self._last_value is not None:
            dt_sec = (now - self._last_time).total_seconds()
            if dt_sec >= 2.0:
                delta = val - self._last_value
                # rate of change per minute
                rate = (delta / dt_sec) * 60.0
                self._gradient = round(rate, 2)
                if self._gradient > 0.05:
                    self._trend = "rising"
                elif self._gradient < -0.05:
                    self._trend = "falling"
                else:
                    self._trend = "stable"

                if self._gradient_threshold > 0:
                    self._gradient_alert = abs(self._gradient) >= self._gradient_threshold
                self._last_time = now
                self._last_value = val
        else:
            self._last_time = now
            self._last_value = val
            self._gradient = 0.0
            self._trend = "stable"
            self._gradient_alert = False

    def _determine_target_state(
        self, val: float, thresholds: list[float]
    ) -> tuple[str, int | None]:
        """Determine target state string and zone index based on mode and hysteresis."""
        if not thresholds:
            return (self._labels[0] if self._labels else "unknown", 0)

        hyst = max(0.0, self._hysteresis)
        cur_val = self._attr_native_value

        # --- MODE 1: INSIDE_RANGE (Lower <= Value <= Upper) ---
        if self._mode == MODE_INSIDE_RANGE:
            lower = thresholds[0]
            upper = thresholds[-1] if len(thresholds) > 1 else thresholds[0]
            inside_label = self._labels[0] if len(self._labels) > 0 else "inside"
            outside_label = self._labels[1] if len(self._labels) > 1 else "outside"

            if hyst == 0.0 or cur_val is None:
                is_in = lower <= val <= upper
                return (inside_label if is_in else outside_label, 0 if is_in else 1)

            if cur_val == inside_label:
                # Stays inside until it breaks outside bounds + hysteresis
                if val < (lower - hyst) or val > (upper + hyst):
                    return (outside_label, 1)
                return (inside_label, 0)
            else:
                # Outside: must penetrate safely inside bounds + hysteresis
                if (lower + hyst) <= val <= (upper - hyst):
                    return (inside_label, 0)
                return (outside_label, 1)

        # --- MODE 2: OUTSIDE_RANGE (Value < Lower OR Value > Upper) ---
        if self._mode == MODE_OUTSIDE_RANGE:
            lower = thresholds[0]
            upper = thresholds[-1] if len(thresholds) > 1 else thresholds[0]
            outside_label = self._labels[0] if len(self._labels) > 0 else "outside"
            inside_label = self._labels[1] if len(self._labels) > 1 else "inside"

            if hyst == 0.0 or cur_val is None:
                is_out = val < lower or val > upper
                return (outside_label if is_out else inside_label, 0 if is_out else 1)

            if cur_val == outside_label:
                # Outside (e.g. alarm): only clears if it safely enters range
                if (lower + hyst) <= val <= (upper - hyst):
                    return (inside_label, 1)
                return (outside_label, 0)
            else:
                # Inside: triggers outside if it drops below or exceeds with hysteresis
                if val < (lower - hyst) or val > (upper + hyst):
                    return (outside_label, 0)
                return (inside_label, 1)

        # --- MODE 3: ABOVE_LIMIT (Value >= Limit) ---
        if self._mode == MODE_ABOVE_LIMIT:
            limit = thresholds[-1]
            above_label = self._labels[0] if len(self._labels) > 0 else "above"
            below_label = self._labels[1] if len(self._labels) > 1 else "below"

            if hyst == 0.0 or cur_val is None:
                is_ab = val >= limit
                return (above_label if is_ab else below_label, 0 if is_ab else 1)

            if cur_val == above_label:
                if val < (limit - hyst):
                    return (below_label, 1)
                return (above_label, 0)
            else:
                if val >= (limit + hyst):
                    return (above_label, 0)
                return (below_label, 1)

        # --- MODE 4: BELOW_LIMIT (Value < Limit) ---
        if self._mode == MODE_BELOW_LIMIT:
            limit = thresholds[0]
            below_label = self._labels[0] if len(self._labels) > 0 else "below"
            above_label = self._labels[1] if len(self._labels) > 1 else "above"

            if hyst == 0.0 or cur_val is None:
                is_bel = val < limit
                return (below_label if is_bel else above_label, 0 if is_bel else 1)

            if cur_val == below_label:
                if val > (limit + hyst):
                    return (above_label, 1)
                return (below_label, 0)
            else:
                if val <= (limit - hyst):
                    return (below_label, 0)
                return (above_label, 1)

        # --- MODE 5: MULTI_ZONE (Default / Multi-Tier) ---
        num_zones = len(thresholds) + 1
        current_zone = self._active_zone_index

        if hyst == 0.0 or current_zone is None:
            for idx, thresh in enumerate(thresholds):
                if val < thresh:
                    label = self._labels[idx] if idx < len(self._labels) else f"zone_{idx + 1}"
                    return (label, idx)
            last_idx = len(thresholds)
            label = self._labels[last_idx] if last_idx < len(self._labels) else f"zone_{last_idx + 1}"
            return (label, last_idx)

        new_zone = current_zone
        while new_zone < num_zones - 1 and val >= (thresholds[new_zone] + hyst):
            new_zone += 1

        while new_zone > 0 and val < (thresholds[new_zone - 1] - hyst):
            new_zone -= 1

        label = self._labels[new_zone] if new_zone < len(self._labels) else f"zone_{new_zone + 1}"
        return (label, new_zone)

    @callback
    def _apply_state(self, new_state: str, zone_idx: int | None) -> None:
        """Apply active state and zone attributes."""
        self._attr_native_value = new_state
        self._active_zone_index = zone_idx
        self._active_zone_label = new_state
        self._pending_state = None
        self._pending_since = None

    @callback
    def _hold_timer_finished(self, _now: Any) -> None:
        """Handle completion of the hold duration."""
        self._cancel_hold_timer = None
        if self._pending_state is not None:
            # Re-evaluate in case value changed during timer
            self._apply_state(self._pending_state, self._active_zone_index)
            self.async_write_ha_state()

    @callback
    def _evaluate_state(self) -> None:
        """Evaluate numeric value and assign active limit state."""
        source_state = self.hass.states.get(self._source_entity) if self.hass else None
        if source_state is None or source_state.state in (
            STATE_UNAVAILABLE,
            STATE_UNKNOWN,
        ):
            self._attr_available = False
            self._attr_native_value = None
            self._current_value = None
            self._stop_hold_timer()
            return

        try:
            val = float(source_state.state)
        except (ValueError, TypeError):
            self._attr_available = False
            self._attr_native_value = None
            self._current_value = None
            self._stop_hold_timer()
            return

        self._attr_available = True
        self._current_value = val

        # Resolve thresholds
        thresholds = self._resolve_numeric_thresholds()
        self._resolved_thresholds = thresholds

        now = dt_util.utcnow()
        self._compute_gradient(val, now)

        # Standard range attributes for convenience
        if thresholds:
            low_bound = thresholds[0]
            high_bound = thresholds[-1]
            self._in_range = low_bound <= val <= high_bound
            self._outside_range = not self._in_range
            self._is_above = val >= high_bound
            self._is_below = val < low_bound
        else:
            self._in_range = None
            self._outside_range = None
            self._is_above = None
            self._is_below = None

        candidate_state, zone_idx = self._determine_target_state(val, thresholds)

        # Debounce / Hold Time
        if self._hold_time > 0 and self._attr_native_value is not None:
            if candidate_state != self._attr_native_value:
                if self._pending_state == candidate_state:
                    # Timer already running for this candidate, do nothing
                    pass
                else:
                    # New target candidate: start or reset hold timer
                    self._stop_hold_timer()
                    self._pending_state = candidate_state
                    self._pending_since = now
                    self._active_zone_index = zone_idx
                    self._cancel_hold_timer = async_call_later(
                        self.hass,
                        self._hold_time,
                        self._hold_timer_finished,
                    )
            else:
                # Value returned to current active state before hold time elapsed
                if self._pending_state is not None:
                    self._stop_hold_timer()
                    self._pending_state = None
                    self._pending_since = None
        else:
            self._stop_hold_timer()
            self._apply_state(candidate_state, zone_idx)
