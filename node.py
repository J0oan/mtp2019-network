import threading
from packet import Packet
from transceiver import Transceiver
import cte
import random


class Node(object):
    def __init__(self, config, file):
        self.config = config
        self.state = cte.BROADCAST_FLOODING if config.role == 'tx' else cte.BROADCAST_ACK
        self.packet = Packet(self.config)
        self.transmitter = Transceiver.transmitter()
        self.receiver = Transceiver.receiver()
        self.retransmission = 0
        self.timeout = ''
        self.neighbors = {}
        self.predecessor = ''
        self.file = file
        self.master = False if config.role == 'rx' else True
        self.file_index = 0
        self.successor = ''

        # Initialize timeout
        if self.state == cte.BROADCAST_ACK:
            self.timeout = threading.Timer(self.config.Tout_Broadcast_Receiver, self.end_error)
            self.timeout.start()

        # Initialize radios

    def broadcast_flooding(self):
        if self.retransmission > 0:
            self.state = cte.IDLE_FLOODING
            self.timeout = threading.Timer(self.config.Tout_Broadcast, self.broadcast_flooding)
            discovery_broadcast_packet = self.packet.generate_discovery()
            self.send_packet(discovery_broadcast_packet)
            self.retransmission -= 1
            self.timeout.start()

        else:
            self.state = cte.CHOOSE_RECEIVER if len(self.neighbors) > 0 else cte.COMMUNICATION_OVER
            self.timeout = ''

    def broadcast_ack(self):
        if self.retransmission > 0:
            self.timeout = threading.Timer(self.config.Tout_ACK, self.broadcast_ack)
            flags = {
                "file": False if not self.file else True,
                "master": self.master
            }
            ack_packet = self.packet.generate_ack_discovery(self.predecessor, flags)
            self.send_packet(ack_packet)
            self.retransmission -= 1
            self.timeout.start()

        else:
            self.state = cte.BROADCAST_ACK
            self.timeout = threading.Timer(self.config.Tout_Broadcast_Receiver, self.end_error)
            self.timeout.start()

    def choose_receiver(self):
        possible_successor = list(filter(lambda successor: not successor.file, self.neighbors))
        if len(possible_successor) > 0:
            self.successor = self.neighbors[random.randint(0, len(possible_successor) - 1)].address
            self.state = cte.SEND_PACKET
        else:
            self.state = cte.PASS_TOKEN

    def send_packets(self):
        if self.retransmission > 0:
            self.timeout = threading.Timer(self.config.Tout_ACK, self.send_packets)
            end = True if self.file_index == len(self.file) - 1 else False
            packet = self.packet.generate_data(self.successor, self.file_index, end, self.file[self.file_index])
            self.send_packet(packet)
            self.timeout.start()
            self.state = cte.IDLE_PACKET_ACK
            self.retransmission -= 1

        else:
            del self.neighbors[self.successor]
            self.state = cte.CHOOSE_RECEIVER

    def receive_packets(self):
        packet = self.packet.generate_ack(self.predecessor, self.file_index % 2 - 1, 0)
        self.send_packet(packet)

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
        # TODO merge receiver functions
        if self.receiver.available():
            packet = self.receiver.read()
            packet = self.packet.decapsulate_packet(packet)

            if packet:
                if self.state == cte.BROADCAST_ACK and packet.type == cte.BROADCAST_DISCOVERY_PACKET:
                    self.off_timeout()
                    self.state = cte.IDLE_BROADCAST
                    self.predecessor = packet.origin
                    self.retransmission = self.config.n
                    slot = random.randint(0, self.config.N_slots)
                    back_off = threading.Timer(self.config.T_slot * slot, self.broadcast_ack)
                    back_off.start()

                elif self.state == cte.IDLE_BROADCAST and packet.type == cte.ACK_PACKET:
                    self.off_timeout()
                    self.state = cte.IDLE_PACKET

                elif packet.type == cte.BROADCAST_ACK_PACKET and self.state == cte.IDLE_FLOODING:
                    neighbor = {
                        'address': packet.origin,
                        'master': packet.flags.master,
                        'file': packet.flags.file
                    }
                    self.neighbors[neighbor.address] = neighbor
                    # TODO SEND ACK

                elif self.state == cte.IDLE_PACKET_ACK and packet.type == cte.DATA_ACK_PACKET:
                    # TODO check end of transmission and send last ACK
                    self.off_timeout()
                    self.file_index += 1
                    if self.file_index == len(self.file):
                        self.neighbors[self.successor].file = True
                        self.state = cte.CHOOSE_RECEIVER
                    else:
                        self.state = cte.SEND_PACKET

                elif self.state == cte.IDLE_PACKET and packet.type == cte.DATA_PACKET:
                    if self.file_index % 2 == packet.seqN:
                        self.file[self.file_index] = packet.payload
                        self.file_index += 1
                    self.state = cte.RECEIVE_DATA

    def send_packet(self, packet):
        # TODO send merge transmitter functions
        raise NotImplementedError

    def off_timeout(self):
        if self.timeout:
            self.timeout.cancel()
            self.timeout = ''
