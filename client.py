from configparser import ConfigParser
import paho.mqtt.client as mqtt 
import time

class Client:

    def __init__(self, address,port, client_id=None):
        self.address = address
        self.port = port
        self.on_connect_topic = None
        self.on_connect_payload = None
        self.on_disconnect_topic = None
        self.on_disconnect_payload = None
        self.publish_in_proc = 0

        self.client = mqtt.Client() if client_id == None else mqtt.Client(client_id = client_id, clean_session=False)

    def on_connect(self, client, userdata, flags, status_code):
        print("Status code:", status_code)
        self.client.is_connected_flag = True

        if self.on_connect_topic != None and self.on_connect_payload != None:
            self.publish(self.on_connect_topic, self.on_connect_payload)

    def on_disconnect(self, client, userdata, status_code):
        self.client.is_connected_flag = False
        print("Disconnected. Status code:",status_code)

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("Subscribed")
        self.client.is_subscribed_flag = True

    def on_message(self, client, userdata, msg):
        print("Topic:" + str(msg.topic))
        print("Received:" + str(msg.payload))

    def on_publish(self, client, userdata, msg):
        if self.publish_in_proc > 0:
            self.publish_in_proc -= 1
            
    def disconnect(self):
        if self.on_disconnect_topic != None and self.on_disconnect_payload != None:
            self.publish(self.on_disconnect_topic, self.on_disconnect_payload)

        if self.publish_in_proc > 0:
            start_time = time.time()
            seconds = 2.5
            while self.publish_in_proc > 0:
                current_time = time.time()
                elapsed_time = current_time - start_time
                if elapsed_time > seconds:
                    break

        self.client.disconnect()
        self.client.loop_stop()

    def connect(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        self.publish_in_proc = 0

        try:
            self.client.is_connected_flag = False
            self.client.connect(self.address, self.port, keepalive=5)
            self.client.loop_start()
            while not self.client.is_connected_flag:
                continue
        except Exception as e:
            print("Connection failed, with details", e)
            raise e

    def onConnectStatus(self, topic, payload):
        self.on_connect_topic = topic
        self.on_connect_payload = payload

    def gracefulDisconnectMessage(self, topic, payload):
        self.on_disconnect_topic = topic
        self.on_disconnect_payload = payload

    def lastWillMessage(self, topic):
        self.client.will_set(topic, payload = 'offline', qos=2, retain=True)

    def publish(self, topic, payload):
        print ("Published Topic: " + topic + ", Value: " + payload)
        self.publish_in_proc += 1
        self.client.publish(topic, payload=payload, qos=2, retain=True)

    def subscribe(self, topic):
        self.client.is_subscribed_flag = False
        self.client.subscribe(topic, 2)
        while not self.client.is_subscribed_flag:
            continue

if __name__ == "__main__":

    config_object = ConfigParser()
    config_object.read("config.ini")
    broker_details = config_object["BROKERINFO"]
    broker_address = broker_details["broker_address"]
    broker_port = int(broker_details["broker_port"])

    client = Client(broker_address, broker_port)
    client.setStatusWill("status/RaspberryPiA")
    client.connect()
    client.publish("status/RaspberryPiA", payload='online')
    client.subscribe("lightSensor")

    while True:
        client.publish("lightSensor", payload='1')
        time.sleep(0.5)
