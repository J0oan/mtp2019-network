import RPi.GPIO as GPIO
import time
from bunch import Bunch
from threading import Thread
import logging
from . import network_mode

GO = False

SW_ROLE = 1  # SW1
SW_GO = 2  # SW2

LED_TX_ROLE = 3  # LED1
LED_RX_ROLE = 4  # LED2
LED_TX_RX_PROCESS = 5  # LED3
WAIT_BLINK_PERIOD = 2
TX_RX_BLINK_PERIOD = 1


class GPIOManager:
    def __init__(self):
        # Initialization
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Setup inputs
        GPIO.setup(SW_ROLE, GPIO.IN)
        GPIO.setup(SW_GO, GPIO.IN)
        # Setup outputs
        GPIO.setup(LED_RX_ROLE, GPIO.OUT)
        GPIO.setup(LED_TX_ROLE, GPIO.OUT)
        GPIO.setup(LED_TX_RX_PROCESS, GPIO.OUT)
        # Setting up LEDs to off
        GPIO.output(LED_TX_RX_PROCESS, 0)
        GPIO.output(LED_TX_ROLE, 0)
        GPIO.output(LED_RX_ROLE, 0)

    def check_role(self):
        sw_role = GPIO.input(SW_ROLE)
        if sw_role == 0:
            return 'rx'
        elif sw_role == 1:
            return 'tx'

    def start_wait_blink(self):
        blink_thread = Thread(target=self.blink_wait, args=(WAIT_BLINK_PERIOD,))
        blink_thread.start()

    def blink_wait(self, blink_period):
        while not GO:
            GPIO.output(LED_TX_RX_PROCESS, 1)
            time.sleep(blink_period)
            GPIO.output(LED_TX_RX_PROCESS, 0)
            time.sleep(blink_period)

    def start_tx_rx_blink(self):
        blink_thread = Thread(target=self.blink_tx_rx, args=(TX_RX_BLINK_PERIOD,))
        blink_thread.start()

    def blink_tx_rx(self, blink_period):
        while GO:
            GPIO.output(LED_TX_RX_PROCESS, 1)
            time.sleep(blink_period)
            GPIO.output(LED_TX_RX_PROCESS, 0)
            time.sleep(blink_period)


def main():
    GO = False
    # Setup GPIO
    led_manager = GPIOManager()
    # Get role of node
    role = led_manager.check_role()

    while not GO:
        go_sw = GPIO.input(SW_GO)
        if go_sw == 1:
            GO = True
            print("Go pushed, starting transmission...")
        else:
            time.sleep(0.1)

    team_configuration = Bunch({
        "File_Path_Input": "/home/pi/mtp2019-netowrk/Files/Input/*.txt",
        "File_Path_Output": "/home/pi/mtp2019-netowrk/Files/Output/file.txt",
        "Log_Path": "/home/pi/mtp2019-netowrk/Files/logger.log",
        "Log_Level": logging.DEBUG,
        "Tx_CS": "RPI_V2_GPIO_P1_15",
        "Tx_CSN": "BCM2835_SPI_CS1",
        "Rx_CS": "RPI_V2_GPIO_P1_13",
        "Rx_CSN": "BCM2835_SPI_CS0",
        "address": 1})

    network_mode.start(role, led_manager, team_configuration)


if __name__ == '__main__':
    main()
