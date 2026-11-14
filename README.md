# 🎚️ Limit Helper for Home Assistant

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=adromir&repository=ha-limit-helper&category=integration)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/adromir)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/default)
[![GitHub Release](https://img.shields.io/github/v/release/adromir/ha-limit-helper?style=for-the-badge&color=blue)](https://github.com/adromir/ha-limit-helper/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=for-the-badge)](https://github.com/adromir/ha-limit-helper)

A lightweight, powerful, and native **Home Assistant Helper Integration** that categorizes any continuous numeric sensor into qualitative limit zones, evaluates single or double boundaries (**Inside Range** vs. **Outside Range / Inverted**), supports **dynamic entity thresholds**, **hold-time debouncing**, and **hysteresis deadband buffers**.

Completely eliminates complex multi-branch Jinja2 YAML template sensors and solves the fundamental shortcomings of Home Assistant's built-in Threshold helper!

---

## 🎯 Why Limit Helper is Far Superior to Native Threshold Sensors

| Feature | Home Assistant Native `threshold` Sensor | 🎚️ Limit Helper (`limit_helper`) |
| :--- | :--- | :--- |
| **Entity Platform** | Binary sensor only (`on` / `off`) | **Full state sensor (`sensor.*`)** with expressive custom labels |
| **Zone Classification** | Only 1 boundary (above or below) | **Arbitrary N zones** (e.g. `critical`, `low`, `normal`, `high`, `alert`) |
| **Two-Boundary Behavior** | Only `Inside Range` (`lower <= val <= upper`) | **Both Inside Range AND Outside Range (Inverted!)** |
| **Threshold Types** | Hardcoded static floats only | **Dynamic Entity IDs** (e.g. `input_number.target_limit`, `sensor.power_peak`) |
| **Spike Filter / Debounce** | ❌ None (flaps on instant noise) | **Hold Time / Debounce (`for: X seconds`)** |
| **Trend & Gradient** | ❌ None | **Live Gradient (rate of change/min), Trend (`rising`, `falling`), and Surge Alerts** |
| **Hysteresis Explanation** | ❌ None in UI | **Built-in UI explanations, diagrams, and examples** |

---

## 🔬 What is Hysteresis and Why Do You Need It?

Home Assistant's native helper does not explain what hysteresis actually does. Here is the straightforward explanation:

### The Problem Without Hysteresis (Chattering / Flapping):
When a sensor reading fluctuates slightly around a boundary (due to electrical noise or gentle air movement), the helper repeatedly flips ON and OFF every few seconds:
```text
Threshold = 20.0°C (No Hysteresis)
Sensor: 19.99°C ➔ OFF
Sensor: 20.01°C ➔ ON
Sensor: 19.99°C ➔ OFF
Sensor: 20.01°C ➔ ON   <-- Relays click repeatedly, notifications spam!
```

### The Solution With Hysteresis:
Hysteresis adds a **symmetric buffer zone** around the threshold:
```text
Threshold = 20.0°C | Hysteresis = 0.5°C

Rising Phase:  Must exceed 20.5°C (20.0 + 0.5) to switch ON
Falling Phase: Must drop below 19.5°C (20.0 - 0.5) to switch OFF

                     ▲ Value Rising
                     │
         [20.5°C] ───┼────────── SWITCHES TO ACTIVE / ON
                     │ (Buffer Zone: Ignores fluctuations)
   Threshold [20.0°C]│
                     │ (Buffer Zone: Ignores fluctuations)
         [19.5°C] ───┼────────── SWITCHES TO INACTIVE / OFF
                     │
                     ▼ Value Falling
```
**Result**: Clean, stable state switching without relay chattering or notification floods.

---

## ⚡ 5 Flexible Operating Modes

1. **Multi-Tier Zones (`multi_zone`)**:
   - Split a sensor into arbitrary bands (e.g. `20, 40, 70` ➔ `critical, low, medium, good`).
2. **Inside Range (`inside_range`)**:
   - Active (`inside`) when value is between lower and upper bound (`lower <= val <= upper`).
3. **Outside Range / Inverted (`outside_range`)**:
   - **The exact inverse of native threshold**: Active (`outside` / `alert`) when value drops below Min OR exceeds Max (`val < lower` OR `val > upper`). Perfect for fridge temperature alarms, greenhouse humidity, and power fault alerts!
4. **Above Limit (`above_limit`)**:
   - Active when value is greater than or equal to threshold (`val >= threshold`).
5. **Below Limit (`below_limit`)**:
   - Active when value is less than threshold (`val < threshold`).

---

## 🔄 Dynamic Thresholds via Entities

Instead of hardcoding fixed numbers, you can provide Home Assistant entity IDs directly in the `thresholds` field:
```text
input_number.heizung_min_soll, 22.0, input_number.heizung_max_soll
```
The helper listens to state change events of these entities in real-time and dynamically recalculates boundaries without any reload or restart!

---

## ⏱️ Hold Time / Debounce Filter (`hold_time`)

Define an optional dwell time in seconds (e.g. `30` seconds). When a sensor crosses a boundary, the helper waits until the reading remains continuously in the candidate zone for 30 seconds before changing the active state. Momentary spikes (e.g., microwave turning on or opening the fridge for 5 seconds) are safely ignored.

---

## 📈 Rate of Change (Gradient) & Trend Detection

Every Limit Helper automatically monitors:
- `gradient`: Rate of change in units per minute (e.g., `+1.8 °C/min`).
- `trend`: Direction (`rising`, `falling`, `stable`).
- `gradient_alert`: Boolean flag triggered when the rate of change exceeds your optional `gradient_threshold` (early warning before reaching critical limits).

---

## 📦 Installation

### Method 1: HACS (Recommended)

1. Click the button below to add this repository directly to HACS:

   [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=adromir&repository=ha-limit-helper&category=integration)

2. Or manually in HACS:
   - Go to **HACS** > **Integrations** > **Three dots menu (top right)** > **Custom repositories**.
   - URL: `https://github.com/adromir/ha-limit-helper`
   - Type: `Integration`
   - Click **Add**, find **Limit Helper** and click **Download**.
3. **Restart Home Assistant**.

### Method 2: Manual Installation
1. Copy the `custom_components/limit_helper` directory into your Home Assistant `<config>/custom_components/` folder.
2. Restart Home Assistant.

---

## 🚀 How to Use

1. In Home Assistant, navigate to **Settings** > **Devices & Services** > **Helpers**.
2. Click **Create Helper** (bottom right) and select **Limit Helper**.
3. Select your **Target Entity**, choose a **Preset** or **Mode**, set your **Thresholds** (numbers or entity IDs), and enter an optional **Hysteresis** and **Hold Time**.
4. Click **Submit**. Your new sensor entity (`sensor.mein_grenzwert`) is immediately ready for dashboards and automations!

---

## 📄 Disclaimer

This is a custom community integration and is not officially affiliated with or endorsed by Nabu Casa or Home Assistant.

---

## 📜 License

MIT License © 2026 Adromir (<https://github.com/adromir>)
