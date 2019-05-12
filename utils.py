from bunch import Bunch
import json
import argparse
import os




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


def get_file(config):
    """ Gets the provided file and reads its content as bytes,
    after that, it stores everything in the variable payload_list,
    which it returns. """

    payload_list = list()

    if os.path.isfile(config.File_Path_Input):
        print("Loading File in: " + config.File_Path_Input)
        with open(config.File_Path_Input, 'rb') as f:
            while True:
                chunk = f.read(config.Paylaod_Size)
                if chunk:
                    payload_list.append(chunk)
                else:
                    break
    else:
        print("ERROR: file does not exist in PATH: " + config.File_Path_Input)

    print("Length of the file in chunks: " + str(len(payload_list)))

    return payload_list



