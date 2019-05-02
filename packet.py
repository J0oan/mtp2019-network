# Clase paquete


class Packet(object):
    def __init__(self, config):
        self.config = config
        self.origin = self.config.address

    def generate_discovery(self):
        """
        Generar paquete Discovery con CRC y delvover array de bytes
        :param origin:
        :return:
        """
        return

    def generate_ack_discovery(self, destination, flags):
        """
        Generar paquete ACK-Discovery con CRC y delvover array de bytes
        :param destination:
        :param flags:
        :return:
        """
        return

    def generate_data(self, destination, seqN, end, payload):
        """
        Generar paquete ACK-Discovery con CRC y delvover array de bytes
        :param destination:
        :param seqN:
        :param end:
        :param payload:
        :return:
        """
        return

    def generate_ack(self, destination, seqN, type):
        """
        Generar paquete ACK con CRC y delvover array de bytes
        :param destination:
        :param seqN:
        :param type:
        :return:
        """
        return

    def generate_token_frame(self, origin, destination):
        """
        Generar paquete tokenFrame con CRC y delvover array de bytes
        :param origin:
        :param destination:
        :return:
        """

        return

    def generate_ack_token_frame(self, origin, destination):
        """
        Generar paquete AckTokenFrame con CRC y delvover array de bytes
        :param origin:
        :param destination:
        :return:
        """
        return

    def end_protocol(self, origin):
        """

        :param origin:
        :return:
        """
        return

    def decapsulate_packet(self, packet):
        """

        :return:
        """
        return
