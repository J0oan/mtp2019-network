import cte


class Packet(object):
    def __init__(self, config):
        self.config = config
        self.origin = self.config.address

    def generate_discovery(self):
        """
        Generar paquete Discovery y delvover array de bytes
        :return:
        """
        chunk = (0xf << 4) | (self.origin & 0xf)         # Destination address Broadcast| source
        packet = bytes([chunk])                    # Transform to bytes
        # SN = 0 | PT = 000 | Flags = 0000
        packet += (b'\x00')
        return packet

    def generate_ack_discovery(self, destination, flag1, flag2):
        """
        Generar paquete ACK-Discovery y delvover array de bytes
        :param destination:
        :param flag1: Has file
        :param flag2: Has been master
        :return:
        """
        chunk = ((destination & 0xf) << 4) | (self.origin & 0xf)         # Destination address Broadcast| source
        # Transform to bytes
        packet = bytes([chunk])
        chunk = (0x1 << 4) | (flag1 & 0x1) << 1 | (flag2 & 0x1)     # SN = 0| PT = 001 | Flags = (0 0 flag1 flag2)
        packet += bytes([chunk])
        return packet

    def generate_data(self, destination, seqN, end, payload):
        """
        Generar paquete ACK-Discovery y delvover array de bytes
        :param destination:
        :param seqN:
        :param end:
        :param payload: type bytes
        :return:
        """
        chunk = ((destination & 0xf) << 4) | (self.origin & 0xf)         # Destination address Broadcast| source
        # Transform to bytes
        packet = bytes([chunk])
        chunk = (seqN & 0x1) << 7 | (0b010 << 4) | (end & 0x1)      # SN = seqN | PT = 010 | Flags = (0 0 0 end)
        packet += bytes([chunk])
        packet += payload
        return packet

    def generate_ack(self, destination, seqN, LPC):
        """
        Generar paquete ACK y delvover array de bytes
        :param destination:
        :param seqN:
        :param type:
        :return:
        """
        chunk = ((destination & 0xf) << 4) | (self.origin & 0xf)         # Destination address Broadcast| source
        # Transform to bytes
        packet = bytes([chunk])
        # SN = seqN | PT = 011 | Flags = 000 + LPC
        chunk = (seqN & 0x1) << 7 | (0b011 << 4) | (LPC & 0x1)
        packet += bytes([chunk])
        return packet

    def generate_token_frame(self, destination):
        """
        Generar paquete tokenFrame y delvover array de bytes
        :param destination:
        :return:
        """
        chunk = ((destination & 0xf) << 4) | (self.origin & 0xf)             # Destination address Broadcast| source
        # Transform to bytes
        packet = bytes([chunk])
        # SN = 0 | PT = 100 | Flags = 0000
        chunk = (0b100 << 4)
        packet += bytes([chunk])
        return packet

    def generate_ack_token_frame(self, destination):
        """
        Generar paquete AckTokenFrame y delvover array de bytes
        :param destination:
        :return:
        """
        chunk = ((destination & 0xf) << 4) | (self.origin & 0xf)         # Destination address Broadcast| source
        # Transform to bytes
        packet = bytes([chunk])
        # SN = 0 | PT = 110 | Flags = 0000
        chunk = (0b110 << 4)
        packet += bytes([chunk])
        return packet

    def end_protocol(self):
        """
        :return:
        """
        chunk = (0xf << 4) | (self.origin & 0xf)                         # Destination address Broadcast| source
        # Transform to bytes
        packet = bytes([chunk])
        # SN = 0 | PT = 101 | Flags = 0000
        chunk = (0b101 << 4)
        packet += bytes([chunk])
        return packet

    def decapsulate_packet(self, packet):
        # Packet Length
        pktlength = packet.length()
        # Source
        source = (packet[0] & 0x0f)
        # Destination
        destination = ((packet[0] & 0xf0) >> 4)

        if (destination != self.origin) & (destination != 0x0f):           # Drop the packet if I'm not the destination or not Broadcast
            return False
        # Packet Type
        PT = ((packet[1] & 0x70) >> 4)

        if PT == 0:                                                          # If 0 Discovery Broadcast
            return {"origin": source, "type": cte.DISCOVERY_BROADCAST}

        elif PT==1:                                                          # If 1 ACK Discovery
            flag1 = ((packet[1] & 0x02) >> 1)
            flag2 = (packet[1] & 0x01)
            return {"origin": source, "type": cte.ACK_DISCOVERY, "flag1": flag1, "flag2": flag2}    # Return Ack Discovery info

        elif PT==2:                                                           # If 2 Data Packet
            # TODO shouldn't be a end of file field
            secN = ((packet[1] & 0x80) >> 7)
            eot = (packet[1] & 0x01)                                          # Final data packet
            payload = packet[2:pktlength-2]
            return {"origin": source, "type": cte.DATA_PACKET, "secN": secN, "payload": payload,  "eot": eot}

        elif PT==3:                                                           # If 3 ACK Data Packet
            secN = ((packet[1] & 0x80) >> 7)
            if (packet[1] & 0x02) >> 1: # Check LPC                           # IF LPC == 1 Final ACK
                return {"origin": source, "type": cte.ACK_ACKPACKET}
            else:
                return {"origin": source, "type": cte.ACK_PACKET, "secN": secN}

        elif PT==4:                                                            # Token packet
            return {"origin": source, "type": cte.TOKEN_PACKET}

        elif PT==6:                                                            # ACK Token
            return {"origin": source, "type": cte.ACK_TOKEN}

        elif PT==5:                                                            # END of transmission
            return {"origin": source, "type": cte.END_OF_TX}


