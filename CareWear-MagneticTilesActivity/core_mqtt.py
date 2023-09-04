import paho.mqtt.client as mqtt

# Define callback functions for MQTT events
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe("M5StackcPlus/hello")  # Subscribe to the MQTT topic you're interested in
    else:
        print(f"Failed to connect, return code: {rc}")

def on_message(client, userdata, message):
    print(f"Received message '{message.payload.decode()}' on topic '{message.topic}'")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"Unexpected disconnection, return code: {rc}")

# Create an MQTT client
client = mqtt.Client()

# Set the callback functions
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Connect to the MQTT broker
client.connect("test.mosquitto.org", 1883)  # Replace with your MQTT broker's address and port

# Start the MQTT client loop (this is a non-blocking call)
client.loop_forever()
