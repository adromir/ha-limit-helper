"""Constants for the Limit Helper integration."""
from __future__ import annotations

DOMAIN = "limit_helper"

CONF_SOURCE_ENTITY = "source_entity"
CONF_MODE = "mode"
CONF_PRESET = "preset"
CONF_THRESHOLDS = "thresholds"
CONF_LABELS = "labels"
CONF_HYSTERESIS = "hysteresis"
CONF_HOLD_TIME = "hold_time"
CONF_GRADIENT_THRESHOLD = "gradient_threshold"
CONF_ICON = "icon"

DEFAULT_NAME = "Limit Helper"
DEFAULT_PRESET = "custom"
DEFAULT_HYSTERESIS = 0.0
DEFAULT_HOLD_TIME = 0.0
DEFAULT_GRADIENT_THRESHOLD = 0.0
DEFAULT_ICON = "mdi:gauge"

MODE_MULTI_ZONE = "multi_zone"
MODE_INSIDE_RANGE = "inside_range"
MODE_OUTSIDE_RANGE = "outside_range"
MODE_ABOVE_LIMIT = "above_limit"
MODE_BELOW_LIMIT = "below_limit"

MODE_OPTIONS = [
    MODE_MULTI_ZONE,
    MODE_INSIDE_RANGE,
    MODE_OUTSIDE_RANGE,
    MODE_ABOVE_LIMIT,
    MODE_BELOW_LIMIT,
]
DEFAULT_MODE = MODE_MULTI_ZONE

PRESET_CUSTOM = "custom"
PRESET_INSIDE_RANGE = "inside_range"
PRESET_OUTSIDE_RANGE = "outside_range"
PRESET_ABOVE_LIMIT = "above_limit"
PRESET_BELOW_LIMIT = "below_limit"
PRESET_BATTERY = "battery"
PRESET_COMFORT_TEMP = "comfort_temp"
PRESET_HUMIDITY = "humidity"
PRESET_AIR_QUALITY = "air_quality"
PRESET_POWER_STANDBY = "power_standby"

PRESET_OPTIONS = [
    PRESET_CUSTOM,
    PRESET_INSIDE_RANGE,
    PRESET_OUTSIDE_RANGE,
    PRESET_ABOVE_LIMIT,
    PRESET_BELOW_LIMIT,
    PRESET_BATTERY,
    PRESET_COMFORT_TEMP,
    PRESET_HUMIDITY,
    PRESET_AIR_QUALITY,
    PRESET_POWER_STANDBY,
]

PRESET_DEFAULTS = {
    PRESET_INSIDE_RANGE: {
        "mode": MODE_INSIDE_RANGE,
        "thresholds": "18, 24",
        "labels": "inside, outside",
    },
    PRESET_OUTSIDE_RANGE: {
        "mode": MODE_OUTSIDE_RANGE,
        "thresholds": "18, 24",
        "labels": "outside, inside",
    },
    PRESET_ABOVE_LIMIT: {
        "mode": MODE_ABOVE_LIMIT,
        "thresholds": "25",
        "labels": "above, below",
    },
    PRESET_BELOW_LIMIT: {
        "mode": MODE_BELOW_LIMIT,
        "thresholds": "15",
        "labels": "below, above",
    },
    PRESET_BATTERY: {
        "mode": MODE_MULTI_ZONE,
        "thresholds": "20, 40, 70",
        "labels": "critical, low, medium, good",
    },
    PRESET_COMFORT_TEMP: {
        "mode": MODE_MULTI_ZONE,
        "thresholds": "18, 24",
        "labels": "cold, comfortable, hot",
    },
    PRESET_HUMIDITY: {
        "mode": MODE_MULTI_ZONE,
        "thresholds": "30, 60",
        "labels": "dry, optimal, humid",
    },
    PRESET_AIR_QUALITY: {
        "mode": MODE_MULTI_ZONE,
        "thresholds": "800, 1200, 1800",
        "labels": "good, moderate, poor, critical",
    },
    PRESET_POWER_STANDBY: {
        "mode": MODE_MULTI_ZONE,
        "thresholds": "5, 200",
        "labels": "standby, idle, active",
    },
}

ATTR_SOURCE_ENTITY = "source_entity"
ATTR_CURRENT_VALUE = "current_value"
ATTR_MODE = "mode"
ATTR_ACTIVE_ZONE_INDEX = "active_zone_index"
ATTR_ACTIVE_ZONE_LABEL = "active_zone_label"
ATTR_THRESHOLDS = "thresholds"
ATTR_RESOLVED_THRESHOLDS = "resolved_thresholds"
ATTR_LABELS = "labels"
ATTR_HYSTERESIS = "hysteresis"
ATTR_IN_RANGE = "in_range"
ATTR_OUTSIDE_RANGE = "outside_range"
ATTR_IS_ABOVE = "is_above"
ATTR_IS_BELOW = "is_below"
ATTR_HOLD_TIME = "hold_time"
ATTR_PENDING_STATE = "pending_state"
ATTR_GRADIENT = "gradient"
ATTR_TREND = "trend"
ATTR_GRADIENT_ALERT = "gradient_alert"
ATTR_GRADIENT_THRESHOLD = "gradient_threshold"
ATTR_PRESET = "preset"
