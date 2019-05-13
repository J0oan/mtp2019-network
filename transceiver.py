from RF24 import *


class Transceiver(RF24):
    # Primary constructor
    def __init__(self, mode, config):
        self.mode = mode
        self.config = config
        self.channel = None
        if mode == 'tx':
            RF24.__init__(self, self.config.Tx_CS, self.config.Tx_CSN, BCM2835_SPI_SPEED_8MHZ)
        else:
            RF24.__init__(self, self.config.Rx_CS, self.config.Rx_CSN, BCM2835_SPI_SPEED_8MHZ)
        self.begin()
        self.setPALevel(RF24_PA_MIN)
        self.setDataRate(RF24_250KBPS)
        self.setAutoAck(False)
        self.enableDynamicPayloads()
        self.openWritingPipe(0xf0f0f0f0e1)
        self.openReadingPipe(1, 0xf0f0f0f0e1)
        self.printDetails()
        self.stopListening()

    # Transmitter constructor
    @classmethod
    def transmitter(cls, config):
        return cls("tx", config)

    # Receiver constructor
    @classmethod
    def receiver(cls, config):
        return cls("rx", config)

    def change_channel(self, channel):
        if channel != self.channel:
            if self.mode == 'rx':
                self.stopListening()

            self.channel = channel
            self.setChannel(channel)

            if self.mode == 'rx':
                self.startListening()
