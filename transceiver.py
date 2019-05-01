from lib_nrf24 import NRF24
import spidev
import json
import time
import configHardware

class Transceiver(object):
    # Primary constructor
    def __init__(self, mode):
        self.mode = mode
        self.pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

    # Transmitter constructor
    @classmethod
    def transmitter(cls):
        return cls("tx")

    # Receiver constructor
    @classmethod
    def receiver(cls):
        return cls("rx")

    def initialize_radio(self):

        #Falta definir la variable GPIO
        radio = NRF24(GPIO, spidev.SpiDev())
        radio.begin(configHardware.CSN, configHardware.CE)
        time.sleep(2)
        radio.setRetries(15, 15)
        radio.setPayloadSize(32)
        radio.setChannel(configHardware.CHANNEL)
        radio.setDataRate(NRF24.BR_250KBPS)
        radio.setPALevel(NRF24.PA_MIN)
        radio.setAutoAck(False)
        radio.enableDynamicPayloads()
        radio.enableAckPayload()
        return radio

    def read_data(self,buffer):
        self.read(buffer,self.getDynamicPayloadSize())
        return buffer

    def wait_data(self):
        return self.available(self.pipes[0])

    def send_data(self,payload):
        self.write(payload)




