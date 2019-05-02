# Clase paquete
import crc16
import cte


class Packet(object):
    def __init__(self, config):
        self.config = config
        self.origin = self.config.address

    def generate_discovery(self):
        """
        Generar paquete Discovery con CRC y delvover array de bytes
        :return:
        """
        chunk = (0xf << 4) | (self.origin &
                              0xf)         # Destination address Broadcast| source
        packet = bytes([chunk])                    # Transform to bytes
        # SN = 0 | PT = 000 | Idle = 0000
        packet += (b'\x00')
        packet += crc16.crc16xmodem(packet)           # 16 bit crc
        return packet

    def generate_ack_discovery(self, destination, LPC, flag1, flag2):
        """+
        Generar paquete ACK-Discovery con CRC y delvover array de bytes
        :param destination:
        :param LPC: Last ack flag
        :param flags1: Has file
        :param flags2: Has been master
        :return:
        """
        chunk = ((destination & 0xf) << 4) | (self.origin &
                                              0xf)         # Destination address Broadcast| source
        # Transform to bytes
        packet = bytes([chunk])
        chunk = (0x1 << 4) | (LPC & 0x1) << 2 | (flag1 & 0x1) << 1 | (flag2 & 0x1)     # SN = 0| PT = 001 | (0 0 flag1 flag2)
        packet += bytes([chunk])
        # 16 bit crc
        packet += crc16.crc16xmodem(packet)
        return packet

    def generate_data(self, destination, seqN, end, payload):
        """
        Generar paquete ACK-Discovery con CRC y delvover array de bytes
        :param destination:
        :param seqN:
        :param end:
        :param payload: type bytes
        :return:
        """
        chunk = ((destination & 0xf) << 4) | (self.origin & 0xf)         # Destination address Broadcast| source
        # Transform to bytes
        packet = bytes([chunk])
        chunk = (seqN & 0x1) << 7 | (0b010 << 4) | (end & 0x1)      # SN = seqN | PT = 010 | (0 0 0 end)
        packet += bytes([chunk])
        packet += payload
        # 16 bit crc
        packet += crc16.crc16xmodem(packet)
        return packet

    def generate_ack(self, destination, seqN, LPC):
        """
        Generar paquete ACK con CRC y delvover array de bytes
        :param destination:
        :param seqN:
        :param type:
        :return:
        """
        chunk = ((destination & 0xf) << 4) | (self.origin & 0xf)         # Destination address Broadcast| source
        # Transform to bytes
        packet = bytes([chunk])
        # SN = seqN | PT = 011 | idle = 0000
        chunk = (seqN & 0x1) << 7 | (0b011 << 4) | (LPC & 0x1) << 1
        packet += bytes([chunk])
        # 16 bit crc
        packet += crc16.crc16xmodem(packet)
        return packet

    def generate_token_frame(self, destination):
        """
        Generar paquete tokenFrame con CRC y delvover array de bytes
        :param destination:
        :return:
        """
        chunk = ((destination & 0xf) << 4) | (self.origin & 0xf)             # Destination address Broadcast| source
        # Transform to bytes
        packet = bytes([chunk])
        # SN = 0 | PT = 100 | idle = 0000
        chunk = (0b100 << 4)
        packet += bytes([chunk])
        # 16 bit crc
        packet += crc16.crc16xmodem(packet)
        return packet

    def generate_ack_token_frame(self, destination):
        """
        Generar paquete AckTokenFrame con CRC y delvover array de bytes
        :param destination:
        :return:
        """
        chunk = ((destination & 0xf) << 4) | (self.origin & 0xf)         # Destination address Broadcast| source
        # Transform to bytes
        packet = bytes([chunk])
        # SN = 0 | PT = 110 | idle = 0000
        chunk = (0b110 << 4)
        packet += bytes([chunk])
        # 16 bit crc
        packet += crc16.crc16xmodem(packet)
        return packet

    def end_protocol(self):
        """
        :return:
        """
        chunk = (0xf << 4) | (self.origin & 0xf)                         # Destination address Broadcast| source
        # Transform to bytes
        packet = bytes([chunk])
        # SN = 0 | PT = 101 | idle = 0000
        chunk = (0b101 << 4)
        packet += bytes([chunk])
        # 16 bit crc
        packet += crc16.crc16xmodem(packet)
        return packet

    def decapsulate_packet(self, packet):
        pktlength = packet.length()
        CRC_packet = packet[pktlength-1:pktlength]

        #check CRC
        CRC_calculated = crc16.crc16xmodem(packet[0,pktlength-2])

        if CRC_calculated == CRC_packet:#process packet:

            source = (packet[0] & 0x0f)
            destination = ((packet[0] & 0xf0) >> 4)
            if (destination != self.origin) & (destination != 0x0f):
                return False

            PT = ((packet[1] & 0x70) >> 4)

            if PT == 0:
                return {origin: source, type: cte.DISCOVERY_BROADCAST}

            elif PT==1:
                flag1 = ((packet[1] & 0x02) >> 1)
                flag2 = (packet[1] & 0x01)
                if ((packet[1] & 0x04) >> 2):  # Check LPC
                    return {origin: source, type: cte.ACK_ACKDISCOVERY}
                else:
                    return {origin: source, type: cte.ACK_DISCOVERY, flag1: flag1, flag2: flag2}

            elif PT==2:
                secN = ((packet[1] & 0x80) >> 7)
                payload = packet[2:pktlength-2]
                return {origin: source, type: cte.DATA_PACKET, secN: secN, payload: payload}

            elif PT==3:
                secN = ((packet[1] & 0x80) >> 7)
                if (packet[1] & 0x02) >> 1: # Check LPC
                    return {origin: source, type: cte.ACK_ACKPACKET}
                else:
                    return {origin: source, type: cte.ACK_PACKET, secN: secN}

            elif PT==4:
                return {origin: source, type: cte.TOKEN_PACKET}

            elif PT==6:
                return {origin: source, type: cte.ACK_TOKEN}

            elif PT==5:
                return {origin: source, type: cte.END_OF_TX}

        else:
            return False
