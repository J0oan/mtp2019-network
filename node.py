
class Node(object):
    def __init__(self):
        # Initialize node
        # Tx channel
        # Initialize radios

    def read_packet(self):
        return NotImplementedError

    def send_packet(self):
        return NotImplementedError

    def broadcast_flooding(self):
        return NotImplementedError

    def broadcast_ack(self):
        return NotImplementedError

