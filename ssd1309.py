# Micropython SSD1309 OLED driver, I2C interfaces.
from micropython import const
import framebuf

# Command constants from display datasheet
CONTRAST_CONTROL = const(0x81)
ENTIRE_DISPLAY_ON = const(0xA4)
ALL_PIXELS_ON = const(0xA5)
INVERSION_OFF = const(0xA6)
INVERSION_ON = const(0xA7)
DISPLAY_OFF = const(0xAE)
DISPLAY_ON = const(0xAF)
NOP = const(0xE3)
COMMAND_LOCK = const(0xFD)
CHARGE_PUMP = const(0x8D)

# Scrolling commands
CH_SCROLL_SETUP_RIGHT = const(0x26)
CH_SCROLL_SETUP_LEFT = const(0x27)
CV_SCROLL_SETUP_RIGHT = const(0x29)
CV_SCROLL_SETUP_LEFT = const(0x2A)
DEACTIVATE_SCROLL = const(0x2E)
ACTIVATE_SCROLL = const(0x2F)
VSCROLL_AREA = const(0xA3)
SCROLL_SETUP_LEFT = const(0x2C)
SCROLL_SETUP_RIGHT = const(0x2D)

# Addressing commands
LOW_CSA_IN_PAM = const(0x00)
HIGH_CSA_IN_PAM = const(0x10)
MEMORY_ADDRESSING_MODE = const(0x20)
COLUMN_ADDRESS = const(0x21)
PAGE_ADDRESS = const(0x22)
PSA_IN_PAM = const(0xB0)
DISPLAY_START_LINE = const(0x40)
SEGMENT_MAP_REMAP = const(0xA0)
SEGMENT_MAP_FLIPPED = const(0xA1)
MUX_RATIO = const(0xA8)
COM_OUTPUT_NORMAL = const(0xC0)
COM_OUTPUT_FLIPPED = const(0xC8)
DISPLAY_OFFSET = const(0xD3)
COM_PINS_HW_CFG = const(0xDA)
GPIO = const(0xDC)

# Timing and driving scheme commands
DISPLAY_CLOCK_DIV = const(0xD5)
PRECHARGE_PERIOD = const(0xD9)
VCOM_DESELECT_LEVEL = const(0xDB)


class Ssd1309(framebuf.FrameBuffer):
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.initial_display()

    def initial_display(self):
        for command in (
            DISPLAY_OFF,
            DISPLAY_CLOCK_DIV,
            0x80,
            MUX_RATIO,
            self.height - 1,
            DISPLAY_OFFSET,
            0x00,
            DISPLAY_START_LINE,
            CHARGE_PUMP,
            0x14,
            MEMORY_ADDRESSING_MODE,
            0x00,
            SEGMENT_MAP_FLIPPED,
            COM_OUTPUT_FLIPPED,
            COM_PINS_HW_CFG,
            0x02
            if (self.height == 32 or self.height == 16) and (self.width != 64)
            else 0x12,
            CONTRAST_CONTROL,
            0xFF,
            PRECHARGE_PERIOD,
            0xF1,
            VCOM_DESELECT_LEVEL,
            0x40,
            ENTIRE_DISPLAY_ON,
            INVERSION_OFF,
            DISPLAY_ON,
        ):
            self.write_command(command)

        self.fill(0)
        self.show()

    def power_off(self):
        self.write_command(DISPLAY_OFF | 0x00)

    def power_on(self):
        self.write_command(DISPLAY_ON | 0x01)

    def contrast(self, contrast):
        self.write_command(CONTRAST_CONTROL)
        self.write_command(contrast)

    def invert(self, invert):
        self.write_command(INVERSION_OFF | (invert & 1))

    def show(self):
        coordinates = [0, self.width - 1]
        if self.width == 64:
            # displays with width of 64 pixels are shifted by 32
            coordinates = [32, self.width + 31]
        self.write_command(COLUMN_ADDRESS)
        for coordinate in coordinates:
            self.write_command(coordinate)
        self.write_command(PAGE_ADDRESS)
        self.write_command(0)
        self.write_command(self.pages - 1)
        self.write_data(self.buffer)


class SSD1309_I2C(Ssd1309):
    def __init__(self, width, height, i2c, address=0x3c, external_vcc=False):
        self.i2c = i2c
        self.address = address
        super().__init__(width, height, external_vcc)

    def write_command(self, command):
        # 0x80 -> Co=1, D/C#=0
        self.i2c.writeto(self.address, bytearray([0x80, command]))

    def write_data(self, buffer):
        # 0x40 ->  Co=0, D/C#=1
        self.i2c.writevto(self.address, [b"\x40", buffer])