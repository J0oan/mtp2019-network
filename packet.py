#Clase paquete

class packet():

    def init(self):

    def generateDiscovery ( origin ):
        #Generar paquete Discovery con CRC y delvover array de bytes
        return

    def generateAckDiscovery ( origin , destination , flags ):
        #Generar paquete ACK-Discovery con CRC y delvover array de bytes
        return

    def generateData ( origin , destination , seqN , end , payload ):
        #Generar paquete ACK-Discovery con CRC y delvover array de bytes
        return

    def generateAck (origin , destination , seqN ,  type ):
        #Generar paquete ACK con CRC y delvover array de bytes
        return

    def generatetokenFrame ( origin , destination ):
        #Generar paquete tokenFrame con CRC y delvover array de bytes
        return

    def generateAckTokenFrame ( origin , destination ):
        #Generar paquete AckTokenFrame con CRC y delvover array de bytes
        return
    def endProtocol ( origin ):
        return

    def decapsulatepacket(self):
        