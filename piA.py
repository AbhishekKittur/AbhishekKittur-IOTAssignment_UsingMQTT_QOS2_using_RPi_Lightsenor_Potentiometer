from configparser import ConfigParser
from client import Client
import time
import RPi.GPIO as GPIO
from adc import *
import os

class PiAClient(Client):
    def mysetup(self):
        self.lastWillMessage("status/RaspberryPiA")
        self.onConnectStatus ('status/RaspberryPiA', 'online')
        self.gracefulDisconnectMessage('status/RaspberryPiA', 'offline')

        self.connect()

        self.publishedLightSensor = None
        self.publishedThreshold = None

        topic1, topic2 = "lightSensor", "threshold"

        self.subscribe(topic1)
        print(f"Subscribed to: {topic1}")

        self.subscribe(topic2)
        print(f"Subscribed to: {topic2}")

        self.w84L = False 
        self.w84T = False 

        time.sleep(1.5)

    def on_message(self, client, userdata, msg):
        topic = str(msg.topic)
        payload = str(msg.payload.decode("utf-8"))

        if topic == 'lightSensor':
            self.publishedLightSensor = payload
            self.w84L = False
        elif topic == 'threshold':
            self.publishedThreshold = payload
            self.w84T = False 

        print("Received Topic: " + topic + ", Value: " + payload)


    def updateLightSensor(self, newValue, deltaThreshold):
        if not self.w84L:
            if self.publishedLightSensor == None:
                self.publish("lightSensor", payload=str(newValue))
                self.w84L = True
            elif abs(newValue - float(self.publishedLightSensor)) > deltaThreshold:
                self.publish("lightSensor", payload=str(newValue))
                self.w84L = True
            
    def updateThreshold(self, newValue, deltaThreshold):
        if not self.w84T:
            if self.publishedThreshold == None:
                self.publish("threshold", payload=str(newValue))
                self.w84T = True
            elif abs(newValue - float(self.publishedThreshold)) > deltaThreshold:
                self.publish("threshold", payload=str(newValue))
                self.w84T = True
            

def main():
    config_object = ConfigParser()
    config_object.read("config.ini")
    broker_details = config_object["BROKERINFO"]
    broker_address = broker_details["broker_address"]
    broker_port = int(broker_details["broker_port"])

    adc = ADC()

    try:
        client = PiAClient(broker_address, broker_port, 'RaspberryPiA')
        client.mysetup()
        clientRunning = True

        lastReadTime = time.time()

        while True:
            f2 = open('control.txt')
            val = f2.readline()

            if val == str(2):
                #Graceful
                print("Graceful")
                client.disconnect()
                time.sleep(15)
                client.mysetup()
            if val == str(3):
                #Disgraceful
                print("Disconnecting disgraceful in 10secs")
                time.sleep(10)
                print("Disgraceful")
                os.system("sudo ifconfig wlan0 down")
                time.sleep(20)
                os.system("sudo ifconfig wlan0 up")
                client.mysetup()
                
            if (time.time() - lastReadTime) >= 0.1:
                ls = readLDR(adc)
                th = readPOT(adc)
                lastReadTime = time.time()

                if clientRunning:
                    client.updateLightSensor(ls, 0.05)
                    client.updateThreshold(th, 0.05)


            time.sleep(.005) 
        
    except Exception as e:
        print(f"Error {e}")



if __name__ == "__main__":
    main()

