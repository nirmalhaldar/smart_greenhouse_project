import base64
import os
import random
from collections import deque
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None


# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="GreenHouse IoT Dashboard",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

UPDATE_INTERVAL_MS = 5000
MAX_HISTORY = 30
MAX_ALERTS = 10


# ============================================================
# THEME / CSS
# ============================================================
st.markdown(
    """
    <style>
    :root {
        --green: #16834b;
        --green-dark: #0b4d35;
        --green-soft: #e8f7ee;
        --text: #102a22;
        --muted: #6c7b76;
        --border: #dfe8e3;
        --card: rgba(255,255,255,.96);
        --page: #f5f8f6;
        --danger: #ef4444;
        --warning: #f59e0b;
        --blue: #3182f6;
        --purple: #7c4dff;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: var(--page) !important;
        color: var(--text) !important;
    }

    [data-testid="stHeader"] { background: transparent !important; }

    .block-container {
        max-width: 1500px;
        padding: 0 1.25rem 2rem 1.25rem;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #082d24 0%, #0b382c 100%) !important;
        border-right: 0 !important;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.0rem;
    }

    section[data-testid="stSidebar"] * {
        color: #f4fbf7 !important;
    }

    .sidebar-brand {
        padding: 10px 10px 24px 10px;
        border-bottom: 1px solid rgba(255,255,255,.14);
        margin-bottom: 18px;
    }

    .brand-row {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .brand-leaf {
        width: 44px;
        height: 44px;
        border-radius: 14px;
        background: #45d98b;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #073c29 !important;
        font-size: 27px;
        transform: rotate(-8deg);
    }

    .brand-title {
        font-size: 20px;
        font-weight: 800;
        letter-spacing: -.3px;
    }

    .brand-subtitle {
        color: rgba(255,255,255,.65) !important;
        font-size: 10px;
        margin-top: 2px;
    }

    .sidebar-nav {
        margin: 8px 0 22px 0;
    }

    .nav-item {
        padding: 11px 13px;
        border-radius: 10px;
        margin: 5px 0;
        color: #e6f4ee !important;
        font-size: 14px;
    }

    .nav-item.active {
        background: linear-gradient(90deg, #1c8050, #287f55);
        font-weight: 700;
    }

    .nav-icon {
        display: inline-block;
        width: 25px;
        font-size: 17px;
    }

    .sustainable-box {
        margin: 28px 8px 8px 8px;
        padding: 15px;
        border: 1px solid rgba(88,220,145,.35);
        border-radius: 13px;
        background: rgba(5,70,45,.45);
    }

    .sustainable-title {
        color: #8be6b1 !important;
        font-weight: 700;
        font-size: 12px;
    }

    .sustainable-text {
        color: rgba(255,255,255,.75) !important;
        font-size: 11px;
        line-height: 1.45;
        margin-top: 5px;
    }

    .live-pill {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background: #edf8f1;
        color: #16834b !important;
        border-radius: 18px;
        padding: 7px 13px;
        font-weight: 700;
    }

    .live-dot {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        background: #16a34a;
        display: inline-block;
    }

    .hero {
        min-height: 185px;
        width: 100%;
        border-radius: 0;
        padding: 0;
        display: flex;
        align-items: stretch;
        background: #dcefe5;
        border: 0;
        overflow: hidden;
        position: relative;
        margin: 0 -1.25rem 18px -1.25rem;
        width: calc(100% + 2.5rem);
    }

    .hero.has-image {
        background-position: center;
        background-size: cover;
    }

    .section-title {
        font-size: 18px;
        font-weight: 800;
        color: #122e25 !important;
        margin: 18px 0 10px 0;
    }

    .metric-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 13px;
        padding: 16px 16px 13px 16px;
        min-height: 128px;
        box-shadow: 0 2px 8px rgba(25,55,43,.035);
    }

    .metric-top {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .metric-icon {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 23px;
        flex: 0 0 auto;
    }

    .metric-icon.temp { background:#fff0f0; color:#ef4444; }
    .metric-icon.rh { background:#edf5ff; color:#2563eb; }
    .metric-icon.ec { background:#eaf8ef; color:#16a34a; }
    .metric-icon.ph { background:#f1ecff; color:#7c4dff; }

    .metric-label {
        color: #18352c;
        font-size: 13px;
        font-weight: 600;
    }

    .metric-value {
        color: #10251e;
        font-size: 25px;
        font-weight: 800;
        margin-top: 5px;
    }

    .metric-change {
        color: #159447;
        font-size: 12px;
        margin-top: 9px;
    }

    .metric-change span {
        color: #71817b;
        font-size: 10px;
        margin-left: 3px;
    }

    .status-card {
        background: linear-gradient(135deg,#effbf2,#e4f5e9);
        border: 1px solid #bfe4ca;
        border-radius: 13px;
        min-height: 128px;
        padding: 16px;
        position: relative;
        overflow: hidden;
    }

    .status-card:after {
        content: "🌿";
        position: absolute;
        right: 13px;
        bottom: -9px;
        font-size: 60px;
        opacity: .10;
    }

    .status-title { font-weight:800; color:#122d24; font-size:14px; }
    .status-main { font-size:23px; font-weight:800; color:#118149; margin-top:13px; }
    .status-sub { font-size:11px; color:#557067; margin-top:7px; }

    .panel {
        background: rgba(255,255,255,.97);
        border: 1px solid var(--border);
        border-radius: 13px;
        padding: 16px 16px 10px 16px;
        box-shadow: 0 2px 8px rgba(25,55,43,.035);
    }

    .panel-heading {
        display:flex;
        justify-content:space-between;
        align-items:center;
        color:#122e25;
        font-weight:800;
        font-size:16px;
        padding-bottom:10px;
        border-bottom:1px solid #e6ece8;
        margin-bottom:4px;
    }

    .panel-heading small {
        color:#6f7e78;
        font-weight:500;
        font-size:10px;
    }

    .condition-row {
        display:flex;
        align-items:center;
        gap:11px;
        padding:11px 0;
        border-bottom:1px solid #edf1ef;
    }

    .condition-row:last-child { border-bottom:0; }

    .condition-icon {
        width:38px;
        height:38px;
        border-radius:50%;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:18px;
        flex:0 0 auto;
    }

    .condition-name { font-size:12px; color:#60706a; }
    .condition-value { font-size:17px; font-weight:800; color:#132d24; margin-top:2px; }
    .condition-range { margin-left:auto; text-align:right; }
    .optimal { color:#118149; background:#eaf8ef; padding:5px 9px; border-radius:14px; font-size:10px; font-weight:700; display:inline-block; }
    .range-text { color:#6e7c77; font-size:10px; margin-top:5px; }

    .alert-row {
        display:flex;
        gap:11px;
        padding:12px 0;
        border-bottom:1px solid #edf1ef;
    }

    .alert-row:last-child { border-bottom:0; }
    .alert-icon { width:32px; height:32px; border-radius:50%; background:#fff3d8; display:flex; align-items:center; justify-content:center; flex:0 0 auto; }
    .alert-title { color:#33463f; font-size:11px; font-weight:700; }
    .alert-meta { color:#7a8983; font-size:9px; margin-top:5px; }

    .quick-row {
        display:flex;
        align-items:center;
        gap:12px;
        padding:12px 0;
        border-bottom:1px solid #edf1ef;
    }
    .quick-row:last-child { border-bottom:0; }
    .quick-icon { width:30px; text-align:center; font-size:20px; }
    .quick-label { color:#718079; font-size:10px; }
    .quick-value { color:#18352c; font-size:12px; margin-top:3px; }

    .mini-card {
        background: rgba(255,255,255,.97);
        border:1px solid var(--border);
        border-radius:13px;
        padding:12px 13px;
        box-shadow:0 2px 8px rgba(25,55,43,.035);
    }

    .mini-title { color:#18352c; font-weight:700; font-size:11px; display:flex; gap:7px; align-items:center; }
    .mini-value { font-size:16px; font-weight:800; margin-top:11px; color:#162e26; }
    .mini-caption { color:#6e7d77; font-size:9px; margin-top:2px; }

    div[data-testid="stPlotlyChart"] {
        margin-bottom: 0 !important;
    }


    .nav-button > button {
        width: 100% !important;
        text-align: left !important;
        background: transparent !important;
        color: #e6f4ee !important;
        border: 0 !important;
        padding: 11px 13px !important;
        border-radius: 10px !important;
        margin: 4px 0 !important;
        font-size: 14px !important;
        box-shadow: none !important;
    }
    .nav-button > button:hover {
        background: rgba(69,217,139,.16) !important;
    }
    .nav-button.active > button {
        background: linear-gradient(90deg,#1c8050,#287f55) !important;
        font-weight: 700 !important;
    }
    .page-note {
        color:#6f7e78; font-size:12px; margin:4px 0 12px 0;
    }
    .actuator-card {
        background: rgba(255,255,255,.97);
        border:1px solid var(--border);
        border-radius:13px;
        padding:14px;
        min-height:108px;
        box-shadow:0 2px 8px rgba(25,55,43,.035);
    }
    .actuator-name { color:#667770; font-size:11px; }
    .actuator-state { font-size:20px; font-weight:800; margin-top:8px; }
    .state-on { color:#118149; }
    .state-off { color:#8a9792; }

    .stButton > button {
        border-radius: 10px !important;
    }

    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# OPTIONAL GREENHOUSE IMAGE
# ============================================================
def image_data(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except (FileNotFoundError, OSError):
        return None


bg64 = image_data("greenhouse_bg.jpg")


# ============================================================
# SESSION STATE
# ============================================================
def initialize_state():
    if "data" not in st.session_state:
        st.session_state.data = {
            "temp": 29.0,
            "rh": 63.0,
            "ec": 1.70,
            "ph": 6.25,
            "fan": "OFF",
            "fogger": "OFF",
            "nutrient": "OFF",
            "acid": "OFF",
        }

    for key in ["temp_history", "rh_history", "ec_history", "ph_history", "time_history"]:
        if key not in st.session_state:
            st.session_state[key] = deque(maxlen=MAX_HISTORY)

    if "alerts" not in st.session_state:
        st.session_state.alerts = deque(maxlen=MAX_ALERTS)

    if "alert_states" not in st.session_state:
        st.session_state.alert_states = {
            "temp_high": False,
            "temp_critical": False,
            "rh_low": False,
            "ec_low": False,
            "ph_high": False,
        }

    if "simulation_step" not in st.session_state:
        st.session_state.simulation_step = 0

    if "sensor_drift" not in st.session_state:
        st.session_state.sensor_drift = {
            "temp": random.uniform(-0.18, 0.18),
            "rh": random.uniform(-0.45, 0.45),
            "ec": random.uniform(-0.025, 0.025),
            "ph": random.uniform(-0.018, 0.018),
        }


initialize_state()
data = st.session_state.data


# ============================================================
# ALERTS
# ============================================================
def add_alert(message, critical=False):
    st.session_state.alerts.appendleft(
        {
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": message,
            "critical": critical,
        }
    )


def threshold_alert(key, condition, message, critical=False):
    previous = st.session_state.alert_states[key]
    if condition and not previous:
        add_alert(message, critical)
    st.session_state.alert_states[key] = condition


# ============================================================
# CONTROLLER — IMMEDIATE ON/OFF WITH HYSTERESIS
# ============================================================
def control_greenhouse(values):
    temp = values["temp"]
    rh = values["rh"]
    ec = values["ec"]
    ph = values["ph"]

    if temp > 30:
        fan = "ON"
    elif temp < 28:
        fan = "OFF"
    else:
        fan = values["fan"]

    if rh < 60:
        fogger = "ON"
    elif rh > 65:
        fogger = "OFF"
    else:
        fogger = values["fogger"]

    if ec < 1.50:
        nutrient = "ON"
    elif ec > 1.80:
        nutrient = "OFF"
    else:
        nutrient = values["nutrient"]

    if ph > 6.50:
        acid = "ON"
    elif ph < 6.20:
        acid = "OFF"
    else:
        acid = values["acid"]

    return {"fan": fan, "fogger": fogger, "nutrient": nutrient, "acid": acid}


# ============================================================
# IRREGULAR ZIG-ZAG SENSOR SIMULATION
# ============================================================
def generate_sensor_data():
    step = st.session_state.simulation_step
    st.session_state.simulation_step += 1

    temp = data["temp"]
    rh = data["rh"]
    ec = data["ec"]
    ph = data["ph"]
    drift = st.session_state.sensor_drift

    # Randomly alter the direction of each sensor independently.
    if step % random.randint(2, 5) == 0:
        drift["temp"] += random.uniform(-0.18, 0.18)
        drift["rh"] += random.uniform(-0.45, 0.45)
        drift["ec"] += random.uniform(-0.018, 0.018)
        drift["ph"] += random.uniform(-0.012, 0.012)

    drift["temp"] = max(-0.42, min(0.42, drift["temp"]))
    drift["rh"] = max(-0.95, min(0.95, drift["rh"]))
    drift["ec"] = max(-0.055, min(0.055, drift["ec"]))
    drift["ph"] = max(-0.035, min(0.035, drift["ph"]))

    # Pull gently toward normal greenhouse values while retaining randomness.
    temp += (30.0 - temp) * 0.035 + drift["temp"] + random.uniform(-0.16, 0.16)
    rh += (62.5 - rh) * 0.045 + drift["rh"] + random.uniform(-0.35, 0.35)
    ec += (1.65 - ec) * 0.035 + drift["ec"] + random.uniform(-0.018, 0.018)
    ph += (6.32 - ph) * 0.035 + drift["ph"] + random.uniform(-0.012, 0.012)

    # Occasional small disturbances make the trends less artificial.
    if random.random() < 0.08:
        temp += random.uniform(-0.35, 0.35)
        rh += random.uniform(-0.70, 0.70)
    if random.random() < 0.06:
        ec += random.uniform(-0.045, 0.045)
    if random.random() < 0.06:
        ph += random.uniform(-0.025, 0.025)

    # Actuator effects.
    if data["fan"] == "ON":
        temp -= 0.20
    if data["fogger"] == "ON":
        rh += 0.45
    if data["nutrient"] == "ON":
        ec += 0.045
    if data["acid"] == "ON":
        ph -= 0.030

    return {
        "temp": round(max(26.0, min(35.5, temp)), 2),
        "rh": round(max(52.0, min(72.0, rh)), 2),
        "ec": round(max(1.35, min(1.95, ec)), 2),
        "ph": round(max(6.00, min(6.75, ph)), 2),
    }


# ============================================================
# RUN SIMULATION
# ============================================================
data.update(generate_sensor_data())
data.update(control_greenhouse(data))

now = datetime.now()
time_label = now.strftime("%H:%M:%S")

st.session_state.temp_history.append(data["temp"])
st.session_state.rh_history.append(data["rh"])
st.session_state.ec_history.append(data["ec"])
st.session_state.ph_history.append(data["ph"])
st.session_state.time_history.append(time_label)

threshold_alert("temp_critical", data["temp"] > 35, "Critical Temperature", True)
threshold_alert("temp_high", data["temp"] > 30, "High Temperature")
threshold_alert("rh_low", data["rh"] < 60, "Low Humidity - Fogger Activated")
threshold_alert("ec_low", data["ec"] < 1.50, "Low EC - Nutrient Dosing Required")
threshold_alert("ph_high", data["ph"] > 6.50, "High pH - Acid Correction Active")


# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown(
    """
    <div class="sidebar-brand">
        <div class="brand-row">
            <div class="brand-leaf">⌁</div>
            <div>
                <div class="brand-title">GreenHouse IoT</div>
                <div class="brand-subtitle">Smart Farming · Better Tomorrow</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Clickable sidebar navigation
if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"

nav_items = [
    ("⌂", "Dashboard"),
    ("⌁", "Live Monitoring"),
    ("▥", "Historical Data"),
    ("♧", "Alerts"),
]

for icon, label in nav_items:
    active = st.session_state.active_page == label
    st.sidebar.markdown(f'<div class="nav-button {"active" if active else ""}">', unsafe_allow_html=True)
    if st.sidebar.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
        st.session_state.active_page = label
        st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)


