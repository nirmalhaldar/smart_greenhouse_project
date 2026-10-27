import json
import time
from pathlib import Path

import paho.mqtt.client as mqtt

from dataSimulation import generate_sensor_data


BROKER = "localhost"
PORT = 1883
PUBLISH_INTERVAL = 3
BASE_DIR = Path(__file__).resolve().parent
SENSOR_DATA_FILE = BASE_DIR / "data" / "sensor_data.json"


def save_sensor_data(data):
    """Keep the sensor-data file synchronized with the latest reading."""
    SENSOR_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with SENSOR_DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def publish_sensor_data():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(BROKER, PORT, 60)

    data = {
        "temp": 29.0,
        "rh": 63.0,
        "ec": 1.70,
        "ph": 6.25,
        "fan": "OFF",
        "fogger": "OFF",
        "nutrient": "OFF",
        "acid": "OFF",
    }

    step = 0

    try:
        while True:
            values = generate_sensor_data(data, step)
            data.update(values)
            save_sensor_data(values)

            topics = {
                "temp": "greenhouse/temp",
                "rh": "greenhouse/rh",
                "ec": "greenhouse/ec",
                "ph": "greenhouse/ph",
            }

            for key, topic in topics.items():
                client.publish(topic, data[key])

            print("Published:")
            print(f"Temperature: {data['temp']} °C")
            print(f"Humidity: {data['rh']} %")
            print(f"EC: {data['ec']}")
            print(f"pH: {data['ph']}")
            print("----------------------")

            step += 1
            time.sleep(PUBLISH_INTERVAL)
    finally:
        client.disconnect()


if __name__ == "__main__":
    publish_sensor_data()
