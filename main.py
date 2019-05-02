import argparse
import cte
from bunch import Bunch
import json
from node import Node
from utils import check_role
import time
import os

def get_config_from_json(json_file):
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

path = "texttosend"
payload_size = 28

for file in os.listdir(path):
    if file.endswith(".txt"):
        file_path = os.path.join(path, file)
        file_pointer = open(file_path, 'r')
    file_len = os.path.getsize(file_path)
    radio_init()
    text = file_pointer.read(payload_size)
    time.sleep(10/1000)
    radio.write(str(file_len))
    time.sleep(10 / 1000)

if role == 'tx':
    file = []
else:
    file = False

node = Node(config, file)

while True:

    node.check_receiver()

    if node.state is cte.BROADCAST_FLOODING:
        node.retransmission = config.N
        node.broadcast_flooding()

    elif node.state is cte.CHOOSE_RECEIVER:
        node.choose_receiver()

    elif node.state is cte.SEND_PACKET:
        node.retransmission = config.n
        node.send_packets()

    elif node.state is cte.RECEIVE_DATA:
        node.receive_packets()

    elif node.state is cte.PASS_TOKEN:
        node.pass_token()
        node.state = cte.COMMUNICATION_OVER

    elif node.state is cte.WAIT_TOKEN:
        node.wait_token()
        node.state = cte.BROADCAST_FLOODING

    elif node.state is cte.COMMUNICATION_OVER:
        node.return_token()

    elif node.state is cte.CHOOSE_TOKEN:
        node.choose_token_successor()
