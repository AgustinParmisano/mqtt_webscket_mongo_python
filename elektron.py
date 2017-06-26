#Python code LEDblink.py
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import time
import json
import tornado
import tornado.websocket
import datetime, sys, time
import ast
import time
from datetime import timedelta
from pprint import pprint
from pymongo import MongoClient


mongo_client = MongoClient('localhost', 27017)
db = mongo_client['elektrondb']
measures = db['measures']

data_json = ""
data_list = [{"ip": "127.0.0.1","time": "now" ,"name": "test","data": 1}]
clients = []

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    tt = datetime.datetime.now()

    def check_origin(self, origin):
        #print "origin: " + origin
        return True
    # the client connected
    def open(self):
        print ("New client connected")
        self.write_message("You are connected")
        clients.append(self)
        tornado.ioloop.IOLoop.instance().add_timeout(timedelta(seconds=1), self.test)

    def test(self):
        try:
            info = {}
            try:
                time.sleep(1)
                publish.single("ledStatus", "2", hostname="localhost")
                print("DATA LIST: ")
                print data_list
                print data_list[len(data_list)-1]["data"]
                """if (data_list[len(data_list)-1] > 0):
                    text = data_list[len(data_list)-1]# Read the newest output from the MQTT
                    #print(text)
                else:
                    text = {"ip":-1,"time":-1,"data":-1}
                """

                text = data_list[len(data_list)-1]
                info = {
                    "name" : text["name"],
                    "data"    : text["data"],
                    "timestamp" : time.time()
                }


                print("MQTT data info: ")
                print(info)
            except Exception as e:
                print("MQTT data info: ")
                print(info)
                info = {
                    "ip"  : float("0.0"),
                    "time"   : float("0.0"),
                    "name" : float("0.0"),
                    "data"    : -1,
                    "timestamp" : time.time()
                }
                print "Exception: "
                print e
                #raise(e)
            #print("Data readed form MQTT: ")
            #print(info)
            self.write_message(info)
        except Exception as e:
            print "Exception: "
            print e
            print ("restartplease")
            self.write_message("restartplease")
            #raise(e)
        else:
            tornado.ioloop.IOLoop.instance().add_timeout(timedelta(seconds=0.1), self.test)

    # the client sent the message
    def on_message(self, message):
        print ("message: " + message)
        try:
            #message = json.loads(message)
            message = ast.literal_eval(message)
            print(message)
            if(message["relay1"] == 0):
                print "RELAY 0"
                relay_off()
            elif(message["relay1"] == 1):
                print "RELAY 1"
                relay_on()

        except Exception as e:
            print ("cant send valu to devices")
            #raise(e)
        #self.write_message(message)

    # client disconnected
    def on_close(self):
        print ("Client disconnected")
        clients.remove(self)


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("esp8266status")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

    #data_list.append({"ip": "127.0.0.1","time": "now" ,"name": "test","data": float_data})
    #data_list.append(msg.payload)

    list = json.loads(msg.payload)

    for key,value in list.iteritems():
        print ("")
        print key, value

    list = make_data_json(list)
    insert_data(list)
    data_list.append(list)
    return list

    #print data_list
    return data_list

def on_subscribe(client, userdata,mid, granted_qos):
    print "userdata : " +str(userdata)

def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))


def make_data_json(list):
  ip = list['ip']
  time = list['time']
  name = list['name']
  data = list['data']
  new_measure = {'ip': ip, 'time': time, 'name': name, 'data': data}
  output = {'name' : new_measure['name'], 'data' : new_measure['data']}
  #data_json =  json.dumps(output, ensure_ascii=True) #jsonify({'result' : output})
  data_json = json.dumps(output)
  data_json = ast.literal_eval(data_json)
  print data_json
  print type(data_json)
  return data_json

def relay_off():
   print("Sending 1...")
   publish.single("ledStatus", "1", hostname="localhost")
   return "Relay Off!"

def relay_on():
    print("Sending 0...")
    publish.single("ledStatus", "0", hostname="localhost")
    return "Relay On!"

def insert_data(data):
    print("Inserting data: %s" % data)
    measures.insert_one(data)

socket = tornado.web.Application([(r"/websocket", WebSocketHandler),])
if __name__ == "__main__":
    print("Starting MQTT Client")
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost", 1883, 60)
    client.loop_start()

    text = publish.single("ledStatus", "0", hostname="localhost")

    print("Starting WebSocket")
    print("Opening port 8888")
    socket.listen(8888)

tornado.ioloop.IOLoop.instance().start()
