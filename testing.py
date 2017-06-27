import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import json
import tornado
import tornado.websocket
import datetime, sys, time
import ast
from datetime import timedelta
from pymongo import MongoClient
import Queue
import pprint

q = Queue.Queue()

#Mongo
mongo_client = MongoClient('localhost', 27017)
db = mongo_client['testdb'] #db example
#measures = db['collname'] #coll example

#Websockets clients
clients = []

#Mongo Basic Functions

def get_single_document(collname):
    return db[collname].find_one()

def get_all_documents(collname):
    return db[collname].find()

#Get documents with some key:value, key & value has to by string types
def get_key_value(collname, key, value):
    return db[collname].find({key:value})

#Insert document, has to be json or dictionary type
def insert_one_document(collname, document):
    db[collname].insert_one(document)

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    tt = datetime.datetime.now()

    def check_origin(self, origin):
        #print "origin: " + origin
        return True

    # the client connected
    def open(self):
        print ("New client connected")
        #self.write_message("You are connected")
        clients.append(self)
        tornado.ioloop.IOLoop.instance().add_timeout(timedelta(seconds=1), self.test)

    def test(self):
        try:
            message = {'potencia':'0','tension':'0'}
            #print("Qeue: " + str(q))
            while not q.empty():
                message = q.get()
                print("Message in MQTT Qeue: " + str(message))
            try:
                time.sleep(1)
            except Exception as e:
                print "Exception: "
                print e
                #raise(e)
            #message =  {'potencia':'78','tension':'62'}
            try:
                message = ast.literal_eval(str(message))
                print("Sending Websocket Message: " + str(type(message)))
                self.write_message(message)
            except Exception as e:
                print "Exception in Websocket AST: "
                print e

        except Exception as e:
            print "Exception in WebSocket test Function: "
            print e
            self.write_message("Error: " + str(e))
            #raise(e)
        else:
            tornado.ioloop.IOLoop.instance().add_timeout(timedelta(seconds=0.1), self.test)

    # the client sent the message
    def on_message(self, message):
        print ("Message From Web: " + message)
        try:
            #message = ast.literal_eval(message)
            print("AST Message: " + str(message))

            if message == "mqtt":
                #Send message from websocket to mqtt
                publish.single("topic", "mongo_put:posting from websocket then mqtt then mongo!", hostname="localhost")

            if message == "mongo":
                #Save message from websocket to mongo
                insert_one_document("testcoll", {"test_message":message})

        except Exception as e:
            print ("Exception:")
            print e
        #self.write_message(message)

    # client disconnected
    def on_close(self):
        print ("Client disconnected")
        clients.remove(self)

#MQTT Functions
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("topic")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

    message = str(msg.payload)
    q.put(message)
    try:
        message = ast.literal_eval(str(message))
        print("Saving Data in MongoDB" + str(type(message)))
        insert_one_document("testcoll", message)
    except Exception as e:
        print ("Exception:")
        print e


def on_subscribe(client, userdata,mid, granted_qos):
    print "userdata : " +str(userdata)

def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))


socket = tornado.web.Application([(r"/websocket", WebSocketHandler),])
if __name__ == "__main__":
    #Start WebScoket Client
    print("Starting WebSocket")
    print("Opening port 8888")
    socket.listen(8888)

    #Start MQTT Client
    print("Starting MQTT Client")
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost", 1883, 60)
    client.loop_start()

tornado.ioloop.IOLoop.instance().start()
