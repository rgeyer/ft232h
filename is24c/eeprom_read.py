import ftdi1, sys, logging
import Adafruit_GPIO.FT232H as FT232H

logger = logging.getLogger()
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)
logger.setLevel(logging.DEBUG)

# FT232H.use_FT232H()
# Necessary only for later versions of OSX, or Linux?

device_address = 0x50

ft232h = FT232H.FT232H()
i2c = FT232H.I2CDevice(ft232h, device_address)

ping_result = i2c.ping()
print(ping_result)
if not ping_result:
    logger.error("Unable to ping target device")
    exit(1)

i2c.writeRaw8(0x00)

print("0x%02X" % i2c.readU8(0x00))

# ("0x%02X " % x for x in can0.spi_read_rx_buffer(spi_instructions.READ_RXB1SIDH)))
print(" ".join("0x%02X" % x for x in i2c.readList(0x00, 10)))
