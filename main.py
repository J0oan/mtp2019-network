import cte
from node import Node
from utils import check_role
from bunch import Bunch
import json


def get_config(json_file):
    with open(json_file, 'r') as configuration:
        config_dict = json.load(configuration)

    configuration = Bunch(config_dict)

    return configuration, config_dict


def process_config(json_file):
    configuration, _ = get_config_from_json(json_file)
    return configuration


def get_args():
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '-c', '--config',
        metavar='C',
        default='None',
        help='The Configuration file')
    args = argparser.parse_args()
    return args


try:
    args = get_args()
    config = process_config(args.config)

except:
    print("missing or invalid arguments")
    exit(0)

role = check_role()

config.role = role

node = Node(config)

while True:

    node.check_receiver()

    if node.state is cte.BROADCAST_FLOODING:
        node.retransmission = config.N
        node.broadcast_flooding()

        """if node.any_neighbor_without_file():
            node.state = cte.SEND_PACKET
        else:
            node.state = cte.COMMUNICATION_OVER"""

    elif node.state is cte.SEND_PACKET:
        node.send_packets()
        node.state = cte.PASS_TOKEN

    elif node.state is cte.RECEIVE_DATA:
        node.receive_packets()
        node.state = cte.WAIT_TOKEN

    elif node.state is cte.PASS_TOKEN:
        node.pass_token()
        node.state = cte.COMMUNICATION_OVER

    elif node.state is cte.WAIT_TOKEN:
        node.wait_token()
        node.state = cte.BROADCAST_FLOODING

    elif node.state is cte.COMMUNICATION_OVER:
        if node.any_neighbor_without_token():
            # Consider neighbors with data and without token
            node.state = cte.PASS_TOKEN

        else:
            if node.any_active_predecessor():
                node.return_token()
                stare = cte.COMMUNICATION_OVER
            else:
                node.state = cte.END
