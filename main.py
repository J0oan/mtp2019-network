import cte
from node import Node
from utils import check_role
from bunch import Bunch
import json


def get_config(json_file):
    with open(json_file, 'r') as config:
        config_dict = json.load(config)

    config = Bunch(config_dict)

    return config, config_dict


def process_config(json_file):
    config, _ = get_config_from_json(json_file)
    return config


def get_args():
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '-c', '--config',
        metavar='C',
        default='None',
        help='The Configuration file')
    args = argparser.parse_args()
    return args


while True:
    # State Machine
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
            node.broadcast_flooding()

            if node.any_neighbor_without_file():
                state = cte.SEND_PACKET
            else:
                state = cte.COMMUNICATION_OVER

        elif state is cte.BROADCAST_ACK:
            node.broadcast_ack()
            state = cte.RECEIVE_DATA

        elif state is cte.SEND_PACKET:
            node.send_packets()
            state = cte.PASS_TOKEN

        elif state is cte.RECEIVE_DATA:
            node.receive_packets()
            state = cte.WAIT_TOKEN

        elif state is cte.PASS_TOKEN:
            node.pass_token()
            state = cte.COMMUNICATION_OVER

        elif state is cte.WAIT_TOKEN:
            node.wait_token()
            state = cte.BROADCAST_FLOODING

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










