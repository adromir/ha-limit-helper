"""Sensor platform for Limit Helper."""
from __future__ import annotations

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
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    ATTR_ACTIVE_ZONE_INDEX,
    ATTR_CURRENT_VALUE,
    ATTR_HYSTERESIS,
    ATTR_LABELS,
    ATTR_PRESET,
    ATTR_SOURCE_ENTITY,
    ATTR_THRESHOLDS,
    CONF_HYSTERESIS,
    CONF_ICON,
    CONF_LABELS,
    CONF_PRESET,
    CONF_SOURCE_ENTITY,
    CONF_THRESHOLDS,
    DEFAULT_HYSTERESIS,
    DEFAULT_ICON,
    DEFAULT_NAME,
    DEFAULT_PRESET,
)

_LOGGER = logging.getLogger(__name__)


def parse_thresholds(thresh_str: str) -> list[float]:
    """Parse comma-separated thresholds string into sorted list of floats."""
    parts = [p.strip() for p in thresh_str.split(",") if p.strip()]
    return sorted([float(p) for p in parts])


def parse_labels(labels_str: str, required_count: int) -> list[str]:
    """Parse comma-separated labels string, padding if necessary."""
    parts = [l.strip() for l in labels_str.split(",") if l.strip()]
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
    """Representation of a Limit Helper Sensor."""

    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_translation_key = "limit_helper"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        self._entry = entry
        config = {**entry.data, **entry.options}

        custom_name = config.get(CONF_NAME)
        if custom_name and custom_name not in (DEFAULT_NAME, "Limit Helper", "Grenzwert-Helfer", "Pembantu Batas"):
            self._attr_name = custom_name
        else:
            self._attr_name = None
        self._attr_unique_id = f"{entry.entry_id}_limit"

        self._source_entity: str = config.get(CONF_SOURCE_ENTITY, "")
        self._preset: str = config.get(CONF_PRESET, DEFAULT_PRESET)

        thresh_str = config.get(CONF_THRESHOLDS, "20, 80")
        try:
            self._thresholds: list[float] = parse_thresholds(thresh_str)
        except ValueError:
            self._thresholds = [20.0, 80.0]

        labels_str = config.get(CONF_LABELS, "low, normal, high")
        required_labels = len(self._thresholds) + 1
        self._labels: list[str] = parse_labels(labels_str, required_labels)

        self._hysteresis: float = float(config.get(CONF_HYSTERESIS, DEFAULT_HYSTERESIS))
        self._attr_icon = config.get(CONF_ICON) or DEFAULT_ICON

        self._current_value: float | None = None
        self._active_zone_index: int | None = None

        self._attr_native_value: str | None = None
        self._attr_available: bool = True

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            ATTR_SOURCE_ENTITY: self._source_entity,
            ATTR_CURRENT_VALUE: self._current_value,
            ATTR_ACTIVE_ZONE_INDEX: self._active_zone_index,
            ATTR_THRESHOLDS: self._thresholds,
            ATTR_LABELS: self._labels,
            ATTR_HYSTERESIS: self._hysteresis,
            ATTR_PRESET: self._preset,
        }

    async def async_added_to_hass(self) -> None:
        """Register state listener when added to hass."""
        if self._source_entity:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass,
                    [self._source_entity],
                    self._async_source_state_changed,
                )
            )
        self._evaluate_state()

    @callback
    def _async_source_state_changed(self, event: Event) -> None:
        """Handle state change of source entity."""
        self._evaluate_state()
        self.async_write_ha_state()

    def _determine_zone(self, value: float) -> int:
        """Determine zone index from numeric value with optional hysteresis."""
        if not self._thresholds:
            return 0

        num_zones = len(self._thresholds) + 1
        current_zone = self._active_zone_index
        hyst = max(0.0, self._hysteresis)

        # Standard zone calculation without hysteresis or on initial eval
        if hyst == 0.0 or current_zone is None:
            for idx, thresh in enumerate(self._thresholds):
                if value < thresh:
                    return idx
            return len(self._thresholds)

        # Hysteresis: check if moving up
        new_zone = current_zone
        while new_zone < num_zones - 1 and value >= (self._thresholds[new_zone] + hyst):
            new_zone += 1

        # Check if moving down
        while new_zone > 0 and value < (self._thresholds[new_zone - 1] - hyst):
            new_zone -= 1

        return new_zone

    @callback
    def _evaluate_state(self) -> None:
        """Evaluate numeric value and assign active limit zone."""
        source_state = self.hass.states.get(self._source_entity)
        if source_state is None or source_state.state in (
            STATE_UNAVAILABLE,
            STATE_UNKNOWN,
        ):
            self._attr_available = False
            self._attr_native_value = None
            self._current_value = None
            return

        try:
            val = float(source_state.state)
        except (ValueError, TypeError):
            self._attr_available = False
            self._attr_native_value = None
            self._current_value = None
            return

        self._attr_available = True
        self._current_value = val

        zone_idx = self._determine_zone(val)
        self._active_zone_index = zone_idx

        if 0 <= zone_idx < len(self._labels):
            self._attr_native_value = self._labels[zone_idx]
        else:
            self._attr_native_value = f"zone_{zone_idx + 1}"

