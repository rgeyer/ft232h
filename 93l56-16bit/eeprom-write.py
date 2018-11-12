import ftdi1, os, sys, time, logging
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.FT232H as FT232H
import Adafruit_GPIO.SPI as SPI
import bb93l56

EEPROM_SIZE_IN_BYTES = 256
NUMBER_OF_ADDRESSES = 128
SIZE_OF_REGISTER_IN_BYTES = 2

logger = logging.getLogger()
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)
logger.setLevel(logging.DEBUG)

if len(sys.argv) < 2:
    logger.error("You must supply a bin file name as an argument")
    exit(1)

# FT232H.use_FT232H()
# Necessary only for later versions of OSX, or Linux?

ft232h = FT232H.FT232H()
bb = bb93l56.BB93L56(ft232h)

with open(sys.argv[1], 'rb') as f:
    data = f.read()

if len(data) != EEPROM_SIZE_IN_BYTES:
    logger.error("Expected {} bytes, but the dumpfile contained {} bytes.".format(EEPROM_SIZE_IN_BYTES, len(data)))
    exit(1)

bb.write_enable()

idx = 0
while idx < NUMBER_OF_ADDRESSES:
    # write_then_read(port, "[0b101 0x%02X 0x%02X 0x%02X]" % (idx, data[idx * 2], data[idx * 2 + 1]))
    bb.write_address(idx, [data[idx * 2], data[idx * 2 + 1]])
    # Wait 1ms for each byte to finish writing?
    time.sleep(0.100)
    idx += 1
