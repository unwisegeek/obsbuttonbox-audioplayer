import os
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from pydub import AudioSegment
from pydub.playback import play
import json
from config import (
    MQTT_HOST,
    MQTT_PORT,
    MQTT_AUTH,
)

SOUNDS_DIR = "./sounds/"

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result: {str(rc)}.")
    client.subscribe('buttonbox')


def on_message(client, userdata, msg):
    message = str(msg.payload.decode('utf-8'))
    command = json.loads(message)
    print(f"Processing message from MQTT: [{str(msg.topic)}] {message}")
    if ("snd") in command.keys():
        if command["snd"] in SOUNDS.keys():
            sound = AudioSegment.from_file(
                f"{SOUNDS_DIR}/{SOUNDS[command['snd']]['name']}",
                SOUNDS[command["snd"]]['ext']
                )
            try:
                play(sound)
            except FileNotFoundError:
                pass
    if ("refresh") in command.keys():
        refresh_sounds

def keycount(file_key, SOUNDS):
    keycount = 0
    for key in SOUNDS.keys():
        if file_key == key.split('-')[0]:
            keycount += 1
    return keycount

def refresh_sounds():
    SOUNDS = {}
    ALLOWED_FORMATS = ('mp3', 'wav', 'aac', 'ogg')
    file_ext = ""
    keylist = []
    keydict = {}
    # # Build SOUNDS dictionary
    for file in os.listdir(SOUNDS_DIR):
        filename = file.split('.')
        if filename[len(filename) - 1] in ALLOWED_FORMATS:
            file_key = filename[0].split('-')[0]
            file_ext = filename[len(filename) - 1]
            if keycount(file_key, SOUNDS) == 0:
                SOUNDS[f"{file_key}-0"] = {'name': file, 'ext': file_ext}
            else:
                SOUNDS[f"{file_key}-{len(SOUNDS)}"] = {'name': file, 'ext': file_ext}

    sound_list = ""
    sound_cnt = 0
    for key in SOUNDS.keys():
        sound_cnt += 1
        value = f"{key}," if sound_cnt < len(SOUNDS.keys()) else f"{key}"
        sound_list += value

    publish.single(
        'buttonbox-sounds', 
        sound_list,
        qos=0, 
        retain=True, 
        hostname='homeassistant.lan', 
        port=1883, 
        client_id="", 
        keepalive=60,
        will=None,
        auth=MQTT_AUTH,
        tls=None,
        protocol=mqtt.MQTTv311,
        transport="tcp",
        )



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
