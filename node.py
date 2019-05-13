import threading
from .packet import Packet
from .transceiver import Transceiver
from . import cte
import random


class Node:
    def __init__(self, config, file, role):
        self.config = config
        self.state = cte.BROADCAST_FLOODING if role == 'tx' else cte.BROADCAST_ACK
        self.last_state = None
        self.packet = Packet(self.config)
        self.transmitter = Transceiver.transmitter(config)
        self.receiver = Transceiver.receiver(config)
        self.retransmission = 0
        self.timeout = None
        self.timeout_general = None
        self.neighbors = {}
        self.predecessor = None
        self.file = file
        self.master = True if role == 'tx' else False
        self.file_index = 0
        self.eot = 0
        self.successor = None

        # Set tx and rx channels
        if role == 'tx':
            self.transmitter.change_channel(self.config.Channel_master)
            self.receiver.change_channel(self.config.Channel_slave)
        else:
            self.receiver.change_channel(self.config.Channel_master)
            self.transmitter.change_channel(self.config.Channel_slave)

        # Set timeout general if receiver before set general error
        if self.state == cte.BROADCAST_ACK:
            self.timeout_general = threading.Timer(self.config.Tout_EOP, self.end_error)
            self.timeout_general.start()

    def broadcast_flooding(self):
        """
        Function to send a broadcast flooding packet
        :return: None
        """
        # Check if retransmissions are reached
        if self.retransmission > 0:
            # set state to wait broadcast ACK, set timeout to next retransmission
            self.state = cte.IDLE_FLOODING
            self.timeout = threading.Timer(self.config.Tout_Discovery, self.broadcast_flooding)
            # get broadcast packet to send and send it
            discovery_broadcast_packet = self.packet.generate_discovery()
            self.send_packet(discovery_broadcast_packet)
            # reduce retransmission counter and start timeout
            self.retransmission -= 1
            self.timeout.start()

        else:
            # once retransmissions completed check if there are new neighbors and send packet to them
            self.state = cte.CHOOSE_RECEIVER if len(self.neighbors) > 0 else cte.RETURN_TOKEN
            # clean timeout
            self.off_timeout()

    def receive_broadcast_discovery(self, _predecessor=None, _last_state=None):
        """
        Corresponding actions after receiving broadcast discovery packet
        :return:
        """
        # Stop timeout of ACK Broadcast retransmission
        self.off_timeout_general()

        predecessor = _predecessor if _predecessor else self.predecessor
        self.last_state = _last_state
        # Set State to wait end handshake set retransmissions of ACK
        self.state = cte.IDLE_BROADCAST
        self.retransmission = self.config.nDiscovery_ACK

        # Get a random slot within the range of slots from config
        slot = random.randint(0, self.config.N_slots)
        # Set and start timeout of back off according to slot and time slot from config.
        back_off = threading.Timer(self.config.T_slot * slot, self.broadcast_ack, [predecessor])
        back_off.start()

    def broadcast_ack(self, _predecessor=None):
        """
        Send broadcast ACK to the transmitter
        :return: None
        """
        predecessor = _predecessor if _predecessor else self.predecessor
        # Check if retransmissions are reached
        if self.retransmission > 0:
            # Set timeout to retransmit broadcast ACK
            self.timeout = threading.Timer(self.config.Tout_Discovery_ACK, self.broadcast_ack, [predecessor])
            # Set flags to send in the ACK
            flags = {
                "file": False if not self.file else True,
                "master": self.master
            }
            # Create packet in bytes to transmit and send packet
            ack_packet = self.packet.generate_ack_discovery(self.predecessor, flags['file'], flags['master'])
            self.send_packet(ack_packet)
            # Discount retransmission and start timeout
            self.retransmission -= 1
            self.timeout.start()

        else:
            self.off_timeout()
            # retransmissions reached, transmitter considered death set state to wait broadcast discovery packet
            self.state = self.last_state if self.last_state else cte.BROADCAST_ACK
            # Set and start timeout general of receiver before set general error
            self.timeout_general = threading.Timer(self.config.Tout_EOP, self.end_error)
            self.timeout_general.start()

    def choose_receiver(self):
        """
        Function to select a random receiver to send the data
        :return: None
        """
        # Filter neighbors that not have file
        possible_successor = list(filter(lambda successor: not successor['file'], self.neighbors))
        # check if there is a possible successor
        if len(possible_successor) > 0:
            # Get a random one and set state to send dataa
            self.successor = self.neighbors[random.randint(0, len(possible_successor) - 1)]['address']
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
            self.timeout = threading.Timer(self.config.Tout_Data_ACK, self.send_packets)
            # Check if this frame is the last one and generate the data packet to send
            end = True if self.file_index == len(self.file) - 1 else False
            packet = self.packet.generate_data(self.successor, self.file_index % 2, end, self.file[self.file_index])
            # Send packet and start timeout
            self.send_packet(packet)
            self.timeout.start()
            # Set state to wait ack for the data packet and reduce number of retransmissions
            self.state = cte.IDLE_PACKET_ACK
            self.retransmission -= 1

        else:
            self.off_timeout()
            # If number of retransmission of data packet is reached the successor
            # Is considered death and deleted from the list of neighbors
            del self.neighbors[self.successor]
            # Restart choose receiver process
            self.state = cte.CHOOSE_RECEIVER

    def receive_packets(self):
        """
        Function to send data packet ACK
        :return:
        """

        if not self.eot:
            # get ack and send it
            packet = self.packet.generate_ack(self.predecessor, (self.file_index - 1) % 2, 0)
            self.send_packet(packet)
            # set state to wait next data packet
            self.state = cte.IDLE_PACKET
            # Re-start general timeout for waiting to receive a new data frame
            self.timeout_general = threading.Timer(self.config.Tout_Data, self.error_tout_data)
            self.timeout_general.start()

        else:
            # get last ACK and send it
            packet = self.packet.generate_ack(self.predecessor, (self.file_index - 1) % 2, 1)
            self.send_packet(packet)
            # Set state to wait packet
            self.state = cte.PULP
            # Save File
            self.write_file()
            self.timeout_general = threading.Timer(self.config.Tout_EOP, self.end_error)
            self.timeout_general.start()

    def choose_token_successor(self):
        """
        Function to select a random receiver to send the token
        :return: None
        """
        # Filter the neighbors list and get a node without token and data received from this node
        possible_successor_token = list(
            filter(lambda successor: not successor['master'] and not successor['file_a_priori'], self.neighbors))
        if len(possible_successor_token) > 0:
            # If there are some possible successor, choose randomly one and set state to pass token
            self.successor = self.neighbors[random.randint(0, len(possible_successor_token) - 1)]['address']
            self.state = cte.PASS_TOKEN
        else:
            # If all the nodes that this node passed the data to, have had the token, get the rest that haven't
            possible_successor_token = list(filter(lambda successor: not successor['master'], self.neighbors))
            if len(possible_successor_token) > 0:
                # If there are some possible successor, choose randomly one and set state to pass token
                self.successor = self.neighbors[random.randint(0, len(possible_successor_token) - 1)]['address']
                self.state = cte.PASS_TOKEN
            else:
                # If there are not more possible successor, set state communication is over
                self.state = cte.RETURN_TOKEN

    def pass_token(self):
        """
        Function to process the transmission of the token between nodes
        :return: None
        """
        # Check if retransmissions are reached
        if self.retransmission > 0:
            # Set timeout for retransmission of token
            self.timeout_general = threading.Timer(self.config.Tout_Token, self.pass_token)
            # Get token packet and send it
            token = self.packet.generate_token_frame(self.successor)
            self.state = cte.IDLE_TOKEN_ACK
            self.receiver.change_channel(self.config.Channel_master)
            self.retransmission -= 1
            self.send_packet(token)
            # Start timeout and set state to wait token ack
            self.timeout_general.start()

        else:
            self.off_timeout_general()
            # If number of retransmission of token is reached the successor
            # Is considered death and deleted from the list of neighbors
            del self.neighbors[self.successor]
            # Set state again to choose another successor for the token
            self.state = cte.CHOOSE_TOKEN

    def return_token(self):
        """

        :return:
        """
        if not self.predecessor or self.retransmission == 0:
            self.retransmission = self.config.nEnd
            self.state = cte.END
        else:
            self.timeout_general = threading.Timer(self.config.Tout_Token, self.return_token)
            token = self.packet.generate_token_frame(self.predecessor)
            self.state = cte.IDLE_TOKEN_ACK
            self.receiver.change_channel(self.config.Channel_master)
            self.retransmission -= 1
            self.send_packet(token)
            # Start timeout and set state to wait token ack
            self.timeout_general.start()

    def token_ack(self):
        """
        Send ACK token to updated predecessor
        :return:
        """
        # Generate ACK packet for token acknowledgment
        packet_ack = self.packet.generate_ack_token_frame(self.predecessor)
        self.send_packet(packet_ack)
        self.state = cte.PULP
        self.timeout_general = threading.Timer(self.config.Tout_EOP, self.end_error)
        self.timeout_general.start()

    def receive_token(self, origin):
        """
        Send ACK token to updated predecessor
        :return:
        """

        # set state to wait broadcast ACK, set timeout to next retransmission
        self.timeout = threading.Timer(self.config.Tout_Token_ACK, self.receive_token, [origin])
        self.transmitter.change_channel(self.config.Channel_master)
        self.receiver.change_channel(self.config.Channel_slave)
        # Generate ACK packet for token acknowledgment and send it
        packet_ack = self.packet.generate_ack_token_frame(origin)
        self.send_packet(packet_ack)
        self.timeout.start()
        # Set State to wait end of handshake
        self.state = cte.WAIT_ACK_TOKEN_CONF

    def send_end(self):
        """
        Function to pass to the neighbours an end of protocol packet
        :return: None
        """
        if self.retransmission > 0:
            packet = self.packet.end_protocol()
            self.send_packet(packet)
            self.retransmission -= 1
        else:
            self.transmitter.powerDown()
            self.receiver.powerDown()
            self.state = cte.OFF

    def error_tout_data(self):
        """
        Function to set the end state when Tout_Data expires
        :return:
        """
        self.state = cte.BROADCAST_ACK

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
        # Check buffer
        if self.receiver.available():
            # Read buffer if there is something
            packet = self.read_packet()
            # Decapsulate received bytes and get Packet Object
            packet = self.packet.decapsulate_packet(packet)

            # Check if decapsulated packet is correct
            if packet:
                # Case received Broadcast Discovery Packet
                if packet['type'] == cte.DISCOVERY_BROADCAST:
                    # waiting to Broadcast Discovery
                    if self.state == cte.BROADCAST_ACK:
                        # Set predecessor
                        self.predecessor = packet['origin']
                        # Send corresponding ACKs to predecessor
                        self.receive_broadcast_discovery()
                    # Waiting to Token
                    elif self.state == cte.PULP:
                        # Send corresponding ACKs
                        self.receive_broadcast_discovery(packet['origin'], self.state)

                # Case sent Broadcast discovery, waiting Discovery ACK and received Discovery ACK
                elif packet['type'] == cte.ACK_DISCOVERY:
                    if self.state == cte.IDLE_FLOODING:
                        # Create neighbor from data received
                        neighbor = {
                            'address': packet['origin'],
                            'master': packet['master'],
                            'file': packet['file'],
                            'file_a_priory': self.neighbors[packet['origin']]['file_a_priory']
                            if packet['origin'] in self.neighbors else packet['file']
                        }
                        # Add neighbor to list
                        self.neighbors[neighbor["address"]] = neighbor
                        # Send Discovery-ACK
                        packet = self.packet.generate_ack_discovery(neighbor["address"], True, True)
                        self.send_packet(packet)

                    # Case waiting to ACK end handshake Discovery and received ACK handshake
                    elif self.state == cte.IDLE_BROADCAST:
                        # Stop timeout of ACK Broadcast and set state to wait for data packet
                        self.off_timeout()
                        self.state = self.last_state if self.last_state else cte.IDLE_PACKET
                        # Set timeout for waiting data packets and start it
                        if self.state == cte.IDLE_PACKET:
                            self.timeout_general = threading.Timer(self.config.Tout_Data, self.error_tout_data)
                        else:
                            self.timeout_general = threading.Timer(self.config.Tout_EOP, self.end_error)
                        self.timeout_general.start()

                # Case waiting data packet ack and received data packet ack
                elif packet['type'] == cte.ACK_PACKET and self.state == cte.IDLE_PACKET_ACK:
                    # Stop timeout for retransmit data packet
                    self.off_timeout()
                    # Set file index to next packet
                    self.file_index += 1
                    # if previous packet was the last packet send ack and get another receiver
                    # else send next packet
                    if self.file_index == len(self.file):
                        self.neighbors[self.successor]['file'] = True
                        self.state = cte.CHOOSE_RECEIVER
                    else:
                        self.state = cte.SEND_PACKET

                # Case waiting data packet and data packet received
                elif packet['type'] == cte.DATA_PACKET:
                    self.off_timeout_general()
                    if self.state == cte.IDLE_PACKET:
                        # Check seq number to know if it is a retransmission or a new packet
                        if self.file_index % 2 == packet['sec_n']:
                            if not self.file:
                                self.file = list()
                            self.file.append(packet['payload'])
                            self.file_index += 1
                            self.eot = packet['eot']
                        # Send ACK
                        self.state = cte.RECEIVE_DATA

                    # Case waiting Token and receiving last data packet
                    elif self.state == cte.PULP:
                        # get last ACK and send it
                        packet = self.packet.generate_ack(self.predecessor, (self.file_index - 1) % 2, 1)
                        self.send_packet(packet)
                        self.timeout_general = threading.Timer(self.config.Tout_EOP, self.end_error)
                        self.timeout_general.start()

                # Case waiting Token and receive the Token packet
                elif packet['type'] == cte.TOKEN_PACKET:
                    # self.state == cte.PULP and self.state == cte.WAIT_ACK_TOKEN_CONF
                    self.off_timeout_general()
                    if packet['origin'] != self.successor:
                        # Update predecessor as may not be the same that sent the data file
                        self.predecessor = packet['origin']
                    # Set state to receive the token
                    self.receive_token(packet['origin'])

                # Case waiting Token and receiving Token-ACK
                elif packet['type'] == cte.ACK_TOKEN:
                    # Case waiting end of Token Handshake from master and receiving correct Token ACK
                    if self.state == cte.WAIT_ACK_TOKEN_CONF:
                        self.off_timeout()
                        # Set state to broadcast flooding to discover neighbors
                        self.master = True
                        self.state = cte.BROADCAST_FLOODING
                    # state == PULP or WAIT_END or IDLE_TOKEN_ACK
                    elif self.state == cte.PULP or self.state == cte.IDLE_TOKEN_ACK:
                        self.off_timeout_general()
                        if self.state == cte.IDLE_TOKEN_ACK:
                            self.transmitter.change_channel(self.config.Channel_slave)
                        self.token_ack()

                # Case waiting Token and receive End of Tx packet
                elif packet['type'] == cte.END_OF_TX and self.state == cte.PULP:
                    self.off_timeout_general()
                    # Set state to end communication
                    self.retransmission = self.config.nEnd
                    self.state = cte.END
                    self.receiver.change_channel(self.config.Channel_slave)
                    self.transmitter.change_channel(self.config.Channel_master)

    def send_packet(self, packet):
        """
        Function to send a packet through the transmitter
        :param packet: in bytes to transmit
        :return: None
        """
        self.transmitter.write(packet)

    def read_packet(self):
        """

        :return:
        """
        length = self.receiver.getDynamicPayloadSize()
        return self.receiver.read(length)

    def off_timeout(self):
        """
        Function to turn off the timeout
        :return: None
        """
        # First check if there is an active timeout
        if self.timeout:
            # Cancel it and clean it
            self.timeout.cancel()
            self.timeout = None

    def off_timeout_general(self):
        """
        Function to turn off the timeout
        :return: None
        """
        # First check if there is an active timeout
        if self.timeout_general:
            # Cancel it and clean it
            self.timeout_general.cancel()
            self.timeout_general = None

    def write_file(self):
        """
        Function that stores the file
        :return:
        """
        with open(self.config.File_Path_Output, "wb") as f:
            for chunk in self.file:
                f.write(chunk)
