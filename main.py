import cte
from node import Node
from utils import  get_args, process_config, get_file
import RPi.GPIO as GPIO
import conf_Gpio
import time
from threading import Thread


try:
    # Get arguments
    args = get_args()
    # Get config file from arguments
    config = process_config(args.config)
except:
    print("missing or invalid arguments")
    exit(0)



# Initialization
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GO = False



def setup_gpio():
    # Setup inputs
    GPIO.setup(conf_Gpio.SW_ROLE, GPIO.IN)
    GPIO.setup(conf_Gpio.SW_GO, GPIO.IN)
    # Setup outputs
    GPIO.setup(conf_Gpio.LED_RX_ROLE, GPIO.OUT)
    GPIO.setup(conf_Gpio.LED_TX_ROLE, GPIO.OUT)
    GPIO.setup(conf_Gpio.LED_TX_RX_PROCESS, GPIO.OUT)
    # Setting up LEDs to off
    GPIO.output(conf_Gpio.LED_TX_RX_PROCESS, 0)
    GPIO.output(conf_Gpio.LED_TX_ROLE, 0)
    GPIO.output(conf_Gpio.LED_RX_ROLE, 0)


def check_role():
    global ROLE
    sw_role = GPIO.input(conf_Gpio.SW_ROLE)
    if sw_role == 0:
        ROLE = 'rx'
        return True
    elif sw_role == 1:
        ROLE = 'tx'
        return True
    else:
        return False

def start_wait_blink():
    blink_thread = Thread(target=blink_wait, args=(conf_Gpio.WAIT_BLINK_PERIOD,))
    blink_thread.start()

def blink_wait(blink_period):
    while not GO:
        GPIO.output(conf_Gpio.LED_TX_RX_PROCESS, 1)
        time.sleep(blink_period)
        GPIO.output(conf_Gpio.LED_TX_RX_PROCESS, 0)
        time.sleep(blink_period)

def start_tx_rx_blink():
    blink_thread = Thread(target=blink_tx_rx, args=(conf_Gpio.TX_RX_BLINK_PERIOD,))
    blink_thread.start()

def blink_tx_rx(blink_period):
    while GO:
        GPIO.output(conf_Gpio.LED_TX_RX_PROCESS, 1)
        time.sleep(blink_period)
        GPIO.output(conf_Gpio.LED_TX_RX_PROCESS, 0)
        time.sleep(blink_period)

def main():
    global GO
    # Setup GPIO
    setup_gpio()
    # Get role of node
    ROLE = check_role()

    if ROLE == 'tx':
        file = get_file(config)
    else:
        file = False


    # Create node entity according to config and pass file if it is possible.
    node = Node(config, file)
    start_wait_blink()

    while not GO:
        go_sw = GPIO.input(conf_Gpio.SW_GO)
        if go_sw == 1:
            GO = True
            print("Go pushed, starting transmission...")
        else:
            time.sleep(0.1)
    # Main loop
    while GO:

        start_tx_rx_blink()
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


if __name__ == '__main__':
    main()

# General TODOs
# TODO review all the necessary timeouts and if there must be different or is not necessary
#   (suggestion): Make a class to manage all timeouts types: backoff, timeout and timeout_general
# TODO decided where to write the received file
# TODO: ACKACKDIscovery
#  (suggestion: receive_packets if end of file)
