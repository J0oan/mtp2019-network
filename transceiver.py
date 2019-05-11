
class Transceiver(object):
    # Primary constructor
    def __init__(self, mode):
        self.mode = mode

    # Transmitter constructor
    @classmethod
    def transmitter(cls):
        return cls("tx")

    # Receiver constructor
    @classmethod
    def receiver(cls):
        return cls("rx")

    def send_data(self):
        raise NotImplementedError
