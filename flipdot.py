import RPi.GPIO as GPIO
import signal
import sys
import time

from characters import Characters

ON = False
OFF = True
pulse_time = 10e-3

relay0 = [37, 35, 40, 38, 36, 33, 31, 32]
relay1 = [26, 24, 22, 23, 21, 15, 13, 11]

# for setting dots to black
common_set = relay1[0]

# vcc toggle and vcc_ground_select required
cols = [relay0[i + 3] for i in range(5)]
# always high if enabled
rows = [relay1[i + 1] for i in range(7)]

# for selecting column polarity
ground_toggle = relay0[0]
vcc_toggle = relay0[1]
# vcc = OFF; ground = ON
cols_polarity_select = relay0[2]


class FlipDot:
    def __init__(self):
        signal.signal(signal.SIGINT, self._exit_handler)
        GPIO.setmode(GPIO.BOARD)

        for pin in relay0 + relay1:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, OFF)

        self.blank_all()

    def _exit_handler(self, sig, frame):
        GPIO.cleanup()
        sys.exit(0)

    def _pulse(self, pin, seconds=pulse_time):
        GPIO.output(pin, ON)
        time.sleep(seconds)
        GPIO.output(pin, OFF)

    class _ColumnsSetTo:
        def __init__(self, value, flipDot):
            """
            columns by default are disconnected. This is a way to make sure
            that columns are only connected when we need them to be.

            @param value -
                ON = vcc on columns
                OFF = ground on columns
            """
            self.value = value
            self.flipDot = flipDot

        def __enter__(self):
            if self.value == ON:
                GPIO.output(vcc_toggle, ON)
            else:
                GPIO.output(ground_toggle, ON)

            GPIO.output(cols_polarity_select, not self.value)

        def __exit__(self, type, value, tb):
            if tb is not None:
                print("something very bad happened, exiting")
                self.flipDot._exit_handler(None, None)

            GPIO.output(vcc_toggle, OFF)
            GPIO.output(ground_toggle, OFF)
            GPIO.output(cols_polarity_select, OFF)

    def blank_all(self):
        """
        set the whole screen to black
        """
        GPIO.output(common_set, ON)
        time.sleep(5e-3)

        with self._ColumnsSetTo(ON, self):
            for col in cols:
                self._pulse(col, 10e-3)

        GPIO.output(common_set, OFF)

    def set_all(self):
        """
        set the whole screen to yellow
        """
        with self._ColumnsSetTo(OFF, self):
            for col in cols:
                GPIO.output(col, ON)

                for row in rows:
                    self._pulse(row)
                    time.sleep(0.1)

                GPIO.output(col, OFF)

    def set_xy(self, x, y):
        """
        set the dot at (x, y) to yellow
        """
        if not ((0 <= x < 5) and (0 <= y < 7)):
            raise IndexError(f"dot ({x}, {y}) out of range")

        with self._ColumnsSetTo(OFF, self):
            GPIO.output(cols[x], ON)
            self._pulse(rows[y])
            GPIO.output(cols[x], OFF)

    def set_from_matrix(self, matrix):
        """
        set the display from a 5x7 matrix
        1 is on, 0 is off
        """
        if len(matrix) != 5 or len(matrix[0]) != 7:
            raise Exception("bad matrix dimensions")

        # TODO: decompose into cubes to optimize write time
        for i in range(5):
            for j in range(7):
                if matrix[4 - i][j]:
                    self.set_xy(i, j)


flipDot = FlipDot()

while True:
    for matrix in Characters.string_to_matrices("click_clack"):
        flipDot.set_from_matrix(matrix)
        time.sleep(0.5)
        flipDot.blank_all()
        time.sleep(0.2)
    time.sleep(0.2)
