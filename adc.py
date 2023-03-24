import spidev
import time

LDR_CHANNEL = 0
POT_CHANNEL = 7

LDR_MIN = 850
LDR_MAX = 1018 

POT_MIN = 0 
POT_MAX = 1019 

class ADC:
    def __init__(self):
        self.spi = spidev.SpiDev()
        self.spi.open(0,0)
        self.spi.max_speed_hz=1000000

    def read(self, channel):
        adc = self.spi.xfer2([1,(8+channel)<<4,0])
        value = ((adc[1]&3) << 8) + adc[2]
        return value

def readLDR(adc):
    raw = min(adc.read(LDR_CHANNEL), LDR_MAX)
    return (raw - LDR_MIN) / (LDR_MAX - LDR_MIN)

def readPOT(adc):
    raw = min(adc.read(POT_CHANNEL), POT_MAX) 
    return (raw - POT_MIN) / (POT_MAX - POT_MIN)

