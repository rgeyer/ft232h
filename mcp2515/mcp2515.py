import spi_instructions, masks, registers
import Adafruit_GPIO.GPIO as GPIO
import Adafruit_GPIO.FT232H as FT232H

class mcp2515(object):
    # CANCTRL Register Values
    # Modes
    CANCTRL_MODE_MASK           = 0xE0
    MCP_CANCTRL_MODE_NORMAL     = 0x00
    MCP_CANCTRL_MODE_SLEEP      = 0x20
    MCP_CANCTRL_MODE_LOOPBACK   = 0x40
    MCP_CANCTRL_MODE_LISTENONLY = 0x60
    MCP_CANCTRL_MODE_CONFIG     = 0x80

    # Config Constants
    # MCP Clock Speed 8M
    MCP_8MHz_1000kBPS_CFG1 = 0x00
    MCP_8MHz_1000kBPS_CFG2 = 0xc0
    MCP_8MHz_1000kBPS_CFG3 = 0x80

    MCP_8MHz_500kBPS_CFG1 = 0x00
    MCP_8MHz_500kBPS_CFG2 = 0xd1
    MCP_8MHz_500kBPS_CFG3 = 0x81

    MCP_8MHz_250kBPS_CFG1 = 0x80
    MCP_8MHz_250kBPS_CFG2 = 0xe5
    MCP_8MHz_250kBPS_CFG3 = 0x83

