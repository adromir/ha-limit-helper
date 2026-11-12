"""Constants for the Limit Helper integration."""
from __future__ import annotations

DOMAIN = "limit_helper"

CONF_SOURCE_ENTITY = "source_entity"
CONF_PRESET = "preset"
CONF_THRESHOLDS = "thresholds"
CONF_LABELS = "labels"
CONF_HYSTERESIS = "hysteresis"
CONF_ICON = "icon"

DEFAULT_NAME = "Limit Helper"
DEFAULT_PRESET = "custom"
DEFAULT_HYSTERESIS = 0.0
DEFAULT_ICON = "mdi:gauge"

PRESET_CUSTOM = "custom"
PRESET_BATTERY = "battery"
PRESET_COMFORT_TEMP = "comfort_temp"
PRESET_HUMIDITY = "humidity"
PRESET_AIR_QUALITY = "air_quality"
PRESET_POWER_STANDBY = "power_standby"

PRESET_OPTIONS = [
    PRESET_CUSTOM,
    PRESET_BATTERY,
    PRESET_COMFORT_TEMP,
    PRESET_HUMIDITY,
    PRESET_AIR_QUALITY,
    PRESET_POWER_STANDBY,
]

PRESET_DEFAULTS = {
    PRESET_BATTERY: {
        "thresholds": "20, 40, 70",
        "labels": "critical, low, medium, good",
    },
    PRESET_COMFORT_TEMP: {
        "thresholds": "18, 24",
        "labels": "cold, comfortable, hot",
    },
    PRESET_HUMIDITY: {
        "thresholds": "30, 60",
        "labels": "dry, optimal, humid",
    },
    PRESET_AIR_QUALITY: {
        "thresholds": "800, 1200, 1800",
        "labels": "good, moderate, poor, critical",
    },
    PRESET_POWER_STANDBY: {
        "thresholds": "5, 200",
        "labels": "standby, idle, active",
    },
}

ATTR_SOURCE_ENTITY = "source_entity"
ATTR_CURRENT_VALUE = "current_value"
ATTR_ACTIVE_ZONE_INDEX = "active_zone_index"
ATTR_THRESHOLDS = "thresholds"
ATTR_LABELS = "labels"
ATTR_HYSTERESIS = "hysteresis"
ATTR_PRESET = "preset"

