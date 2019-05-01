from packet import Packet
from transceiver import Transceiver


class Node(object):
    def __init__(self, config):
        self.config = config
        self.packet = Packet(self.config)
        self.transmitter = Transceiver.transmitter()
        self.receiver = Transceiver.receiver()
        # Initialize radios

    def broadcast_flooding(self):
        discovery_broadcast_packet = self.packet.generate_discovery()

        for retransmission in range(self.config.N):

        raise NotImplementedError

    def broadcast_ack(self):
        raise NotImplementedError

    def send_packets(self):
        raise NotImplementedError

    def receive_packets(self):
        raise NotImplementedError

    def any_neighbors(self):
        """
        True if it has neighbors, False otherwise
        :return: Bool
        """
        raise NotImplementedError

    def any_neighbor_without_file(self):
        raise NotImplementedError

    def any_neighbor_without_token(self):
        raise NotImplementedError

    def any_active_predecessor(self):
        raise NotImplementedError

    def return_token(self):
        raise NotImplementedError

    def wait_token(self):
        raise NotImplementedError

    def pass_token(self):
        raise NotImplementedError
