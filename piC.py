import time
from client import Client
from configparser import ConfigParser
import os


class PiCClient(Client):
    def initialize(self):
        self.lastWillMessage("status/RaspberryPiC")
        self.onConnectStatus ('status/RaspberryPiC', 'online')
        self.gracefulDisconnectMessage('status/RaspberryPiC', 'offline')

        self.connect()
        
        self.lightSensor, self.threshold, self.lightStatus = None, None, None

        topic1, topic2, topic3 = 'lightStatus', 'lightSensor', 'threshold'
        client.subscribe(topic1)
        print(f"Subscribed to: {topic1}")

        client.subscribe(topic2)
        print(f"Subscribed to: {topic2}")

        client.subscribe(topic3)
        print(f"Subscribed to: {topic3}")

        time.sleep(1)

    def on_message(self, client, userdata, msg):
        topic, payload = str(msg.topic), str(msg.payload.decode("utf-8"))

        if topic == 'lightSensor':
            self.lightSensor = float(payload)
        elif topic == 'threshold':
            self.threshold = float(payload)
        elif topic == 'lightStatus':
            self.lightStatus = payload

        print ("Received Topic: " + topic + ", Value: " + payload)

    def updateLightStatus(self):
        if self.lightSensor != None and self.threshold != None:
            if (self.lightSensor > self.threshold) and self.lightStatus != 'TurnOn':
                self.lightStatus = 'TurnOn'
                self.publish("lightStatus", payload=self.lightStatus)
            elif (self.lightSensor <= self.threshold) and self.lightStatus != 'TurnOff':
                self.lightStatus = 'TurnOff'
                self.publish("lightStatus", payload=self.lightStatus)

if __name__ == "__main__":

    config_object = ConfigParser()
    config_object.read("config.ini")

    broker_details = config_object["BROKERINFO"]
    broker_address = broker_details["broker_address"]
    broker_port = int(broker_details["broker_port"])

    try:
        client = PiCClient(broker_address, broker_port, 'RaspberryPiC')
        client.initialize()
        clientRunning = True 
        time.sleep(1)

        while True:
            
            f2 = open('control.txt')
            val = f2.readline()

            if val == str(2):
                #Graceful
                print("Graceful")
                client.disconnect()
            if val == str(3):
                #Disgraceful
                print("Disgraceful")
                os.system("netsh interface set interface 'Wifi' disabled")
            if val == str(4):
                os.system("netsh interface set interface 'Wifi' enabled")
                client.initialize()
            
            client.updateLightStatus()
            time.sleep(.005) 
            
    except KeyboardInterrupt:
        client.disconnect()
        quit()