# define MCP_8MHz_200kBPS_CFG1 (0x80)   /* Increased SJW       */
# define MCP_8MHz_200kBPS_CFG2 (0xF6)   /* Enabled SAM bit     */
# define MCP_8MHz_200kBPS_CFG3 (0x84)   /* Sample point at 75% */
#
# define MCP_8MHz_125kBPS_CFG1 (0x81)   /* Increased SJW       */
# define MCP_8MHz_125kBPS_CFG2 (0xE5)   /* Enabled SAM bit     */
# define MCP_8MHz_125kBPS_CFG3 (0x83)   /* Sample point at 75% */
#
# define MCP_8MHz_100kBPS_CFG1 (0x81)   /* Increased SJW       */
# define MCP_8MHz_100kBPS_CFG2 (0xF6)   /* Enabled SAM bit     */
# define MCP_8MHz_100kBPS_CFG3 (0x84)   /* Sample point at 75% */
#
# define MCP_8MHz_80kBPS_CFG1 (0x84)    /* Increased SJW       */
# define MCP_8MHz_80kBPS_CFG2 (0xD3)    /* Enabled SAM bit     */
# define MCP_8MHz_80kBPS_CFG3 (0x81)    /* Sample point at 75% */
#
# define MCP_8MHz_50kBPS_CFG1 (0x84)    /* Increased SJW       */
# define MCP_8MHz_50kBPS_CFG2 (0xE5)    /* Enabled SAM bit     */
# define MCP_8MHz_50kBPS_CFG3 (0x83)    /* Sample point at 75% */
#
# define MCP_8MHz_40kBPS_CFG1 (0x84)    /* Increased SJW       */
# define MCP_8MHz_40kBPS_CFG2 (0xF6)    /* Enabled SAM bit     */
# define MCP_8MHz_40kBPS_CFG3 (0x84)    /* Sample point at 75% */
#
# define MCP_8MHz_33k3BPS_CFG1 (0x85)   /* Increased SJW       */
# define MCP_8MHz_33k3BPS_CFG2 (0xF6)   /* Enabled SAM bit     */
# define MCP_8MHz_33k3BPS_CFG3 (0x84)   /* Sample point at 75% */
#
# define MCP_8MHz_31k25BPS_CFG1 (0x87)  /* Increased SJW       */
# define MCP_8MHz_31k25BPS_CFG2 (0xE5)  /* Enabled SAM bit     */
# define MCP_8MHz_31k25BPS_CFG3 (0x83)  /* Sample point at 75% */
#
# define MCP_8MHz_20kBPS_CFG1 (0x89)    /* Increased SJW       */
# define MCP_8MHz_20kBPS_CFG2 (0xF6)    /* Enabled SAM bit     */
# define MCP_8MHz_20kBPS_CFG3 (0x84)    /* Sample point at 75% */
#
# define MCP_8MHz_10kBPS_CFG1 (0x93)    /* Increased SJW       */
# define MCP_8MHz_10kBPS_CFG2 (0xF6)    /* Enabled SAM bit     */
# define MCP_8MHz_10kBPS_CFG3 (0x84)    /* Sample point at 75% */
#
# define MCP_8MHz_5kBPS_CFG1 (0xA7)     /* Increased SJW       */
# define MCP_8MHz_5kBPS_CFG2 (0xF6)     /* Enabled SAM bit     */
# define MCP_8MHz_5kBPS_CFG3 (0x84)     /* Sample point at 75% */

    def __init__(self, ft232h, cs_pin=3):
        # Mode is defaulted to 0, and bit order to MSBFIRST
        ft232h.setup(cs_pin, GPIO.OUT)
        self._ft232h = ft232h
        self._cs = cs_pin
        # 450kHz was too slow for retrieval of rx buffers, 2Mhz worked, bumped
        # it to twice that for funsies.. Then realized that 10Mhz is the max,
        # so let's do that!
        self._spi = FT232H.SPI(ft232h, max_speed_hz=10000000)

    def enable_interrupts(self, interrupt_flags=[]):
        caninte = 0x00
        for flag in interrupt_flags:
            caninte |= flag

        self.spi_set_register(registers.CANINTE, caninte)

    # def init_buffers(self):
    #     self.

    def write_masks_and_filters(self, address, ext, id):
        # TODO: Presumably this is a mask for CAN IDs, since
        # they can only be 11 bit?. Weird tho, since this is 12 bit.
        # Stealing shamelessly from here, but trying to understand it for myself
        # https://github.com/coryjfowler/MCP_CAN_lib/blob/master/mcp_can.cpp#L637
        canid = id & masks.CAN_ID
        tbufdata = []

        if ext == 1:
            tbufdata[registers.MF_EID0_IDX] = canid & 0xFF
            tbufdata[regiseters.MF_EID8_IDX] = canid >> 8
            # TODO: Why?
            canid = id >> 16
            tbufdata[registers.MF_SIDL_IDX] = canid & 0x03
            tbufdata[registers.MF_SIDL_IDX] += (canid & 0x1c) << 3
            tbufdata[registers.MF_SIDL_IDX] |= masks.MCP_TXB_EXIDE
            tbufdata[registers.MF_SIDH_IDX] = canid >> 5
        else:
            tbufdata[registers.MF_EID0_IDX] = canid & 0xFF
            tbufdata[registers.MF_EID8_IDX] = canid >> 8
            # TODO: Why?
            canid = id >> 16
            tbufdata[registers.MF_SIDL_IDX] = (canid & 0x07) << 5
            tbufdata[registers.MF_SIDH_IDX] = canid >> 3

        self.spi_set_registers_sequential(address, tbufdata)

    def spi_read_register(self, address):
        return self.spi_read_registers_sequential(address, 1)

    def spi_read_registers_sequential(self, address, count):
        self._ft232h.set_low(self._cs)
        self._spi.write([spi_instructions.MCP_READ, address])
        response = self._spi.read(count)
        self._ft232h.set_high(self._cs)
        return response

    def spi_set_registers_sequential(self, address, value):
        write_array = [spi_instructions.MCP_WRITE, address]
        write_array.extend(value)
        self._ft232h.set_low(self._cs)
        self._spi.write(write_array)
        self._ft232h.set_high(self._cs)

    def spi_set_register(self, address, value):
        self._ft232h.set_low(self._cs)
        self._spi.write([spi_instructions.MCP_WRITE, address, value])
        self._ft232h.set_high(self._cs)

    def spi_modify_register(self, address, mask, value):
        self._ft232h.set_low(self._cs)
        self._spi.write([spi_instructions.MCP_BITMOD, address, mask, value])
        self._ft232h.set_high(self._cs)

    def set_CANCTRL_mode(self, newmode):
        self.spi_modify_register(registers.CANCTRL, mcp2515.CANCTRL_MODE_MASK, newmode)

    def spi_read_status(self):
        self._ft232h.set_low(self._cs)
        self._spi.write([spi_instructions.MCP_READ_STATUS])
        response = self._spi.read(1)
        self._ft232h.set_high(self._cs)
        return response

    def spi_rx_status(self):
        self._ft232h.set_low(self._cs)
        self._spi.write([spi_instructions.MCP_RX_STATUS])
        response = self._spi.read(1)
        self._ft232h.set_high(self._cs)
        return response

    def spi_reset(self):
        self._ft232h.set_low(self._cs)
        self._spi.write([spi_instructions.MCP_RESET])
        self._ft232h.set_high(self._cs)

    def spi_read_rx_buffer(self, start_address):
        self._ft232h.set_low(self._cs)
        self._spi.write([spi_instructions.READ_RX_BUFFER | start_address])
        response = self._spi.read(13)
        self._ft232h.set_high(self._cs)
        return response

    def spi_load_tx_buffer(self, start_address, data):
        sendbuf = [spi_instructions.LOAD_TX_BUFFER | start_address]
        sendbuf.extend(data)
        self._ft232h.set_low(self._cs)
        self._spi.write(sendbuf)
        self._ft232h.set_high(self._cs)

    def spi_request_to_send(self, tx_buffer):
        self._ft232h.set_low(self._cs)
        self._spi.write([spi_instructions.RTS | tx_buffer])
        self._ft232h.set_high(self._cs)

    def can_status(self):
        return self.spi_read_register(registers.CANSTAT)[0]

    def can_control(self):
        return self.spi_read_register(registers.CANCTRL)[0]

    def configure_rate(self, canSpeed=250000, canClock=8000000):
        # TODO: Only supporting an 8MHz clock crystal and 240k canbus speed.
        if canClock == 8000000:
            if canSpeed == 250000:
                self.spi_set_register(registers.CNF3, mcp2515.MCP_8MHz_250kBPS_CFG3)
                self.spi_set_register(registers.CNF2, mcp2515.MCP_8MHz_250kBPS_CFG2)
                self.spi_set_register(registers.CNF1, mcp2515.MCP_8MHz_250kBPS_CFG1)
            else:
                return "Unsupported CAN bus speed of {}".format(canSpeed)
        else:
            return "Unsupported CAN clock of {}".format(canClock)
