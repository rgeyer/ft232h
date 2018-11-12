from Adafruit_GPIO import *

class BB93L56(SPI.BitBang):
    def __init__(self, ft232h, cs=3, max_speed_hz=450000):
        # CLK, MOSI, and MISO are the SPI pins, since we're mixing and matching
        # GPIO and SPI into an awful amalgamation
        super(BB93L56, self).__init__(ft232h, 0, 1, 2, 3)
        self._gpio.set_low(self._ss)
        self._spi = FT232H.SPI(ft232h, max_speed_hz=max_speed_hz)

    def write_enable(self):
        command = [0x04, 0xc0]
        self.write(command)
        # TODO: Return anything?

    def write_address(self, address, data):
        command = [0x05, address]
        command.extend(data)
        self.write(command)
        # TODO: Bring CS back up and monitor DO for completion?

    def read_address(self, address, length):
        self.write([0x06,address],assert_ss=True,deassert_ss=False)
        # The 93xxx series I'm working with sends a dummy 0 bit on DO after the
        # read command and address has been sent, so we tick the clock once to
        # ignore it before starting the read.
        # Flip clock off base.
        self._gpio.output(self._sclk, not self._clock_base)
        # Return clock to base.
        self._gpio.output(self._sclk, self._clock_base)
        # Switch to using a straight SPI read which is infinitely faster, and
        # reliable than bit banging.
        return self.read(length, False, True)

    def write(self, data, assert_ss=True, deassert_ss=True):
        if assert_ss and self._ss is not None:
            self._gpio.set_high(self._ss)
        self._spi.write(data)
        if deassert_ss and self._ss is not None:
            self._gpio.set_low(self._ss)

    def read(self, length, assert_ss=True, deassert_ss=True):
        if assert_ss and self._ss is not None:
            self._gpio.set_high(self._ss)
        result = self._spi.read(length)
        if deassert_ss and self._ss is not None:
            self._gpio.set_low(self._ss)
        return result
