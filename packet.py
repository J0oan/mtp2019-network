from . import cte


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
        packet += b'\x00'
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

    def generate_data(self, destination, seq_number, end, payload):
        """
        Generar paquete ACK-Discovery y delvover array de bytes
        :param destination:
        :param seq_number:
        :param end:
        :param payload: type bytes,
        :return:
        """
        chunk = ((destination & 0xf) << 4) | (self.origin & 0xf)      # Destination address Broadcast| source
        # Transform to bytes
        packet = bytes([chunk])
        chunk = (seq_number & 0x1) << 7 | (0b010 << 4) | (end & 0x1)  # SN = seq_number | PT = 010 | Flags = (0 0 0 end)
        packet += bytes([chunk])
        packet += payload
        return packet

    def generate_ack(self, destination, seq_number, lpc):
        """
        Generar paquete ACK y delvover array de bytes
        :param destination:
        :param seq_number:
        :param lpc:
        :return:
        """
        chunk = ((destination & 0xf) << 4) | (self.origin & 0xf)         # Destination address Broadcast| source
        # Transform to bytes
        packet = bytes([chunk])
        # SN = seq_number | PT = 011 | Flags = 000 + lpc
        chunk = (seq_number & 0x1) << 7 | (0b011 << 4) | (lpc & 0x1)
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
        packet_length = len(packet)
        # Source
        source = (packet[0] & 0x0f)
        # Destination
        destination = ((packet[0] & 0xf0) >> 4)

        # Drop the packet if I'm not the destination or not Broadcast
        if (destination != self.origin) & (destination != 0x0f):
            return False
        # Packet Type
        pt = ((packet[1] & 0x70) >> 4)

        if pt == 0:                                                          # If 0 Discovery Broadcast
            return {"origin": source, "type": cte.DISCOVERY_BROADCAST}

        elif pt == 1:                                                          # If 1 ACK Discovery
            flag1 = True if ((packet[1] & 0x02) >> 1) else False
            flag2 = True if (packet[1] & 0x01) else False
            # Return Ack Discovery info
            return {"origin": source, "type": cte.ACK_DISCOVERY, "file": flag1, "master": flag2}

        elif pt == 2:                                                           # If 2 Data Packet
            sec_n = ((packet[1] & 0x80) >> 7)
            eot = (packet[1] & 0x01)                                          # Final data packet
            payload = packet[2:packet_length]
            return {"origin": source, "type": cte.DATA_PACKET, "sec_n": sec_n, "payload": payload,  "eot": eot}

        elif pt == 3:                                                           # If 3 ACK Data Packet
            sec_n = ((packet[1] & 0x80) >> 7)
            return {"origin": source, "type": cte.ACK_PACKET, "sec_n": sec_n}

        elif pt == 4:                                                            # Token packet
            return {"origin": source, "type": cte.TOKEN_PACKET}

        elif pt == 6:                                                            # ACK Token
            return {"origin": source, "type": cte.ACK_TOKEN}

        elif pt == 5:                                                            # END of transmission
            return {"origin": source, "type": cte.END_OF_TX}
