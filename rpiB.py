from configparser import ConfigParser
from client import Client
import time
import RPi.GPIO as GPIO
import json

LIGHT_STATUS_PIN = 11
PI_A_PIN = 13
PI_C_PIN = 15

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LIGHT_STATUS_PIN, GPIO.OUT)
GPIO.setup(PI_A_PIN, GPIO.OUT)
GPIO.setup(PI_C_PIN, GPIO.OUT)

class PiBClient(Client):
    def mysetup(self):
        client.connect()

        client.brokerLightStatus = False
        client.lightStatus = False
        client.piA = False
        client.piC = False

        topic1, topic2, topic3 = "lightStatus", "status/RaspberryPiA", "status/RaspberryPiC"
        client.subscribe(topic1)
        #print(f"Subscribed to: {topic1}")

        client.subscribe(topic2)
        #print(f"Subscribed to: {topic2}")

        client.subscribe(topic3)
        #print(f"Subscribed to: {topic3}")


    def on_message(self, client, userdata, msg):
        topic = str(msg.topic)
        payload = str(msg.payload.decode("utf-8"))

        if topic == 'lightStatus':
            if payload == 'TurnOn':
                self.brokerLightStatus = True
            else:
                self.brokerLightStatus = False
        elif topic == 'status/RaspberryPiA':
            if payload == 'online':
                self.piA = True
            else:
                self.piA = False
        elif topic == 'status/RaspberryPiC':
            if payload == 'online':
                self.piC = True
            else:
                self.piC = False

        if self.piC == True:
            self.lightStatus = self.brokerLightStatus
        else:
            self.lightStatus = False

        print ("Received Topic: " + topic + ", Value: " + payload)
        print("Updated Outputs:\n   PiA Online (" + str(self.piA) + ")\n   PiC Online (" + str(self.piC) + ")\n   Light Status On (" + str(self.lightStatus)+ ")")

if __name__ == "__main__":

    config_object = ConfigParser()
    config_object.read("config.ini")
    broker_details = config_object["BROKERINFO"]
    broker_address = broker_details["broker_address"]
    broker_port = int(broker_details["broker_port"])

    
    client = PiBClient(broker_address, broker_port, 'RaspberryPiB')
    client.mysetup()

    LightStatusCache, PiAStatusCache, PiCStatusCache = None, None, None
    time.sleep(1)

    while True:
        if LightStatusCache != client.lightStatus or PiAStatusCache != client.piA or PiCStatusCache != client.piC:
            GPIO.output(LIGHT_STATUS_PIN, client.lightStatus)
            GPIO.output(PI_A_PIN, client.piA)
            GPIO.output(PI_C_PIN, client.piC)
        time.sleep(.005) 

   
