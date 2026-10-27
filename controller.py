import paho.mqtt.client as mqtt

broker = "localhost"

fan_on = False
fogger_on = False
nutrient_on = False
acid_on = False

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)


def publish_status(topic, state):
    client.publish(topic, state)


def on_message(client, userdata, msg):
    global fan_on, fogger_on, nutrient_on, acid_on

    topic = msg.topic
    value = float(msg.payload.decode())

    # FAN: ON above 30°C, OFF below 28°C
    if topic == "greenhouse/temp":
        if value > 30:
            if not fan_on:
                fan_on = True
                publish_status("greenhouse/fan_status", "ON")

        elif value < 28:
            if fan_on:
                fan_on = False
                publish_status("greenhouse/fan_status", "OFF")

    # FOGGER: ON below 60% RH, OFF above 65% RH
    elif topic == "greenhouse/rh":
        if value < 60:
            if not fogger_on:
                fogger_on = True
                publish_status("greenhouse/fogger_status", "ON")

        elif value > 65:
            if fogger_on:
                fogger_on = False
                publish_status("greenhouse/fogger_status", "OFF")

    # NUTRIENT: ON below 1.50 EC, OFF above 1.80 EC
    elif topic == "greenhouse/ec":
        if value < 1.50:
            if not nutrient_on:
                nutrient_on = True
                publish_status("greenhouse/nutrient_status", "ON")

        elif value > 1.80:
            if nutrient_on:
                nutrient_on = False
                publish_status("greenhouse/nutrient_status", "OFF")

    # ACID: ON above pH 6.50, OFF below 6.20
    elif topic == "greenhouse/ph":
        if value > 6.50:
            if not acid_on:
                acid_on = True
                publish_status("greenhouse/acid_status", "ON")

        elif value < 6.20:
            if acid_on:
                acid_on = False
                publish_status("greenhouse/acid_status", "OFF")


def control_greenhouse(data):
    global fan_on, fogger_on, nutrient_on, acid_on

    temp = data["temperature"]
    rh = data["humidity"]
    ec = data["ec"]
    ph = data["ph"]

    # FAN
    if temp > 30:
        fan_on = True
    elif temp < 28:
        fan_on = False

    # FOGGER
    if rh < 60:
        fogger_on = True
    elif rh > 65:
        fogger_on = False

    # NUTRIENT
    if ec < 1.50:
        nutrient_on = True
    elif ec > 1.80:
        nutrient_on = False

    # ACID
    if ph > 6.50:
        acid_on = True
    elif ph < 6.20:
        acid_on = False

    return {
        "fan": "ON" if fan_on else "OFF",
        "fogger": "ON" if fogger_on else "OFF",
        "nutrient": "ON" if nutrient_on else "OFF",
        "acid": "ON" if acid_on else "OFF",
    }


client.on_message = on_message
client.connect(broker, 1883, 60)

client.subscribe("greenhouse/temp")
client.subscribe("greenhouse/rh")
client.subscribe("greenhouse/ec")
client.subscribe("greenhouse/ph")

print("🌱 Smart Greenhouse Controller running...")
print("Immediate ON/OFF threshold control active.")

client.loop_forever()
