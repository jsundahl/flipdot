import RPi.GPIO as GPIO
import signal
import sys
import time


def exit_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)


signal.signal(signal.SIGINT, exit_handler)
GPIO.setmode(GPIO.BOARD)

pulse_time = 10e-3
ON = False
OFF = True

relay0 = [37, 35, 40, 38, 36, 33, 31, 32]
relay1 = [26, 24, 22, 23, 21, 15, 13, 11]

for pin in relay0 + relay1:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, OFF)

# vcc toggle and vcc_ground_select required
cols = [relay0[i + 3] for i in range(5)]
# always high if enabled
rows = [relay1[i + 1] for i in range(7)]

ground_toggle = relay0[0]
vcc_toggle = relay0[1]
# vcc = OFF; ground = ON
vcc_ground_select = relay0[2]
common_set = relay1[0]


class ColumnsSetTo:
    def __init__(self, value):
        """
        columns by default are disconnected. This is a way to make sure
        that columns are only connected when we need them to be.

        @param value -
            ON = vcc on columns
            OFF = ground on columns
        """
        self.value = value

    def __enter__(self):
        GPIO.output(vcc_toggle, OFF)
        GPIO.output(ground_toggle, OFF)

        if self.value == ON:
            GPIO.output(vcc_toggle, ON)
        else:
            GPIO.output(ground_toggle, ON)
        GPIO.output(vcc_ground_select, not self.value)

    def __exit__(self, type, value, tb):
        if tb is not None:
            exit_handler(None, None)

        GPIO.output(vcc_toggle, OFF)
        GPIO.output(ground_toggle, OFF)
        GPIO.output(vcc_ground_select, OFF)


def pulse(pin, seconds=pulse_time):
    GPIO.output(pin, ON)
    time.sleep(seconds)
    GPIO.output(pin, OFF)


def blank_all():
    """
    set the whole screen to black
    """
    GPIO.output(common_set, ON)
    time.sleep(5e-3)

    with ColumnsSetTo(ON):
        for col in cols:
            pulse(col, 10e-3)

    GPIO.output(common_set, OFF)


def set_all():
    with ColumnsSetTo(OFF):
        for col in cols:
            GPIO.output(col, ON)

            for row in rows:
                pulse(row)
                time.sleep(0.1)

            GPIO.output(col, OFF)


while True:
    blank_all()
    time.sleep(1)
    set_all()
    time.sleep(1)
