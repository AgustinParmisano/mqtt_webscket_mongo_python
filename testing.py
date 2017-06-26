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
    return db.collname.find_one()

def get_all_documents(collname):
    return db.collname.find()

#Get documents with some key:value, key & value has to by string types
def get_key_value(collname, key, value):
    return db.collname.find({key:value})

#Insert document, has to be json or dictionary type
def insert_one_document(collname, document):
    db.collname.insert_one(document)

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
            message = "Hello Web Socket!"
            #print("Qeue: " + str(q))
            while not q.empty():
                message = q.get()
                print("Websocket Message: " + str(message))
                if str(message) == "mongo_get":
                    pprint.pprint(get_all_documents("testcoll"))
                if str(message) == "mongo_put":
                    insert_one_document("testcoll", {"mqtt_message":str(message)})
                if str(message) == "mqtt_pub":
                    publish.single("topic", message, hostname="localhost")
            try:
                time.sleep(1)
            except Exception as e:
                print "Exception: "
                print e
                #raise(e)
            self.write_message(message)
        except Exception as e:
            print "Exception: "
            print e
            self.write_message("Es un write message")
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

    method = str(msg.payload).split(":")[0]
    message = str(msg.payload).split(":")[1]

    if str(method) == "websocket":
        print("Method: " + str(method))
        print("Message: " + str(message))
        q.put(message)
        #send to websocket

    if str(method) == "mongo_put":
        #save msg in mongo
        insert_one_document("testcoll", {"mqtt_message":str(message)})

    if str(method) == "mongo_get":
        #save msg in mongo
        pprint.pprint(get_single_document("testcoll"))

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
