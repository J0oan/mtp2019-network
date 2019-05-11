from bunch import Bunch
import json
import argparse
import os


def check_role():
    """

    :return:
    """
    # TODO decide how to determine de role of every node.
    return "tx"


def get_config_from_json(json_file):
    """
    Read json file.
    :param json_file: file to read
    :return: content of the file.
    """
    with open(json_file, 'r') as configuration:
        config_dict = json.load(configuration)

    configuration = Bunch(config_dict)

    return configuration, config_dict


def process_config(json_file):
    """

    :param json_file: configuration file.
    :return: json variable with configurations
    """
    configuration, _ = get_config_from_json(json_file)
    return configuration


def get_args():
    """
    Function to get arguments passed to python binary.
    Ex: python3 main.py -c ./config.json
    :return: arguments passed
    Ex: {config: './config.json'}
    """
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '-c', '--config',
        metavar='C',
        default='None',
        help='The Configuration file')
    args = argparser.parse_args()
    return args


def get_file():
    # TODO review get_file
    path = "texttosend"
    payload_size = 28

    for file in os.listdir(path):
        if file.endswith(".txt"):
            file_path = os.path.join(path, file)
            file_pointer = open(file_path, 'r')
            file_len = os.path.getsize(file_path)
            text = file_pointer.read(payload_size)
            return text
