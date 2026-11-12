"""Config flow for Limit Helper integration."""
from __future__ import annotations

import logging
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_SOURCE_ENTITY,
    CONF_PRESET,
    CONF_THRESHOLDS,
    CONF_LABELS,
    CONF_HYSTERESIS,
    CONF_ICON,
    DEFAULT_NAME,
    DEFAULT_PRESET,
    DEFAULT_HYSTERESIS,
    DEFAULT_ICON,
    PRESET_CUSTOM,
    PRESET_DEFAULTS,
    PRESET_OPTIONS,
)

_LOGGER = logging.getLogger(__name__)


def parse_thresholds(thresh_str: str) -> list[float]:
    """Parse comma-separated thresholds string into sorted list of floats."""
    parts = [p.strip() for p in thresh_str.split(",") if p.strip()]
    return sorted([float(p) for p in parts])


def parse_labels(labels_str: str) -> list[str]:
    """Parse comma-separated labels string."""
    return [l.strip() for l in labels_str.split(",") if l.strip()]


def _validate_input(user_input: dict[str, Any]) -> dict[str, str]:
    """Validate user input fields."""
    errors: dict[str, str] = {}
    name = user_input.get(CONF_NAME, "").strip() if CONF_NAME in user_input else "valid"
    source_entity = user_input.get(CONF_SOURCE_ENTITY)
    preset = user_input.get(CONF_PRESET, DEFAULT_PRESET)

    if not name:
        errors[CONF_NAME] = "empty_name"
    if not source_entity:
        errors[CONF_SOURCE_ENTITY] = "empty_source"

    thresh_str = user_input.get(CONF_THRESHOLDS, "").strip()
    labels_str = user_input.get(CONF_LABELS, "").strip()

    if preset != PRESET_CUSTOM and preset in PRESET_DEFAULTS:
        if not thresh_str:
            thresh_str = PRESET_DEFAULTS[preset]["thresholds"]
            user_input[CONF_THRESHOLDS] = thresh_str
        if not labels_str:
            labels_str = PRESET_DEFAULTS[preset]["labels"]
            user_input[CONF_LABELS] = labels_str

    if not thresh_str:
        errors[CONF_THRESHOLDS] = "empty_thresholds"
    else:
        try:
            thresh_list = parse_thresholds(thresh_str)
            if not thresh_list:
                errors[CONF_THRESHOLDS] = "empty_thresholds"
        except ValueError:
            errors[CONF_THRESHOLDS] = "invalid_thresholds"

    if not labels_str:
        errors[CONF_LABELS] = "empty_labels"

    return errors


class LimitHelperConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Limit Helper."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = _validate_input(user_input)
            if not errors:
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, DEFAULT_NAME),
                    data=user_input,
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                ),
                vol.Required(CONF_SOURCE_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor", "input_number"])
                ),
                vol.Required(
                    CONF_PRESET, default=DEFAULT_PRESET
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[{"value": p, "label": p} for p in PRESET_OPTIONS],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        translation_key="preset",
                    )
                ),
                vol.Optional(
                    CONF_THRESHOLDS, default="20, 80"
                ): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                ),
                vol.Optional(
                    CONF_LABELS, default="low, normal, high"
                ): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                ),
                vol.Optional(
                    CONF_HYSTERESIS, default=DEFAULT_HYSTERESIS
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0.0,
                        mode=selector.NumberSelectorMode.BOX,
                        step="any",
                    )
                ),
                vol.Optional(
                    CONF_ICON,
                    description={"suggested_value": DEFAULT_ICON},
                ): selector.IconSelector(),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> LimitHelperOptionsFlow:
        """Get the options flow for this handler."""
        return LimitHelperOptionsFlow(config_entry)


class LimitHelperOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Limit Helper."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}
        current_data = {**self.config_entry.data, **self.config_entry.options}

        if user_input is not None:
            errors = _validate_input(user_input)
            if not errors:
                return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SOURCE_ENTITY,
                    default=current_data.get(CONF_SOURCE_ENTITY, ""),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor", "input_number"])
                ),
                vol.Required(
                    CONF_PRESET,
                    default=current_data.get(CONF_PRESET, DEFAULT_PRESET),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[{"value": p, "label": p} for p in PRESET_OPTIONS],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        translation_key="preset",
                    )
                ),
                vol.Required(
                    CONF_THRESHOLDS,
                    default=current_data.get(CONF_THRESHOLDS, "20, 80"),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                ),
                vol.Required(
                    CONF_LABELS,
                    default=current_data.get(CONF_LABELS, "low, normal, high"),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                ),
                vol.Optional(
                    CONF_HYSTERESIS,
                    default=current_data.get(CONF_HYSTERESIS, DEFAULT_HYSTERESIS),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0.0,
                        mode=selector.NumberSelectorMode.BOX,
                        step="any",
                    )
                ),
                vol.Optional(
                    CONF_ICON,
                    description={"suggested_value": current_data.get(CONF_ICON, DEFAULT_ICON)},
                ): selector.IconSelector(),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
        )
