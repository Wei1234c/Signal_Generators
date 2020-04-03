# To be a substitute of SPI
# https://en.wikipedia.org/wiki/Serial_Peripheral_Interface


class ShiftRegister:
    BITS_IN_BYTE = 8
    POLARITY_DEFAULT = 0
    PHASE_DEFAULT = 0
    CLEAR_VALUE = 0x00
    MODES = {0: {'CPOL': 0, 'CPHA': 0},
             1: {'CPOL': 0, 'CPHA': 1},
             2: {'CPOL': 1, 'CPHA': 0},
             3: {'CPOL': 1, 'CPHA': 1}}


    def __init__(self, stb_pin, clk_pin, data_pin,
                 bits = BITS_IN_BYTE, lsbfirst = False,
                 polarity = POLARITY_DEFAULT, phase = PHASE_DEFAULT):

        self.stb_pin = stb_pin
        self.clk_pin = clk_pin
        _ = self.clk_pin.low() if polarity == 0 else self.clk_pin.high()
        self.data_pin = data_pin
        self.lsbfirst = lsbfirst
        self.polarity = polarity
        self.phase = phase
        self.bits = bits


    def _get_bits(self, value, lsbfirst):
        return [value >> i & 1 for i in (range(0, self.bits, 1) if lsbfirst else range(self.bits - 1, -1, -1))]


    def write(self, bytes_array, lsbfirst = None):
        self.stb_pin.low()
        for b in bytes_array:
            self.shiftOut(b, lsbfirst = lsbfirst, drop_stb = False, raise_stb = False)
        self.stb_pin.high()


    def shiftOut(self, value, lsbfirst = None, drop_stb = True, raise_stb = True):

        if lsbfirst is None:
            lsbfirst = self.lsbfirst

        bits = self._get_bits(value, lsbfirst)

        if drop_stb:
            self.stb_pin.low()

        for i in range(len(bits)):
            if self.phase == 0:
                _ = self.data_pin.high() if bits[i] else self.data_pin.low()
                _ = self.clk_pin.high() if self.polarity == 0 else self.clk_pin.low()
            else:
                _ = self.clk_pin.high() if self.polarity == 0 else self.clk_pin.low()
                _ = self.data_pin.high() if bits[i] else self.data_pin.low()

            _ = self.clk_pin.low() if self.polarity == 0 else self.clk_pin.high()

        if raise_stb:
            self.stb_pin.high()


    def shiftIn(self, lsbfirst = None, drop_stb = True, raise_stb = True):
        if lsbfirst is None:
            lsbfirst = self.lsbfirst
        self.data_pin.high()  # need to pull high

        if drop_stb:
            self.stb_pin.low()

        bits = 0
        for i in range(self.bits):
            self.clk_pin.low()
            shift_bits = i if lsbfirst else self.bits - i
            bits = bits | self.data_pin.value() << shift_bits
            self.clk_pin.high()

        if raise_stb:
            self.stb_pin.high()

        return bits


    def clear(self, value = CLEAR_VALUE):
        self.shiftOut(value)
