import cte
from node import Node
from utils import check_role, get_args, process_config, get_file


try:
    # Get arguments
    args = get_args()
    # Get config file from arguments
    config = process_config(args.config)
except:
    print("missing or invalid arguments")
    exit(0)


# Get role of node
role = check_role()

if role == 'tx':
    file = get_file(config)
else:
    file = False

# Create node entity according to config and pass file if it is possible.
node = Node(config, file)

# Main loop
while True:
    # Check if packet received
    node.check_receiver()

    if node.state is cte.BROADCAST_FLOODING:
        # If node state is broadcast flooding set retransmission of state
        # and begin broadcast transmission
        node.retransmission = config.nDiscovery
        node.broadcast_flooding()

    elif node.state is cte.CHOOSE_RECEIVER:
        # If node state is choose receiver, execute its function
        node.choose_receiver()

    elif node.state is cte.SEND_PACKET:
        # If node state is send data packet set retransmission for this packet
        # and start transmission
        node.retransmission = config.nData
        node.send_packets()

    elif node.state is cte.RECEIVE_DATA:
        # If the node has received a new data packet send ack
        node.receive_packets()

    elif node.state is cte.PASS_TOKEN:
        # If there is a successor to pass the token
        node.pass_token()

    elif node.state is cte.RECEIVE_TOKEN:
        # If passive node has received token packet
        node.receive_token()

    elif node.state is cte.COMMUNICATION_OVER:
        # If this network branch is completed return token
        node.return_token()

    elif node.state is cte.CHOOSE_TOKEN:
        # State to select a successor of the token
        node.choose_token_successor()

    elif node.state is cte.END:
        # State to send end of protocol
        node.retransmission = config.nEnd
        node.send_end()

# General TODOs
# TODO review all the necessary timeouts and if there must be different or is not necessary
#   (suggestion): Make a class to manage all timeouts types: backoff, timeout and timeout_general
# TODO decided where to write the received file
# TODO: ACKACKDIscovery
#  (suggestion: receive_packets if end of file)
