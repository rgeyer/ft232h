import mcp2515, registers, spi_instructions, ftdi1, logging, sys, time
import Adafruit_GPIO.FT232H as FT232H

logger = logging.getLogger()
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)
logger.setLevel(logging.INFO)

ft232h = FT232H.FT232H()
can0 = mcp2515.mcp2515(ft232h)
can1 = mcp2515.mcp2515(ft232h, 4)
can2 = mcp2515.mcp2515(ft232h, 5)

# RESET
logger.info("Sending RESET SPI instruction")
can0.spi_reset()
can1.spi_reset()
can2.spi_reset()

# CONFIG MODE
# Technically redundant, since the reset above puts it into config mode
logger.info("Setting CANCTRL Mode to config")
can0.set_CANCTRL_mode(mcp2515.mcp2515.MCP_CANCTRL_MODE_CONFIG)
can1.set_CANCTRL_mode(mcp2515.mcp2515.MCP_CANCTRL_MODE_CONFIG)
can2.set_CANCTRL_mode(mcp2515.mcp2515.MCP_CANCTRL_MODE_CONFIG)

# CONFIG RATE
# Using the defaults in the class, of 8Mhz crystal, and 250Khz can network
# speed
rate_response = can0.configure_rate()
if rate_response:
    logger.error("Failed to set canbus rate for can0. Error: {}".format(rate_response))
    exit(1)

rate_response = can1.configure_rate()
if rate_response:
    logger.error("Failed to set canbus rate for can1. Error: {}".format(rate_response))
    exit(1)

rate_response = can2.configure_rate()
if rate_response:
    logger.error("Failed to set canbus rate for can2. Error: {}".format(rate_response))
    exit(1)

# TODO: Setup masks and filters. This should just show everything is set to zeros
# logger.info("RXF0-2:")
# logger.info("".join("0x%02X " % x for x in can1.spi_read_registers_sequential(0x00, 12)))
# logger.info("RXF3-5:")
# logger.info("".join("0x%02X " % x for x in can1.spi_read_registers_sequential(0x10, 12)))
# logger.info("RXM0-1:")
# logger.info("".join("0x%02X " % x for x in can1.spi_read_registers_sequential(0x20, 8)))

logger.info("Setting RXB0CTRL to accept all")
can0.spi_modify_register(registers.RXB0CTRL, 0xff, 0x64)
can1.spi_modify_register(registers.RXB0CTRL, 0xff, 0x64)
can2.spi_modify_register(registers.RXB0CTRL, 0xff, 0x64)

logger.info("Setting RXB1CTRL to accept all")
can0.spi_modify_register(registers.RXB1CTRL, 0xff, 0x60)
can1.spi_modify_register(registers.RXB0CTRL, 0xff, 0x64)
can2.spi_modify_register(registers.RXB0CTRL, 0xff, 0x64)

can0.enable_interrupts([registers.CANINTE_RX0IE, registers.CANINTE_RX1IE])
can1.enable_interrupts([registers.CANINTE_RX0IE, registers.CANINTE_RX1IE])
can2.enable_interrupts([registers.CANINTE_RX0IE, registers.CANINTE_RX1IE])

logger.info("Setting CANCTRL Mode to MCP_CANCTRL_MODE_NORMAL")
can0.set_CANCTRL_mode(mcp2515.mcp2515.MCP_CANCTRL_MODE_NORMAL)
can1.set_CANCTRL_mode(mcp2515.mcp2515.MCP_CANCTRL_MODE_NORMAL)
can2.set_CANCTRL_mode(mcp2515.mcp2515.MCP_CANCTRL_MODE_NORMAL)

can0.spi_load_tx_buffer(spi_instructions.LOAD_TXB0SIDH, [0x6f, 0xe0, 0x00, 0x00, 0x04, 0xab, 0xcd, 0xef, 0x01])
can0.spi_request_to_send(spi_instructions.RTS_TXB0)

can1.spi_load_tx_buffer(spi_instructions.LOAD_TXB0SIDH, [0x6f, 0xe0, 0x00, 0x00, 0x04, 0xab, 0xcd, 0xef, 0x01])
can1.spi_request_to_send(spi_instructions.RTS_TXB0)

