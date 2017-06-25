import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import tornado
import tornado.websocket
from datetime import timedelta
from pymongo import MongoClient

mongo_client = MongoClient('localhost', 27017)
db = mongo_client['dbname']
measures = db['collname']

clients = []

class WebSocketHandler(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        print "Origin: " + str(origin)
        return True

    # the client connected
    def open(self):
        print ("New client connected")
        self.write_message("You are connected")
        clients.append(self)
        tornado.ioloop.IOLoop.instance().add_timeout(timedelta(seconds=1), self.test)

    # the client sent the message
    def on_message(self, message):
        print ("Message: " + message)
        try:
            message = ast.literal_eval(message)
            print(message)

        except Exception as e:
            print ("Exception:")
            print e

    # client disconnected
    def on_close(self):
        print ("Client disconnected")
        clients.remove(self)

    def test(self):
        message = "Hello Web Socket!"
        try:
            self.write_message(message)
        except Exception as e:
            print "Exception: "
            print e
            self.write_message("Es un write message")
        else:
            tornado.ioloop.IOLoop.instance().add_timeout(timedelta(seconds=0.1), self.test)

class MyMQTTClass:

    def __init__(self, clientid=None, topic="topic"):
        self._mqttc = mqtt.Client(clientid)
        self._mqttc.on_message = self.mqtt_on_message
        self._mqttc.on_connect = self.mqtt_on_connect
        self._mqttc.on_publish = self.mqtt_on_publish
        self._mqttc.on_subscribe = self.mqtt_on_subscribe
        self.topic = topic

    def mqtt_on_connect(self, mqttc, obj, flags, rc):
        print("rc: "+str(rc))

    def mqtt_on_message(self, mqttc, obj, msg):
        print("Msg: " + str(msg))
        print("Msg.topic: " + msg.topic)
        print("Msg.qos: " + str(msg.qos))
        print("Msg.payload: " + str(msg.payload))
        print("Obj: " + str(obj))
        print("Mqttc: " + str(mqttc))
        print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))

    def mqtt_on_publish(self, mqttc, obj, mid):
        print("mid: "+str(mid))

    def mqtt_on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos))

    def mqtt_on_log(self, mqttc, obj, level, string):
        print(string)

    def run(self):
        self._mqttc.connect("localhost", 1883, 60)
        self._mqttc.subscribe(self.topic, 0)
        rc = 0
        while rc == 0:
            rc = self._mqttc.loop()
        return rc

    def set_topic(self, topic):
        self.topic = topic

    def set_topic(self, topic):
        self.topic = topic

socket = tornado.web.Application([(r"/websocket", WebSocketHandler),])

if __name__ == "__main__":
    print("Starting WebSocket")
    print("Opening port 8888")
    socket.listen(8888)

    print("Starting MQTT Client")
    mqttc = MyMQTTClass()
    rc = mqttc.run()
    print("rc: "+str(rc))

tornado.ioloop.IOLoop.instance().start()
