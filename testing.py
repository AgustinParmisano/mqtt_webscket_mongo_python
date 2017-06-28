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

class Measure(object):
    """docstring for Measure."""
    def __init__(self, potencia, tension, timedata, state):
        super(Measure, self).__init__()
        self.potencia = potencia
        self.tension = tension
        self.timedata = timedata
        self.state = state

    def set_potencia(self, potencia):
        self.potencia = potencia

    def set_tension(self, tension):
        self.tension = tension

    def set_timedata(self, timedata):
        self.timedata = timedata

    def set_state(self, state):
        self.state = state

    def get_potencia(self):
        return self.potencia

    def get_tension(self):
        return self.tension

    def get_timedata(self):
        return self.timedata

    def get_state(self):
        return self.state

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

#Get data from-to times: String Format Example: 2013-09-28 20:30:55.78200
def get_documents_from_to_time(collname, from_time, to_time):
    #Query Example in Mongo shell:
    #db.testcoll.find({timedata:{$gte: ISODate("2017-06-27T20:28:00.000Z"),$lt: ISODate("2017-06-27T20:28:10.000Z")}})
    from_time = datetime.datetime.strptime(from_time, "%Y-%m-%d %H:%M:%S.%f")
    to_time = datetime.datetime.strptime(to_time, "%Y-%m-%d %H:%M:%S.%f")
    posts = db.testcoll.find({"timedata":{"$gte": from_time, "$lt": to_time}})
    return posts

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
                time.sleep(1)
                message = q.get()
                print("Message in MQTT Qeue: " + str(message))
                try:
                    if len(clients) > 0:
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
            #print("AST Message: " + str(message))

            if message == "on":
                #Send message from websocket to mqtt
                publish.single("state", "on", hostname="localhost")

            elif message == "off":
                #Save message from websocket to mongo
                publish.single("state", "off", hostname="localhost")

            else:
                print "ELSE"
                #Eval if message is valid and do something (e.g: search in mongo)
                #String Format Example: 2013-09-28 20:30:55.78200
                from_time = "2017-06-27 21:41:00.00000" #example
                to_time = "2017-06-27 21:41:10.00000"   #example
                docs = get_documents_from_to_time("testcoll", from_time, to_time)
                output = []
                for post in docs:
                    print post["potencia"]
                    pprint.pprint(post)
                    #potencia, tension, timedata, state
                    output.append({'potencia' : post["potencia"], 'tension' : post["tension"],'timedata' : post['timedata'], "state" : post['estado']})
                print output

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
        date_time_now = datetime.datetime.now()

        message = ast.literal_eval(str(message))

        measure = Measure(message["potencia"], message["tension"], date_time_now, message["estado"], )

        print("Saving Data in MongoDB" + str(measure.__dict__))
        insert_one_document("testcoll", measure.__dict__)
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
