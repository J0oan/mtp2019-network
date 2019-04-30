import GPIO
from utils import check_role
import cte

while True:
    # Gestiona los diferentes estados
    node = Node()

    role = check_role()
    state = ''

    if role == "tx":
        state = cte.INITIAL_TX
    else:
        state = cte.INITIAL_RX

    while True:
        if state is cte.INITIAL_TX:
            state = cte.BROADCAST_FLOODING

        elif state is cte.INITIAL_RX:
            state = cte.BROADCAST_ACK

        elif state is cte.BROADCAST_FLOODING:
            node.broacast_flooding()

        elif state is cte.BROADCAST_ACK:
            node.broadcast_ack()







