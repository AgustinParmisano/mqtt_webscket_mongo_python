import random
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import json
import datetime, sys, time
import ast
from datetime import timedelta

#MQTT Functions
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("topic")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def on_subscribe(client, userdata,mid, granted_qos):
    print "userdata : " +str(userdata)

def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))

if __name__ == "__main__":
    #Start MQTT Client
    print("Starting MQTT Client")
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost", 1883, 60)
    client.loop_start()
    while True:
        time.sleep(1)
        potencia = random.randint(0,100)
        tension = random.randint(0,100)
        data = {"potencia": potencia, "tension": tension}
        publish.single("topic", str(data), hostname="localhost")