st.sidebar.markdown(
    f"""
    <div class="sustainable-box">
        <div style="font-size:28px;">🌿</div>
        <div class="sustainable-title">Sustainable Agriculture</div>
        <div class="sustainable-text">Healthy Plants<br>Healthier Future</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# ============================================================
# FULL-WIDTH GREENHOUSE IMAGE
# ============================================================
hero_style = ""
if bg64:
    hero_style = (
        f' class="hero has-image" style="background-image:'
        f'linear-gradient(rgba(7,42,30,.08), rgba(7,42,30,.12)),'
        f'url(data:image/jpeg;base64,{bg64});"'
    )
else:
    hero_style = ' class="hero"'

st.markdown(f"<div{hero_style}></div>", unsafe_allow_html=True)


# TOP METRIC CARDS
# ============================================================
def metric_card(icon, icon_class, label, value, unit, change):
    return f"""
    <div class="metric-card">
        <div class="metric-top">
            <div class="metric-icon {icon_class}">{icon}</div>
            <div>
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value} <span style="font-size:14px;font-weight:600;">{unit}</span></div>
            </div>
        </div>
        <div class="metric-change">↑ {change} <span>(vs. previous hour)</span></div>
    </div>
    """


c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1.12], gap="small")

with c1:
    st.markdown(metric_card("♨", "temp", "Temperature", f"{data['temp']:.2f}", "°C", f"{abs(data['temp']-29.32):.2f} °C"), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card("💧", "rh", "Humidity", f"{data['rh']:.2f}", "%", f"{abs(data['rh']-60.23):.2f} %"), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card("🌿", "ec", "EC (Electrical Conductivity)", f"{data['ec']:.2f}", "mS/cm", f"{abs(data['ec']-1.56):.2f}"), unsafe_allow_html=True)
with c4:
    st.markdown(metric_card("✥", "ph", "pH", f"{data['ph']:.2f}", "", f"{abs(data['ph']-6.12):.2f}"), unsafe_allow_html=True)
with c5:
    st.markdown(
        """
        <div class="status-card">
            <div class="status-title">🌿 &nbsp;Greenhouse Status</div>
            <div class="status-main">Healthy &nbsp;✓</div>
            <div class="status-sub">All systems are functioning normally.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# MAIN CONTENT ROW
