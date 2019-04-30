
class Node(object):
    def __init__(self):
        # Initialize node
        # Tx channel
        # Initialize radios
    def send_data(self):
        return NotImplementedError

    def read_data(self):
        return NotImplementedError

    def send_packet(self):
        """
        Uses send_data() to tx data
        :return:
        """
        return NotImplementedError

    def broadcast_flooding(self):
        return NotImplementedError

    def broadcast_ack(self):
        return NotImplementedError

    def has_neighbors(self):
        """
        True if it has neighbors, False otherwise
        :return: Bool
        """
        return NotImplementedError

    def have_neighbors_without_file(self):
        return NotImplementedError

    def any_neighbor_without_token(self):
        return NotImplementedError

    def any_active_predecessor(self):
        return NotImplementedError

    def return_token(self):
        return NotImplementedError