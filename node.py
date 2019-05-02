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
        self.token_successor = ''

        # Set timeout general if receiver before set general error
        if self.state == cte.BROADCAST_ACK:
            self.timeout = threading.Timer(self.config.Tout_Broadcast_Receiver, self.end_error)
            self.timeout.start()

    def broadcast_flooding(self):
        """
        Function to send a broadcast flooding packet
        :return: None
        """
        # Check if retransmissions are reached
        if self.retransmission > 0:
            # set state to wait broadcast ACK, set timeout to next retransmission
            self.state = cte.IDLE_FLOODING
            self.timeout = threading.Timer(self.config.Tout_Broadcast, self.broadcast_flooding)
            # get broadcast packet to send and send it
            discovery_broadcast_packet = self.packet.generate_discovery()
            self.send_packet(discovery_broadcast_packet)
            # reduce retransmission counter and start timeout
            self.retransmission -= 1
            self.timeout.start()

        else:
            # once retransmissions completed check if there are new neighbors and send packet to them
            self.state = cte.CHOOSE_RECEIVER if len(self.neighbors) > 0 else cte.COMMUNICATION_OVER
            # clean timeout
            self.timeout = ''

    def broadcast_ack(self):
        """
        Send broadcast ACK to the transmitter
        :return: None
        """
        # Check if retransmissions are reached
        if self.retransmission > 0:
            # Set timeout to retransmit broadcast ACK
            self.timeout = threading.Timer(self.config.Tout_ACK, self.broadcast_ack)
            # Set flags to send in the ACK
            flags = {
                "file": False if not self.file else True,
                "master": self.master
            }
            # Create packet in bytes to transmit and send packet
            # TODO review LPC of function generate_ack_discovery
            ack_packet = self.packet.generate_ack_discovery(self.predecessor, flags.file, flags.master)
            self.send_packet(ack_packet)
            # Discount retransmission and start timeout
            self.retransmission -= 1
            self.timeout.start()

        else:
            # retransmissions reached, transmitter considered death set state to wait broadcast discovery packet
            self.state = cte.BROADCAST_ACK
            # Set and start timeout general of receiver before set general error
            self.timeout = threading.Timer(self.config.Tout_Broadcast_Receiver, self.end_error)
            self.timeout.start()

    def receive_packets(self):
        """
        Function to send data packet ACK
        :return:
        """
        # TODO implement check in reception of end of file to send ack
        packet = self.packet.generate_ack(self.predecessor, self.file_index % 2 - 1, 0)
        self.send_packet(packet)

    def choose_receiver(self):
        """
        Function to select a random receiver to send the data
        :return: None
        """
        # Filter neighbors that not have file
        possible_successor = list(filter(lambda successor: not successor.file, self.neighbors))
        # check if there is a possible successor
        if len(possible_successor) > 0:
            # Get a random one and set state to send dataa
            self.successor = self.neighbors[random.randint(0, len(possible_successor) - 1)].address
            self.state = cte.SEND_PACKET
        else:
            # If there is not successor pass token
            self.state = cte.CHOOSE_TOKEN

    def send_packets(self):
        """
        Function to send a frame of data to the successor
        :return: None
        """
        # Check if retransmissions are reached
        if self.retransmission > 0:
            # Set timeout of the next data frame to sent
            self.timeout = threading.Timer(self.config.Tout_ACK, self.send_packets)
            # Check if this frame is the last one and generate the data packet to send
            end = True if self.file_index == len(self.file) - 1 else False
            packet = self.packet.generate_data(self.successor, self.file_index, end, self.file[self.file_index])
            # Send packet and start timeout
            self.send_packet(packet)
            self.timeout.start()
            # Set state to wait ack for the data packet and reduce number of retransmissions
            self.state = cte.IDLE_PACKET_ACK
            self.retransmission -= 1

        else:
            # If number of retransmission of data packet is reached the successor
            # Is considered death and deleted from the list of neighbors
            del self.neighbors[self.successor]
            # Restart choose receiver process
            self.state = cte.CHOOSE_RECEIVER

    def wait_token(self):
        """
        # TODO explain function
        :return:
        """
        token_buffer = []
        radio_rx.read(token_buffer_buffer, radio.getDynamicPayloadSize())
        packet = ''.join(chr(x) for x in token_buffer)
        type_packet = unpacketack(packet)
        if type_packet is TOKEN_PACKET:
            node.state = cte.BROADCAST_FLOODING
        elif type_packet is DISCOVERY_BROADCAST:
            node.state = cte.BROADCAST_FLOODING

    def return_token(self):
        """
        # TODO decidir como detectar any_active_predecessor y ver si se puede combinar en esta misma funcion
        # puede haber diferentes predecessors?
        :return:
        """
        if not self.predecessor:
            self.state = cte.END
        elif not self.any_active_predecessor():
            self.state = cte.END
        else:
            if self.retransmission > 0:
                self.timeout = threading.Timer(self.config.Tout_ACK, self.pass_token())
                token = self.packet.generate_token_frame(self.token_predecessor)
                self.send_packet(token)
                self.timeout.start()
                self.state = cte.IDLE_TOKEN_ACK
                self.retransmission -= 1

    def choose_token_successor(self):
        """
        Function to select a random receiver to send the token
        :return: None
        """
        # Filter the neighbors list and get a node without token and data received from this node
        possible_successor_token = list(
            filter(lambda successor: not successor.master and not successor.file_a_priori, self.neighbors))
        if len(possible_successor_token) > 0:
            # If there are some possible successor, choose randomly one and set state to pass token
            self.successor = self.neighbors[random.randint(0, len(possible_successor_token) - 1)].address
            self.state = cte.PASS_TOKEN
        else:
            # If all the nodes that this node passed the data to, have had the token, get the rest that haven't
            possible_successor_token = list(filter(lambda successor: not successor.master, self.neighbors))
            if len(possible_successor_token) > 0:
                # If there are some possible successor, choose randomly one and set state to pass token
                self.successor = self.neighbors[random.randint(0, len(possible_successor_token) - 1)].address
                self.state = cte.PASS_TOKEN
            else:
                # If there are not more possible successor, set state communication is over
                self.state = cte.COMMUNICATION_OVER

    def pass_token(self):
        """
        Function to process the transmission of the token between nodes
        :return: None
        """
        # Check if retransmissions are reached
        if self.retransmission > 0:
            # Set timeout for retransmission of token
            self.timeout = threading.Timer(self.config.Tout_ACK, self.pass_token)
            # Get token packet and send it
            token = self.packet.generate_token_frame(self.token_successor)
            # TODO is it necessary to have token_successor?
            self.send_packet(token)
            # Start timeout and set state to wait token ack
            self.timeout.start()
            self.state = cte.IDLE_TOKEN_ACK
            self.retransmission -= 1

        else:
            # If number of retransmission of token is reached the successor
            # Is considered death and deleted from the list of neighbors
            del self.neighbors[self.token_successor]
            # Set state again to choose another successor for the token
            self.state = cte.CHOOSE_TOKEN

    def send_end(self):
        """
        Function to pass to the neighbours an end of protocol packet
        :return: None
        """
        # TODO send end of protocol packet

    def end_error(self):
        """
        Function to set the end state when some error happens that block the system
        :return:
        """
        self.state = cte.ERROR_END

    def check_receiver(self):
        """
        Check if there is packet in the receiver buffer, decapsulate, check crc and destination.
        And do anything related with it.
        :return: None
        """
        # TODO merge receiver functions
        # Check buffer
        if self.receiver.available():
            # Read buffer if there is something
            packet = self.receiver.read()
            # Decapsulate received bytes and get Packet Object
            packet = self.packet.decapsulate_packet(packet)

            # Check if decapsulated packet is correct
            if packet:

                # Case waiting to Broadcast Discovery and received Broadcast Discovery Packet
                if self.state == cte.BROADCAST_ACK and packet.type == cte.DISCOVERY_BROADCAST:
                    # Stop timeout of ACK Broadcast retransmission
                    self.off_timeout()
                    # Set State to wait end handshake, set predecessor, set retransmissions of ACK
                    self.state = cte.IDLE_BROADCAST
                    self.predecessor = packet.origin
                    self.retransmission = self.config.n

                    # Get a random slot within the range of slots from config
                    slot = random.randint(0, self.config.N_slots)
                    # Set and start timeout of back off according to slot and time slot from config.
                    back_off = threading.Timer(self.config.T_slot * slot, self.broadcast_ack)
                    back_off.start()

                # Case waiting to ACK end handshake Discovery and received ACK handshake
                elif self.state == cte.IDLE_BROADCAST and packet.type == cte.ACK_ACKDISCOVERY:
                    # Stop timeout of ACK Broadcast and set state to wait for data packet
                    self.off_timeout()
                    self.state = cte.IDLE_PACKET

                # Case sent Broadcast discovery, waiting Discovery ACK and received Discovery ACK
                elif packet.type == cte.ACK_DISCOVERY and self.state == cte.IDLE_FLOODING:
                    # Create neighbor from data received
                    neighbor = {
                        'address': packet.origin,
                        'master': packet.flags.master,
                        'file': packet.flags.file,
                        'file_a_priory': packet.flags.file
                    }
                    # Add neighbor to list
                    self.neighbors[neighbor.address] = neighbor
                    # TODO SEND ACK

                # Case waiting data packet ack and received data packet ack
                elif self.state == cte.IDLE_PACKET_ACK and packet.type == cte.ACK_PACKET:
                    # Stop timeout for retransmit data packet
                    self.off_timeout()
                    # Set file index to next packet
                    self.file_index += 1
                    # if previous packet was the last packet send ack and get another receiver
                    # else send next packet
                    if self.file_index == len(self.file):
                        # TODO send ack
                        self.neighbors[self.successor].file = True
                        self.state = cte.CHOOSE_RECEIVER
                    else:
                        self.state = cte.SEND_PACKET

                # Case waiting data packet and data packet received
                elif self.state == cte.IDLE_PACKET and packet.type == cte.DATA_PACKET:
                    # Check seq number to know if it is a retransmission or a new packet
                    if self.file_index % 2 == packet.seqN:
                        self.file[self.file_index] = packet.payload
                        self.file_index += 1
                    # Send ACK
                    self.state = cte.RECEIVE_DATA

                # TODO IDLE_TOKEN_ACK received token ack and send ACK
                # TODO wait token and wait token ack
                # TODO received end of protocol packet

    def send_packet(self, packet):
        """
        Function to send a packet through the transmitter
        :param packet: in bytes to transmit
        :return: None
        """
        # TODO merge transmitter functions
        raise NotImplementedError

    def off_timeout(self):
        """
        Function to turn off the timeout
        :return: None
        """
        # First check if there is an active timeout
        if self.timeout:
            # Cancel it and clean it
            self.timeout.cancel()
            self.timeout = ''