# ============================================================
st.markdown('<div class="section-title">Environmental Trends</div>', unsafe_allow_html=True)
left, middle, right = st.columns([1.75, 0.95, 0.62], gap="small")

# -------------------------
# Combined environmental trend
# -------------------------
with left:
    st.markdown(
        '<div class="panel"><div class="panel-heading"><span>📈 &nbsp;Environmental Trends</span><small>Live · 5 sec telemetry</small></div>',
        unsafe_allow_html=True,
    )

    if len(st.session_state.time_history) >= 2:
        x = list(st.session_state.time_history)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=list(st.session_state.temp_history), name="Temperature (°C)", mode="lines", line=dict(color="#ff8a18", width=2), hovertemplate="%{y:.2f} °C<extra>Temperature</extra>"))
        fig.add_trace(go.Scatter(x=x, y=list(st.session_state.rh_history), name="Humidity (%)", mode="lines", line=dict(color="#6aa5ff", width=2), hovertemplate="%{y:.2f} %<extra>Humidity</extra>"))
        fig.add_trace(go.Scatter(x=x, y=list(st.session_state.ec_history), name="EC (mS/cm)", mode="lines", line=dict(color="#159447", width=2), yaxis="y2", hovertemplate="%{y:.2f} mS/cm<extra>EC</extra>"))
        fig.add_trace(go.Scatter(x=x, y=list(st.session_state.ph_history), name="pH", mode="lines", line=dict(color="#7c4dff", width=2), yaxis="y3", hovertemplate="%{y:.2f}<extra>pH</extra>"))
        fig.update_layout(
            height=310,
            margin=dict(l=8, r=8, t=12, b=5),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#64736d", size=9),
            legend=dict(orientation="h", y=1.10, x=0, font=dict(size=9)),
            hovermode="x unified",
            xaxis=dict(showgrid=True, gridcolor="#edf2ef", zeroline=False, title="Time"),
            yaxis=dict(title="Temperature / Humidity", showgrid=True, gridcolor="#edf2ef", zeroline=False, range=[0, 75]),
            yaxis2=dict(title="EC", overlaying="y", side="right", showgrid=False, range=[0, 2.2]),
            yaxis3=dict(title="pH", overlaying="y", side="right", position=0.97, showgrid=False, range=[5.5, 7.0], tickmode="array", tickvals=[5.5, 6.0, 6.5, 7.0]),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="combined_environment")
    else:
        st.info("Collecting environmental history...")

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# -------------------------
# Actuator status
# -------------------------
with middle:
    st.markdown('<div class="panel"><div class="panel-heading"><span>⚙ &nbsp;Actuator Status</span><small>Live</small></div>', unsafe_allow_html=True)
    actuators = [
        ("🌀", "Fan", data["fan"]),
        ("🌫️", "Fogger", data["fogger"]),
        ("🧪", "Nutrient", data["nutrient"]),
        ("⚗️", "Acid", data["acid"]),
    ]
    for icon, name, state in actuators:
        cls = "state-on" if state == "ON" else "state-off"
        st.markdown(
            f'<div class="condition-row"><div class="condition-icon" style="background:#eaf8ef;">{icon}</div>'
            f'<div><div class="condition-name">{name}</div><div class="actuator-state {cls}">{state}</div></div></div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# Recent alerts
# -------------------------
with right:
    st.markdown('<div class="panel"><div class="panel-heading"><span>🔔 &nbsp;Recent Alerts</span><small>Live</small></div>', unsafe_allow_html=True)
    if st.session_state.alerts:
        for alert in list(st.session_state.alerts)[:4]:
            icon = "🚨" if alert["critical"] else "⚠️"
            st.markdown(
                f'<div class="alert-row"><div class="alert-icon">{icon}</div><div>'
                f'<div class="alert-title">{alert["message"]}</div><div class="alert-meta">{alert["time"]}</div></div></div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown('<div class="page-note">No active alerts.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# INDEPENDENT SENSOR TREND CARDS
# ============================================================
st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
mini_cols = st.columns(4, gap="small")

mini_specs = [
    ("🌡️", "Temperature", "#ef4444", list(st.session_state.temp_history), f"{data['temp']:.2f} °C", "25 – 32 °C"),
    ("💧", "Humidity", "#2563eb", list(st.session_state.rh_history), f"{data['rh']:.2f} %", "50 – 70 %"),
    ("🌿", "EC", "#16a34a", list(st.session_state.ec_history), f"{data['ec']:.2f} mS/cm", "1.2 – 2.0 mS/cm"),
    ("◒", "pH", "#7c4dff", list(st.session_state.ph_history), f"{data['ph']:.2f}", "5.5 – 6.5"),
]

for col, (icon, title, color, yvalues, current, normal) in zip(mini_cols, mini_specs):
    with col:
        st.markdown(f'<div class="mini-card"><div class="mini-title"><span style="color:{color};font-size:17px;">{icon}</span>{title} Trend</div>', unsafe_allow_html=True)
        if len(yvalues) >= 2:
            # Each card has its own independent x-axis, y-range and threshold.
            xs = list(range(1, len(yvalues) + 1))
            lo, hi = min(yvalues), max(yvalues)
            pad = max((hi - lo) * 0.22, 0.02 if title in ["EC", "pH"] else 0.25)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=xs, y=yvalues, mode="lines+markers",
                line=dict(color=color, width=2.2),
                marker=dict(size=4, color=color),
                hovertemplate=f"%{{y:.2f}}<extra>{title}</extra>",
            ))
            fig.update_layout(
                height=105, margin=dict(l=2, r=2, t=5, b=2),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                xaxis=dict(visible=False, fixedrange=True, range=[1, len(xs)]),
                yaxis=dict(visible=False, fixedrange=True, range=[lo-pad, hi+pad]),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=f"mini_{title.lower()}_independent")
        else:
            st.markdown('<div style="height:105px;display:flex;align-items:center;color:#8a9892;font-size:10px;">Collecting trend...</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="mini-caption">Current</div><div class="mini-value" style="color:{color};">{current}</div><div class="mini-caption">Normal Range &nbsp; {normal}</div></div>', unsafe_allow_html=True)


# FOOTER + AUTO REFRESH
# ============================================================
st.markdown(
    '<div style="text-align:center;color:#8a9792;font-size:10px;padding:18px 0 0 0;">🌿 GreenHouse IoT · Smart Farming · Better Tomorrow · 5-second telemetry updates</div>',
    unsafe_allow_html=True,
)

if st_autorefresh is not None:
    st_autorefresh(interval=UPDATE_INTERVAL_MS, key="greenhouse_auto_refresh")
else:
    st.warning("Install streamlit-autorefresh: py -m pip install streamlit-autorefresh")
