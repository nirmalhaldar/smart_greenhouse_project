import math
import random


def generate_sensor_data(data, step):
    """
    Generate the same gradual/realistic sensor changes used by the
    original dashboard.

    The caller owns the simulation step so Streamlit session-state
    behavior remains unchanged.
    """
    temp = data["temp"]
    rh = data["rh"]
    ec = data["ec"]
    ph = data["ph"]

    # Slow environmental cycle
    cycle = (step % 72) / 72.0
    heat_pressure = 1.8 * math.sin(cycle * 2 * math.pi)

    # Gradual stress period to demonstrate alerts
    stress_phase = step % 120

    if 70 <= stress_phase <= 90:
        heat_pressure += 2.0

    # Temperature
    temp_change = (
        0.10
        + (heat_pressure * 0.08)
        + random.uniform(-0.22, 0.28)
    )

    if data["fan"] == "ON":
        temp_change -= 0.45

    temp += temp_change
    temp = max(25.0, min(36.0, temp))

    # Humidity
    rh_change = random.uniform(-0.35, 0.25)

    if data["fogger"] == "ON":
        rh_change += 0.85
    else:
        rh_change -= 0.05

    # High temperature lowers relative humidity
    rh_change -= max(0, temp - 30) * 0.04

    rh += rh_change
    rh = max(50.0, min(75.0, rh))

    # EC
    ec_change = random.uniform(-0.035, 0.025)

    if data["nutrient"] == "ON":
        ec_change += 0.08

    ec += ec_change
    ec = max(1.20, min(2.30, ec))

    # pH
    ph_change = random.uniform(-0.012, 0.018)

    if data["acid"] == "ON":
        ph_change -= 0.055

    if temp > 31:
        ph_change += 0.015

    ph += ph_change
    ph = max(5.70, min(6.90, ph))

    return {
        "temp": round(temp, 2),
        "rh": round(rh, 2),
        "ec": round(ec, 2),
        "ph": round(ph, 2),
    }
