# 🌿 Smart Greenhouse IoT — Intelligent Climate Control for the Future of Agriculture

> **AI-powered, MQTT-driven precision farming** — real-time environmental monitoring, automated actuator control, and a live data-visualization dashboard for next-generation indoor agriculture.

---

## Table of Contents

1. [Project Vision](#project-vision)
2. [Architecture Overview](#architecture-overview)
3. [Key Features](#key-features)
4. [Technology Stack](#technology-stack)
5. [Project Structure](#project-structure)
6. [Prerequisites](#prerequisites)
7. [Installation](#installation)
8. [Quick Start — Dashboard Mode](#quick-start--dashboard-mode)
9. [Full IoT Mode — MQTT Broker](#full-iot-mode--mqtt-broker)
10. [How It Works](#how-it-works)
11. [Control Logic & Thresholds](#control-logic--thresholds)
12. [MQTT Topic Reference](#mqtt-topic-reference)
13. [Data Files](#data-files)
14. [Configuration](#configuration)
15. [Dashboard Navigation](#dashboard-navigation)
16. [Troubleshooting](#troubleshooting)
17. [Future Enhancements](#future-enhancements)
18. [License](#license)

---

## Project Vision

Modern agriculture is transitioning to **data-driven precision farming**. This Smart Greenhouse system creates a closed-loop IoT ecosystem where:

- **Sensors** continuously measure the growing environment
- **AI-style logic controllers** make split-second actuator decisions with hysteresis to prevent oscillation
- **Automated actuators** (cooling fans, fogging systems, nutrient dosers, pH regulators) maintain optimal growing conditions
- **Operators** monitor everything through a beautiful, real-time web dashboard with predictive trend visualization

The system is designed for **scalability** — start with the built-in simulator dashboard, then plug in real MQTT sensors and actuators as your greenhouse grows.

---

## Architecture Overview

```
                    ┌─────────────────────────────────────────────────┐
                    │              SMART GREENHOUSE                    │
                    │              IoT ECOSYSTEM                        │
                    └────────────────────────┬────────────────────────┘
                                             │
            ┌────────────────────────────────┼─────────────────────────────────┐
            │                              │                                   │
            ▼                              ▼                                   ▼
    ┌──────────────┐           ┌──────────────────┐           ┌──────────────────┐
    │   Sensor     │           │   Controller     │           │    Dashboard     │
    │  Simulator   │           │  (Actuator Logic)│           │   (Web UI)       │
    │ publisher.py │           │  controller.py   │           │  dashboard.py    │
    └──────┬───────┘           └────────┬────────┘           └────────┬────────┘
           │                            │                               │
           │  Publishes readings        │  Subscribes to sensor topics  │
           │  (greenhouse/temp, rh,      │  Publishes actuator states    │
           │   ec, ph)                   │  (greenhouse/fan_status, ...) │
           │                            │                               │
           ▼                            ▼                               ▼
    ┌──────────────────────────────────────────────────────────────────────────┐
    │                        MQTT MESSAGE BROKER                               │
    │                  (e.g., Mosquitto on localhost:1883)                       │
    │                                                                          │
    │   Topic Hierarchy:  greenhouse/{sensor|actuator|...}                   │
    └────────────────────────────────┬──────────────────────────────────────────┘
                                     │
                ┌────────────────────┼────────────────────┐
                ▼                    ▼                    ▼
         ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
         │  Real or    │      │  Actuator   │      │    Data     │
         │  Virtual    │      │   Hardware  │      │  Persistence│
         │  Sensors    │      │   (Fans,    │      │(JSON state) │
         └─────────────┘      │ Foggers,    │      └─────────────┘
                              │ Nutrients,  │
                              │ pH Systems) │
                              └─────────────┘
```

---

## Key Features

### Real-Time Monitoring
- **5-second auto-refresh** web dashboard with live telemetry
- Live gauge metrics for **temperature, humidity, EC, and pH** with delta change indicators
- Multi-axis **Plotly charts** with unified hover tooltips for trend analysis

### Intelligent Control
- **Hysteresis-based actuator control** prevents relay chatter and oscillation
- 5 distinct alert thresholds with **edge detection** (alerts fire only on state transitions, not continuously)
- Actuator feedback is modeled in the simulation loop — actuators influence sensor readings realistically

### Simulation Engine
- **Sinusoidal environmental cycles** mimic day/night temperature and humidity patterns
- **Stress periods** periodically push sensors beyond thresholds to demonstrate alert behavior
- **Random sensor drift** and disturbances create realistic, non-artificial data patterns
- Each sensor drifts independently with clamping to physically realistic ranges

### Alert System
- **Edge-triggered alerts**: fires only when a threshold boundary is crossed (not while continuously exceeded)
- Alert queue (max 10) with timestamps, severity levels (warning vs. critical)
- Critical alerts highlighted with distinct icons

### Visual Design
- **Dark-themed sidebar** with branded navigation
- **Hero image** (`greenhouse_bg.jpg`) as a full-width banner with gradient overlay
- Color-coded metric cards with themed icons
- Responsive layout with custom CSS styling

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.8+ |
| **Web Framework** | Streamlit |
| **Charting** | Plotly (graph objects) |
| **Data Handling** | Pandas |
| **Auto-Refresh** | streamlit-autorefresh |
| **IoT Protocol** | MQTT v5 (via Paho) |
| **Message Broker** | Mosquitto (localhost:1883) |
| **Simulation** | Custom Python (math + random) |
| **Persistence** | JSON files |

---

## Project Structure

```text
smart_greenhouse_project/
│
├── dashboard.py              # Streamlit web dashboard with in-memory simulation
├── publisher.py              # MQTT sensor data publisher (simulator → broker)
├── controller.py             # MQTT actuator controller (broker → actuators)
├── dataSimulation.py         # Sensor simulation engine (shared logic)
├── greenhouse_bg.jpg         # Hero background image for the dashboard
│
├── data/                     # Persistent data store
│   ├── sensor_data.json      # Latest sensor readings (temp, rh, ec, ph)
│   ├── control_state.json    # Current actuator states (fan, fogger, nutrient, acid)
│   └── history.json          # Historical data log (array, initially empty)
│
├── README.md                 # This file
└── __pycache__/              # Python bytecode cache (auto-generated)
```

### Component Responsibilities

| File | Role | Type |
|------|------|------|
| `dashboard.py` | Full web UI with built-in simulator and controller | Standalone (Streamlit) |
| `publisher.py` | Simulates sensors and publishes to MQTT | Edge device / broker client |
| `controller.py` | Subscribes to MQTT and controls actuators | Edge device / broker client |
| `dataSimulation.py` | Pure simulation logic — reusable by publisher | Shared library |

---

## Prerequisites

### For Dashboard Mode Only
- Python 3.8+
- pip (or pip3)

### For Full IoT Mode
- All Dashboard Mode prerequisites
- A running **MQTT broker** (Mosquitto recommended) on `localhost:1883`

#### Installing Mosquitto Broker

<details>
<summary>Windows (using Chocolatey)</summary>

```bash
choco install mosquitto
net start mosquitto
```
</details>

<details>
<summary>macOS (using Homebrew)</summary>

```bash
brew install mosquitto
brew services start mosquitto
```
</details>

<details>
<summary>Ubuntu/Debian</summary>

```bash
sudo apt update && sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```
</details>

<details>
<summary>Docker (cross-platform)</summary>

```bash
docker run -d --name mosquitto-broker \
  -p 1883:1883 -p 9001:9001 \
  eclipse-mosquitto:latest
```
</details>

---

## Installation

```bash
# 1. Clone or navigate to the project directory
cd path/to/smart_greenhouse_project

# 2. (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate      # Linux/macOS
# or
venv\Scripts\activate          # Windows

# 3. Install Python dependencies
pip install streamlit pandas plotly streamlit-autorefresh paho-mqtt
```

> **Note:** `paho-mqtt` is only required for the MQTT publisher and controller. If you're using Dashboard Mode only, you can skip it.

---

## Quick Start — Dashboard Mode

The simplest way to run the system. All simulation and control logic is self-contained in the Streamlit app — no MQTT broker needed.

```bash
streamlit run dashboard.py
```

Open your browser to `http://localhost:8501` to see the live dashboard.

The dashboard will:
- Begin simulating sensor data immediately
- Auto-refresh every 5 seconds
- Display live metrics, trend charts, actuator status, and alerts

---

## Full IoT Mode — MQTT Broker

Run the publisher and controller separately for a realistic IoT pipeline.

### Terminal 1 — Start the MQTT Sensor Publisher

```bash
python publisher.py
```

The publisher generates simulated sensor readings every **3 seconds** and publishes them to:
- `greenhouse/temp`
- `greenhouse/rh`
- `greenhouse/ec`
- `greenhouse/ph`

It also saves the latest readings to `data/sensor_data.json` on each cycle.

### Terminal 2 — Start the Actuator Controller

```bash
python controller.py
```

The controller subscribes to the four sensor topics above and publishes actuator states to:
- `greenhouse/fan_status`
- `greenhouse/fogger_status`
- `greenhouse/nutrient_status`
- `greenhouse/acid_status`

### Terminal 3 (Optional) — Launch the Dashboard

```bash
streamlit run dashboard.py
```

> When running in Full IoT Mode, the dashboard **uses its own in-memory simulator** by default. To display live MQTT data, wire the dashboard to read from `data/sensor_data.json` or use a Streamlit MQTT integration (see [Future Enhancements](#future-enhancements)).

### Stopping the System

| Component | How to Stop |
|-----------|------------|
| MQTT Publisher | `Ctrl + C` in its terminal |
| MQTT Controller | `Ctrl + C` in its terminal |
| Dashboard | `Ctrl + C` in its terminal, or click **Stop session** in the terminal |

---

## How It Works

### Data Flow

```
┌──────────┐     Step 1       ┌──────────────┐     Step 2       ┌──────────────┐
│ Environment│  Sensor Readings │   Publisher   │ MQTT Topics     │  Controller   │
│ (or sim)  │ ────────────────► │  (publisher.  │ ───────────────► │  (controller. │
│           │                   │  py)          │ greenhouse/temp │  .py)         │
└──────────┘                   └──────────────┘ greenhouse/rh   └──────────────┘
                                              │ greenhouse/ec    │
                                              │ greenhouse/ph     │
                                              └────────┬──────────┘
                                                       │
                                              Step 3   │ Actuator Commands
                                                       ▼
                                              ┌──────────────────┐
                                              │  Dashboard (UI)  │
                                              │  dashboard.py    │
                                              │  ─ Reads & charts│
                                              └──────────────────┘
```

1. **Publish**: `publisher.py` reads sensor values (simulated or real) every 3 seconds and publishes them to MQTT topics.
2. **Subscribe & Control**: `controller.py` listens to sensor topics. When a reading crosses a threshold, it toggles the corresponding actuator **with hysteresis** and publishes the new state.
3. **Visualize**: `dashboard.py` (when running independently) simulates its own data loop, or can be extended to consume MQTT data and display live metrics, charts, and alerts.

### Simulation Loop (Dashboard Mode)

```
┌────────────────────────────────────────────────────────┐
│                    Dashboard Tick (5s)                    │
│                                                            │
│  1. Generate sensor data (drift + cycle + disturbances)   │
│  2. Apply actuator effects (fan cools, fogger humidifies) │
│  3. Run control logic (hysteresis thresholds)             │
│  4. Update session-state history (max 30 readings)         │
│  5. Check alert thresholds (edge detection)               │
│  6. Re-render UI (metrics, charts, alerts)                │
└────────────────────────────────────────────────────────┘
```

### The Hysteresis Principle

Hysteresis prevents **relay chatter** — rapid on/off switching when a sensor value hovers near a threshold. Each actuator has **separate ON and OFF thresholds** to create a dead band:

```
Temperature:  ─────┬─────ON(>30°C)────•────OFF(<28°C)──────
Humidity:     ─────┬─────ON(<60%)─────•────OFF(>65%)──────
EC:           ─────┬─────ON(<1.50)────•────OFF(>1.80)──────
pH:           ─────┬─────ON(>6.50)────•────OFF(<6.20)──────
                  OFF zone       ◄── Dead Band ──►   ON zone
```

Values within the dead band retain their previous state.

### Simulation Engine (`dataSimulation.py`)

The publisher's simulation engine creates realistic sensor behavior:

- **Slow sinusoidal cycle**: A 72-step sine wave drives baseline temperature and humidity, simulating day/night cycles.
- **Stress periods**: At step intervals `70–90` (within a 120-step cycle), heat pressure is boosted by `+2.0` to force threshold crossings.
- **Random walk**: Each sensor has a stochastic drift component bounded by clamping ranges.
- **Actuator feedback**: When an actuator is ON, it influences the sensor it controls (fan lowers temp, fogger raises RH, etc.)

---

## Control Logic & Thresholds

| Parameter | Unit | Optimal Range | Actuator | ON Threshold | OFF Threshold | Alert Trigger |
|-----------|------|--------------|----------|-------------|---------------|---------------|
| Temperature | °C | 25–32 | Fan | > 30.0 | < 28.0 | > 30 (warning), > 35 (critical) |
| Humidity | %RH | 50–70 | Fogger | < 60.0 | > 65.0 | < 60 (warning) |
| EC (Electrical Conductivity) | mS/cm | 1.2–2.0 | Nutrient | < 1.50 | > 1.80 | < 1.50 (warning) |
| pH | — | 5.5–6.5 | Acid | > 6.50 | < 6.20 | > 6.50 (warning) |

### Simulation Value Ranges

| Sensor | Min | Max | Starting Value |
|--------|-----|-----|----------------|
| Temperature | 26.0 °C | 35.5 °C | 29.0 °C |
| Humidity | 52.0 % | 72.0 % | 63.0 % |
| EC | 1.35 mS/cm | 1.95 mS/cm | 1.70 mS/cm |
| pH | 6.00 | 6.75 | 6.25 |

### Dashboard vs. MQTT Controller Logic

| | Dashboard Mode | MQTT Controller |
|---|---|---|
| Control function | `control_greenhouse(data)` in `dashboard.py` | `control_greenhouse(data)` in `controller.py` |
| Hysteresis | Same thresholds | Same thresholds |
| State persistence | Streamlit session state (in-memory) | Python module-level globals |
| Output | Updates UI in-memory | Publishes to MQTT topics |

---

## MQTT Topic Reference

All topics use the prefix `greenhouse/`.

### Sensor Topics (Published by `publisher.py`)

| Topic | Payload | Description |
|-------|---------|-------------|
| `greenhouse/temp` | Float (e.g., `29.35`) | Temperature in °C |
| `greenhouse/rh` | Float (e.g., `62.10`) | Relative humidity in % |
| `greenhouse/ec` | Float (e.g., `1.72`) | Electrical conductivity in mS/cm |
| `greenhouse/ph` | Float (e.g., `6.28`) | pH level |

### Actuator Status Topics (Published by `controller.py`)

| Topic | Payload | Description |
|-------|---------|-------------|
| `greenhouse/fan_status` | `"ON"` / `"OFF"` | Cooling fan status |
| `greenhouse/fogger_status` | `"ON"` / `"OFF"` | Humidifier/fogger status |
| `greenhouse/nutrient_status` | `"ON"` / `"OFF"` | Nutrient dosing pump status |
| `greenhouse/acid_status` | `"ON"` / `"OFF"` | pHdown/acid dosing status |

### Testing MQTT Topics

```bash
# Subscribe to all sensor topics (watch sensor data flow)
mosquitto_sub -h localhost -t "greenhouse/#" -v

# Subscribe to temperature only
mosquitto_sub -h localhost -t "greenhouse/temp"

# Subscribe to actuator statuses
mosquitto_sub -h localhost -t "greenhouse/fan_status" -v

# Publish a test temperature value
mosquitto_pub -h localhost -t "greenhouse/temp" -m "31.5"
```

---

## Data Files

All data files live in the `data/` directory and serve as persistent storage for the system state.

| File | Format | Purpose |
|------|--------|---------|
| `data/sensor_data.json` | JSON object | Latest sensor readings (`temp`, `rh`, `ec`, `ph`). Updated by `publisher.py` every 3s. |
| `data/control_state.json` | JSON object | Current actuator states (`fan`, `fogger`, `nutrient`, `acid`). Intended for controller state persistence. |
| `data/history.json` | JSON array | Historical log of readings. Currently empty — can be extended to append timestamped records for long-term analytics. |

### Example: `sensor_data.json`
```json
{
    "temp": 36.0,
    "rh": 50.0,
    "ec": 1.26,
    "ph": 6.9
}
```

### Example: `control_state.json`
```json
{
    "fan": "OFF",
    "fogger": "OFF",
    "nutrient": "OFF",
    "acid": "OFF"
}
```

---

## Configuration

### Dashboard Configuration (`dashboard.py`)

These constants at the top of `dashboard.py` (line 27–29) control the dashboard behavior:

```python
UPDATE_INTERVAL_MS = 5000      # Auto-refresh interval in milliseconds
MAX_HISTORY = 30               # Maximum number of readings stored in history
MAX_ALERTS = 10                # Maximum number of alerts in the alert queue
```

### Publisher Configuration (`publisher.py`)

```python
BROKER = "localhost"           # MQTT broker address
PORT = 1883                    # MQTT broker port
PUBLISH_INTERVAL = 3           # Seconds between sensor readings
```

### Controller Configuration (`controller.py`)

```python
broker = "localhost"           # MQTT broker address
# Connects on port 1883, subscribes to 4 sensor topics
```

### Changing the MQTT Broker

To use a remote or cloud MQTT broker (e.g., for connecting multiple greenhouses), update the `BROKER` and `broker` variables in `publisher.py` and `controller.py` respectively:

```python
# Example: connect to a cloud broker
BROKER = "mqtt.example.com"
PORT = 1883
```

---

## Dashboard Navigation

The sidebar provides four navigation pages:

| Page | Symbol | Description |
|------|--------|-------------|
| **Dashboard** | ⌂ | Overview: live metrics, environmental trend chart, actuator status, recent alerts |
| **Live Monitoring** | ⌁ | Detailed real-time sensor trends with independent charts |
| **Historical Data** | ▥ | Trend analysis of stored historical readings |
| **Alerts** | ♧ | Full alert log with timestamps and severity levels |

> The sidebar also features a **"Sustainable Agriculture"** call-out with the project's mission: *"Healthy Plants · Healthier Future."*

### UI Components

- **Top Metric Cards**: Large display of current temperature, humidity, EC, and pH values with delta change indicators
- **Status Card**: Overall greenhouse health status (e.g., "Healthy ✓")
- **Environmental Trends Chart**: Multi-axis Plotly line chart (30-point rolling window) showing all four sensors
- **Actuator Status Panel**: Real-time display of all four actuators (ON/OFF with color coding)
- **Recent Alerts Panel**: Live alert feed (max 4 shown) with critical/warning icons
- **Mini Trend Cards**: Independent small charts for each sensor with current value and normal range

---

## Troubleshooting

### Streamlit auto-refresh not working?

The dashboard requires the `streamlit-autorefresh` package. If you see a warning at the bottom of the dashboard instead of auto-refreshing:

```bash
pip install streamlit-autorefresh
```

Restart the dashboard after installation.

### MQTT Connection Refused?

```
Connection refused: localhost:1883
```

The MQTT broker is not running or not reachable. Verify:
1. Mosquitto is installed and running: `mosquitto -v` (or check service status)
2. Port 1883 is not blocked by a firewall
3. `BROKER` in `publisher.py` / `controller.py` matches your broker address

To verify the broker is listening:
```bash
# Linux/macOS
netstat -tlnp | grep 1883

# Windows
netstat -an | findstr 1883
```

### Streamlit dashboard not loading?

- Ensure you're running `streamlit run dashboard.py` from the project directory
- The background image `greenhouse_bg.jpg` should be in the same directory as `dashboard.py`
- Check that all dependencies are installed: `pip install streamlit pandas plotly streamlit-autorefresh`

### Actuator not responding in MQTT mode?

- Ensure `controller.py` is running and connected to the same broker
- Use `mosquitto_sub` to verify sensor data is being published correctly:
  ```bash
  mosquitto_sub -h localhost -t "greenhouse/temp" -v
  ```
- Check the controller's terminal output for the `🌱 Smart Greenhouse Controller running...` message

### Simulation values seem stuck?

In dashboard mode, the simulation runs on the Streamlit session state. If the dashboard tab has been idle or the browser has suspended the page, refresh the page (`Ctrl + R` / `Cmd + R`).

---
## License

Distributed under the MIT License. See `LICENSE` for more information.

---

**🌱 Smart Greenhouse IoT — Cultivating the future, one byte at a time.**

*Built with ❤️ using Python, Streamlit, Plotly, and MQTT.*
