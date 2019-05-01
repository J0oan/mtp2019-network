import threading
from packet import Packet
from transceiver import Transceiver
import cte


class Node(object):
    def __init__(self, config):
        self.config = config
        self.state = cte.BROADCAST_FLOODING if config.role == 'tx' else cte.BROADCAST_ACK
        self.packet = Packet(self.config)
        self.transmitter = Transceiver.transmitter()
        self.receiver = Transceiver.receiver()
        self.retransmission = 0
        self.timeout = ''
        self.neighbors = {}
        self.predecessor = ''
        self.file = False if config.role == 'rx' else True
        self.master = False if config.role == 'rx' else True

        # Initialize timeout
        if self.state == cte.BROADCAST_ACK:
            self.timeout = threading.Timer(self.config.Tout_Broadcast_Receiver, self.end_error)

        # Initialize radios

    def broadcast_flooding(self):
        if self.retransmission > 0:
            self.state = cte.IDLE_FLOODING
            self.timeout = threading.Timer(self.config.Tout_Broadcast, self.broadcast_flooding)
            discovery_broadcast_packet = self.packet.generate_discovery()
            self.send_packet(discovery_broadcast_packet)
            self.retransmission -= 1

        else:
            self.state = cte.SEND_PACKET if len(self.neighbor) > 0 else cte.COMMUNICATION_OVER
            self.timeout = ''

    def broadcast_ack(self):
        if self.retransmission > 0:
            self.timeout = threading.Timer(self.config.Tout_ACK, self.broadcast_ack)
            flags = {
                "file": self.file,
                "master": self.master
            }
            ack_packet = self.packet.generate_ack_discovery(self.predecessor, flags)
            self.send_packet(ack_packet)
            self.retransmission -= 1

        else:
            self.state = cte.BROADCAST_ACK

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

    def end_error(self):
        self.state = cte.END

    def check_receiver(self):
        if self.receiver.available():
            packet = self.receiver.read()
            self.packet.decapsulate_packet(packet)

            if packet:
                if self.state == cte.BROADCAST_ACK and packet.type == cte.BROADCAST_DISCOVERY_PACKET:
                    self.state = cte.IDLE_BROADCAST
                    self.predecessor = packet.origin
                    self.retransmission = self.config.n
                    self.broadcast_ack()

                elif self.state == cte.IDLE_BROADCAST and packet.type == cte.ACK_PACKET:
                    self.state = cte.IDLE_PACKET
                    if self.timeout:
                        self.timeout.cancel()
                        self.timeout = ''

                elif packet.type == cte.BROADCAST_ACK_PACKET and self.state == cte.IDLE_FLOODING:
                    neighbor = {
                        'address': packet.origin,
                        'master': packet.flags.master,
                        'file': packet.flags.file
                    }
                    self.neighbors[neighbor.address] = neighbor


    def send_packet(self, packet):
        raise NotImplementedError
