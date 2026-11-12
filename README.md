# 🎚️ Limit Helper for Home Assistant

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=adromir&repository=ha-limit-helper&category=integration)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/default)
[![GitHub Release](https://img.shields.io/github/v/release/adromir/ha-limit-helper?style=for-the-badge&color=blue)](https://github.com/adromir/ha-limit-helper/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=for-the-badge)](https://github.com/adromir/ha-limit-helper)

A lightweight, native **Home Assistant Helper Integration** that categorizes any continuous numeric sensor (battery %, temperature, power W, CO2 ppm, humidity %, illuminance lx) into multi-tier qualitative limit zones (`low`, `normal`, `high`, `critical`) with optional hysteresis deadband.

Completely eliminates complex multi-branch Jinja2 YAML template sensors!

---

## 🎯 The Problem This Solves

Classifying numeric sensors into human-readable states or status tiers is one of the most common smart home needs:
- **Battery**: `< 20%` ➔ `critical`, `< 40%` ➔ `low`, `< 70%` ➔ `medium`, `>= 70%` ➔ `good`
- **Temperature**: `< 18°C` ➔ `cold`, `18°C - 24°C` ➔ `comfortable`, `> 24°C` ➔ `hot`
- **Air Quality (CO2)**: `< 800` ➔ `good`, `< 1200` ➔ `moderate`, `< 1800` ➔ `poor`, `>= 1800` ➔ `critical`
- **Power Usage**: `< 5 W` ➔ `standby`, `< 200 W` ➔ `idle`, `>= 200 W` ➔ `active`

Until now, creating this in Home Assistant required writing tedious Jinja2 template sensors in YAML:
```yaml
# ❌ Cumbersome YAML template sensor (requires manual editing and HA restarts):
template:
  - sensor:
      - name: "Batteriestatus"
        state: >
          {% set val = states('sensor.main_battery') | float(0) %}
          {% if val < 20 %}critical
          {% elif val < 40 %}low
          {% elif val < 70 %}medium
          {% else %}good{% endif %}
```

With the **Limit Helper**, you set this up in seconds directly in the Home Assistant UI and get a clean, reactive `sensor` entity that updates automatically!

---

## ✨ Key Features & Advantages

- 🎛️ **Native Helper Integration (`integration_type: helper`)**: Appears directly in Home Assistant under **Settings > Devices & Services > Helpers > Create Helper > Limit Helper**.
- 📋 **Built-in Presets for Instant Setup**:
  - 🔋 **Battery Status**: `Critical` (<20) / `Low` (<40) / `Medium` (<70) / `Good` (>=70)
  - 🌡️ **Comfort Temperature**: `Cold` (<18°C) / `Comfortable` (18-24°C) / `Hot` (>=24°C)
  - 💧 **Humidity Comfort**: `Dry` (<30%) / `Optimal` (30-60%) / `Humid` (>=60%)
  - 🌬️ **Air Quality (CO2)**: `Good` (<800 ppm) / `Moderate` / `Poor` / `Critical`
  - ⚡ **Power Consumption**: `Standby` (<5 W) / `Idle` / `Active`
  - 🛠️ **Custom**: Define arbitrary thresholds and zone labels.
- 🛡️ **Hysteresis Noise Buffer**: Prevents rapid bouncing between adjacent zones when a sensor measurement hovers right on a boundary.
- 🏷️ **Rich State Attributes**: Exposes `source_entity`, `current_value`, `active_zone_index`, `thresholds`, `labels`, and `hysteresis` right in developer tools.
- ⚙️ **100% UI Config Flow & Options Flow**: Modify thresholds, zone names, or hysteresis live without restarting Home Assistant.
- 🌐 **Bilingual Support**: Fully localized in English and German.

---

## 📦 Installation

### Method 1: HACS (Recommended)

1. Click the button below to add this repository directly to HACS:

   [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=adromir&repository=ha-limit-helper&category=integration)

2. Or manually in HACS:
   - Go to **HACS** > **Integrations** > **Three dots menu (top right)** > **Custom repositories**.
   - URL: `https://github.com/adromir/ha-limit-helper`
   - Type: `Integration`
   - Click **Add**, then find **Limit Helper** and click **Download**.
3. **Restart Home Assistant**.

### Method 2: Manual Installation
1. Copy the `custom_components/limit_helper` directory into your Home Assistant `<config>/custom_components/` folder.
2. Restart Home Assistant.

---

## 🚀 How to Use

1. In Home Assistant, navigate to **Settings** > **Devices & Services** > **Helpers**.
2. Click **Create Helper** (bottom right) and select **Limit Helper**.
3. Configure your helper:
   - **Name**: e.g., `Batteriestatus` or `Luftqualität Wohnzimmer`
   - **Target Entity**: e.g., `sensor.smartphone_battery_level`
   - **Preset**: Choose a preset (e.g. `Battery Status`) or `Custom`.
   - **Thresholds**: e.g., `20, 40, 70`
   - **Zone Labels**: e.g., `critical, low, medium, good`
   - **Hysteresis**: e.g., `1.0` (optional deadband buffer)
4. Click **Submit**. Your new sensor entity (`sensor.batteriestatus`) is immediately available for your dashboard cards, automations, and notifications!

---

## 📄 Disclaimer

This is a custom community integration and is not officially affiliated with or endorsed by Nabu Casa or Home Assistant.

---

## 📜 License

This project is open-source under the [MIT License](LICENSE).

**Author**: [Adromir](https://github.com/adromir)  
Website: [https://github.com/adromir](https://github.com/adromir)
