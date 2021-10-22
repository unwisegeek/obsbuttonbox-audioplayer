import paho.mqtt.client as mqtt
from pydub import AudioSegment
from pydub.playback import play
import json
from config import (
    MQTT_HOST,
    MQTT_PORT,
    MQTT_AUTH,
)

SOUNDS_DIR = "."
SOUNDS = {
    "horn": {"name": "horn.wav", "ext": "wav"},
}

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result: {str(rc)}.")
    client.subscribe('buttonbox')


def on_message(client, userdata, msg):
    message = str(msg.payload.decode('utf-8'))
    command = json.loads(message)
    print(f"Processing message from MQTT: [{str(msg.topic)}] {message}")
    if ("snd") in command.keys():
        if command["snd"] in SOUNDS:
            sound = AudioSegment.from_file(
                f"{SOUNDS_DIR}/{SOUNDS[command['snd']]['name']}",
                SOUNDS[command["snd"]]["ext"]
                )
            play(sound)

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

if MQTT_AUTH == None:
    mqtt_client.username_pw_set(
        username=None, 
        password=None,
        )
else:
    mqtt_client.username_pw_set(
        username=MQTT_AUTH["username"],
        password=MQTT_AUTH["password"]
        )
mqtt_client.connect(MQTT_HOST, MQTT_PORT, 15)
try:
    mqtt_client.loop_forever()
except KeyboardInterrupt:
    pass
