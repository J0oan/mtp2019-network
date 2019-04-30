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

            if node.have_neighbors_without_file():
                state = cte.SEND_PACKET
            else:
                state = cte.COMMUNICATION_OVER

        elif state is cte.BROADCAST_ACK:
            node.broadcast_ack()

        elif state is cte.SEND_PACKET:
            node.send_packet()
            state = cte.PASS_TOKEN

        elif state is cte.PASS_TOKEN:
            node.pass_token()
            state = cte.COMMUNICATION_OVER

        elif state is cte.COMMUNICATION_OVER:
            if node.any_neighbor_without_token():
                # Consider neighbors with data and without token
                state = cte.PASS_TOKEN

            else:
                if node.any_active_predecessor():
                    node.return_token()
                    stare = cte.COMMUNICATION_OVER
                else:
                    state = cte.END