# time.sleep(1)
#
# logger.info("Read Status: 0x%02X" % can0.spi_read_status()[0])
# logger.info("RX Status: 0x%02X" % can0.spi_rx_status()[0])
#
# logger.info("RX0 Buffer: %s" % "".join("0x%02X " % x for x in can0.spi_read_rx_buffer(spi_instructions.READ_RXB0SIDH)))
# logger.info("RX1 Buffer: %s" % "".join("0x%02X " % x for x in can0.spi_read_rx_buffer(spi_instructions.READ_RXB1SIDH)))
#
# logger.info("Read Status: 0x%02X" % can0.spi_read_status()[0])
# logger.info("RX Status: 0x%02X" % can0.spi_rx_status()[0])
#
# logger.info("RX0 Buffer: %s" % "".join("0x%02X " % x for x in can0.spi_read_rx_buffer(spi_instructions.READ_RXB0SIDH)))
# logger.info("RX1 Buffer: %s" % "".join("0x%02X " % x for x in can0.spi_read_rx_buffer(spi_instructions.READ_RXB1SIDH)))
#
# logger.info("Read Status: 0x%02X" % can0.spi_read_status()[0])
# logger.info("RX Status: 0x%02X" % can0.spi_rx_status()[0])

start = time.time()
end = start + 20

last_pulse = start

while time.time() < end:
    if time.time() > last_pulse + 10:
        can2.spi_load_tx_buffer(spi_instructions.LOAD_TXB0SIDH, [0x6f, 0xe0, 0x00, 0x00, 0x04, 0x01, 0x23, 0x45, 0x67])
        # can0.spi_load_tx_buffer(spi_instructions.LOAD_TXB0D0, [0xab])
        can2.spi_request_to_send(spi_instructions.RTS_TXB0)
        last_pulse = time.time()
    canintf0 = can0.spi_read_register(registers.CANINTF)[0]
    canintf1 = can1.spi_read_register(registers.CANINTF)[0]
    canintf2 = can2.spi_read_register(registers.CANINTF)[0]
    if canintf0 & 0x01:
        logger.info("CAN0 RXB0CTRL: 0x%02X" % can0.spi_read_register(registers.RXB0CTRL)[0])
        logger.info("".join("0x%02X " % x for x in can0.spi_read_registers_sequential(0x61, 13)))
        logger.info("CAN0 RX0 Buffer: %s" % "".join("0x%02X " % x for x in can0.spi_read_rx_buffer(spi_instructions.READ_RXB0SIDH)))

    if canintf0 & 0x02:
        logger.info("CAN0 RXB1CTRL: 0x%02X" % can0.spi_read_register(registers.RXB1CTRL)[0])
        logger.info("".join("0x%02X " % x for x in can0.spi_read_registers_sequential(0x71, 13)))
        logger.info("CAN0 RX1 Buffer: %s" % "".join("0x%02X " % x for x in can0.spi_read_rx_buffer(spi_instructions.READ_RXB1SIDH)))

    if canintf1 & 0x01:
        logger.info("CAN1 RXB0CTRL: 0x%02X" % can1.spi_read_register(registers.RXB0CTRL)[0])
        logger.info("".join("0x%02X " % x for x in can1.spi_read_registers_sequential(0x61, 13)))
        logger.info("CAN1 RX0 Buffer: %s" % "".join("0x%02X " % x for x in can1.spi_read_rx_buffer(spi_instructions.READ_RXB0SIDH)))

    if canintf1 & 0x02:
        logger.info("CAN1 RXB1CTRL: 0x%02X" % can1.spi_read_register(registers.RXB1CTRL)[0])
        logger.info("".join("0x%02X " % x for x in can1.spi_read_registers_sequential(0x71, 13)))
        logger.info("CAN1 RX1 Buffer: %s" % "".join("0x%02X " % x for x in can1.spi_read_rx_buffer(spi_instructions.READ_RXB1SIDH)))

    if canintf2 & 0x01:
        logger.info("CAN2 RXB0CTRL: 0x%02X" % can2.spi_read_register(registers.RXB0CTRL)[0])
        logger.info("".join("0x%02X " % x for x in can2.spi_read_registers_sequential(0x61, 13)))
        logger.info("CAN2 RX0 Buffer: %s" % "".join("0x%02X " % x for x in can2.spi_read_rx_buffer(spi_instructions.READ_RXB0SIDH)))

    if canintf2 & 0x02:
        logger.info("CAN2 RXB1CTRL: 0x%02X" % can2.spi_read_register(registers.RXB1CTRL)[0])
        logger.info("".join("0x%02X " % x for x in can2.spi_read_registers_sequential(0x71, 13)))
        logger.info("CAN2 RX1 Buffer: %s" % "".join("0x%02X " % x for x in can2.spi_read_rx_buffer(spi_instructions.READ_RXB1SIDH)))
