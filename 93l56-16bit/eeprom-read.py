import ftdi1, os, sys, time, logging
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.FT232H as FT232H
import Adafruit_GPIO.SPI as SPI
import bb93l56

logger = logging.getLogger()
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)
logger.setLevel(logging.DEBUG)

# FT232H.use_FT232H()
# Necessary only for later versions of OSX, or Linux?

ft232h = FT232H.FT232H()
bb = bb93l56.BB93L56(ft232h)
read_bytes = bb.read_address(0x00, 256)

with open("93x56-dump-{}.bin".format(time.time()), "wb") as f:
    f.write(read_bytes)
