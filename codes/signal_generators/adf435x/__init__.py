# Based on: https://github.com/atx/python-adf4351

# The MIT License (MIT)
#
# Copyright (C) 2016 Josef Gajdusek <atx@atx.name>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


try:
    from math import gcd
except ImportError:
    from fractions import gcd



def bit(x):
    return 1 << x



def bits(n):
    return (1 << n) - 1



def insert_val(n, v, o, m):
    return (n & ~m) | ((v << o) & m)



class Register:

    def __init__(self, reg_bits):
        self.bits = reg_bits
        self.val = 0x00000000


    def __get__(self, obj, obtype = None):
        if obj is None:
            return self
        return (self.val | self.bits) if self.val is not None else None


    def __set__(self, obj, val):
        self.val = val & ~0b111
        obj.write(val | self.bits)



class RegBit:

    def __init__(self, reg, reg_bit):
        self.reg = reg
        self.bit = reg_bit


    def __get__(self, obj, obtype = None):
        if obj is None:
            return self
        return bool(self.reg.__get__(obj) & self.bit)


    def __set__(self, obj, val):
        rval = self.reg.__get__(obj)
        if val:
            rval |= self.bit
        else:
            rval &= ~self.bit
        self.reg.__set__(obj, rval)



class RegVal:

    def __init__(self, reg, off, width):
        self.reg = reg
        self.off = off
        self.mask = ((1 << width) - 1) << self.off


    def __get__(self, obj, obtype = None):
        if obj is None:
            return self
        return (self.reg.__get__(obj) & self.mask) >> self.off


    def __set__(self, obj, val):
        rval = self.reg.__get__(obj)
        rval &= ~self.mask
        rval |= (val << self.off) & self.mask
        self.reg.__set__(obj, rval)



class ADF4351:
    class R0:
        FRAC_OFF = 3
        FRAC_MASK = bits(12) << FRAC_OFF
        INT_OFF = 15
        INT_MASK = bits(16) << INT_OFF


    class R1:
        MOD_OFF = 3
        MOD_MASK = bits(12) << MOD_OFF
        PHASE_OFF = 15
        PHASE_MASK = bits(12) << PHASE_OFF
        PRESCALER = bit(27)
        PHASE_ADJUST = bit(28)


    class R2:
        COUNTER_RESET_ENABLE = bit(3)
        CP_THREE_STATE_ENABLE = bit(4)
        POWER_DOWN = bit(5)
        PD_POLARITY_POSITIVE = bit(6)
        LDP_6NS = bit(7)
        LDF_INTN = bit(8)
        CHARGE_PUMP_CURRENT_OFF = 9
        DOUBLE_BUFFER_ENABLE = bit(13)
        R_OFF = 14
        R_MASK = bits(10) << R_OFF
        RDIV2_ENABLE = bit(24)
        REFERENCE_DOUBLER_ENABLE = bit(25)
        MUXOUT_OFF = 26
        MUXOUT_THREE_STATE = 0 << MUXOUT_OFF
        MUXOUT_DVDD = 1 << MUXOUT_OFF
        MUXOUT_DGND = 2 << MUXOUT_OFF
        MUXOUT_R = 3 << MUXOUT_OFF
        MUXOUT_N = 4 << MUXOUT_OFF
        MUXOUT_ALD = 5 << MUXOUT_OFF
        MUXOUT_DLD = 6 << MUXOUT_OFF
        LOW_NOISE_SPUR_OFF = 29
        LOW_NOISE_SPUR_MASK = bits(2) << LOW_NOISE_SPUR_OFF


    class R3:
        CLK_DIV_OFF = 3
        CLK_DIV_MASK = bits(12) << CLK_DIV_OFF
        CLK_DIV_MODE_OFF = 15
        CLK_DIV_MODE_DISABLED = 0b00 << CLK_DIV_MODE_OFF
        CLK_DIV_MODE_FAST_LOCK = 0b01 << CLK_DIV_MODE_OFF
        CLK_DIV_MODE_RESYNC_ENABLE = 0b10 << CLK_DIV_MODE_OFF
        CSR = bit(18)
        CHARGE_CANCEL = bit(21)
        ABP = bit(22)
        BAND_SELECT_MODE = bit(23)


    class R4:
        OUTPUT_POWER_OFF = 3
        OUTPUT_POWER__4DBM = 0b00 << OUTPUT_POWER_OFF
        OUTPUT_POWER__1DBM = 0b01 << OUTPUT_POWER_OFF
        OUTPUT_POWER_2DBM = 0b10 << OUTPUT_POWER_OFF
        OUTPUT_POWER_5DBM = 0b11 << OUTPUT_POWER_OFF
        RF_OUTPUT_ENABLE = bit(5)
        AUX_OUTPUT_POWER_OFF = 6
        AUX_OUTPUT_POWER__4DBM = 0b00 << AUX_OUTPUT_POWER_OFF
        AUX_OUTPUT_POWER__1DBM = 0b01 << AUX_OUTPUT_POWER_OFF
        AUX_OUTPUT_POWER_2DBM = 0b10 << AUX_OUTPUT_POWER_OFF
        AUX_OUTPUT_POWER_5DBM = 0b11 << AUX_OUTPUT_POWER_OFF
        AUX_OUTPUT_ENABLE = bit(8)
        AUX_OUTPUT_SELECT = bit(9)
        MTLD = bit(10)
        VCO_POWER_DOWN = bit(11)
        BAND_SELECT_CLOCK_DIV_OFF = 12
        BAND_SELECT_CLOCK_DIV_MASK = bits(8) << BAND_SELECT_CLOCK_DIV_OFF
        DIVIDER_SELECT_OFF = 20
        DIVIDER_SELECT_MASK = 0b111 << DIVIDER_SELECT_OFF
        DIVIDER_SELECT_1 = 0b000 << DIVIDER_SELECT_OFF
        DIVIDER_SELECT_2 = 0b001 << DIVIDER_SELECT_OFF
        DIVIDER_SELECT_4 = 0b010 << DIVIDER_SELECT_OFF
        DIVIDER_SELECT_8 = 0b011 << DIVIDER_SELECT_OFF
        DIVIDER_SELECT_16 = 0b100 << DIVIDER_SELECT_OFF
        DIVIDER_SELECT_32 = 0b101 << DIVIDER_SELECT_OFF
        DIVIDER_SELECT_64 = 0b110 << DIVIDER_SELECT_OFF
        FEEDBACK_SELECT = bit(23)


    class R5:
        LD_PIN_MODE_OFF = 22
        LD_PIN_MODE_LOW = 0b00 << LD_PIN_MODE_OFF
        LD_PIN_MODE_LOCK_DETECT = 0b01 << LD_PIN_MODE_OFF
        LD_PIN_MODE_HIGH = 0b11 << LD_PIN_MODE_OFF


    r0 = Register(0b000)
    r1 = Register(0b001)
    r2 = Register(0b010)
    r3 = Register(0b011)
    r4 = Register(0b100)
    r5 = Register(0b101)

    int = RegVal(r0, R0.INT_OFF, 16)
    frac = RegVal(r0, R0.FRAC_OFF, 12)

    mod = RegVal(r1, R1.MOD_OFF, 12)
    phase = RegVal(r1, R1.PHASE_OFF, 12)
    prescaler_89 = RegBit(r1, R1.PRESCALER)
    phase_adj = RegBit(r1, R1.PHASE_ADJUST)

    couter_reset = RegBit(r2, R2.COUNTER_RESET_ENABLE)
    cp_three_state = RegBit(r2, R2.CP_THREE_STATE_ENABLE)
    power_down = RegBit(r2, R2.POWER_DOWN)
    pd_polarity_positive = RegBit(r2, R2.PD_POLARITY_POSITIVE)
    ldp_6ns = RegBit(r2, R2.LDP_6NS)
    ldf_intn = RegBit(r2, R2.LDF_INTN)
    charge_pump_current = RegVal(r2, R2.CHARGE_PUMP_CURRENT_OFF, 4)
    double_buffer = RegBit(r2, R2.DOUBLE_BUFFER_ENABLE)
    r_counter = RegVal(r2, R2.R_OFF, 10)
    ref_div2 = RegBit(r2, R2.RDIV2_ENABLE)
    ref_doubler = RegBit(r2, R2.REFERENCE_DOUBLER_ENABLE)
    muxout = RegVal(r2, R2.MUXOUT_OFF, 3)


    @property
    def low_spur(self):
        return bool((self.r2 >> self.R2.LOW_NOISE_SPUR_OFF) & 0b11)


    @low_spur.setter
    def low_spur(self, val):
        if val:
            self.r2 |= self.R2.LOW_NOISE_SPUR_MASK
        else:
            self.r2 &= ~self.R2.LOW_NOISE_SPUR_MASK


    clock_divider_val = RegVal(r3, R3.CLK_DIV_OFF, 12)
    clock_divider_mode = RegVal(r3, R3.CLK_DIV_MODE_OFF, 2)
    cycle_slip_reduction = RegBit(r3, R3.CSR)
    charge_cancelation = RegBit(r3, R3.CHARGE_CANCEL)
    antibacklash_pulse_3ns = RegBit(r3, R3.ABP)
    band_select_high = RegBit(r3, R3.BAND_SELECT_MODE)

    output_power = RegVal(r4, R4.OUTPUT_POWER_OFF, 2)
    output_enable = RegBit(r4, R4.RF_OUTPUT_ENABLE)
    aux_output_power = RegVal(r4, R4.AUX_OUTPUT_POWER_OFF, 2)
    aux_output_enable = RegBit(r4, R4.AUX_OUTPUT_ENABLE)
    aux_output_fundamental = RegBit(r4, R4.AUX_OUTPUT_SELECT)
    mute_till_lock_detect = RegBit(r4, R4.MTLD)
    vco_power_down = RegBit(r4, R4.VCO_POWER_DOWN)
    band_select_clock_div = RegVal(r4, R4.BAND_SELECT_CLOCK_DIV_OFF, 8)
    rf_divider = RegVal(r4, R4.DIVIDER_SELECT_OFF, 3)
    feedback_fundamental = RegBit(r4, R4.FEEDBACK_SELECT)

    ld_pin_mode = RegVal(r5, R5.LD_PIN_MODE_OFF, 2)

    OUTPUT_DIVIDER_1 = 0b000
    OUTPUT_DIVIDER_2 = 0b001
    OUTPUT_DIVIDER_4 = 0b010
    OUTPUT_DIVIDER_8 = 0b011
    OUTPUT_DIVIDER_16 = 0b100
    OUTPUT_DIVIDER_32 = 0b101
    OUTPUT_DIVIDER_64 = 0b110


    def __init__(self, spi, refclk):
        self.spi = spi
        # Technically, the maximum speed is 20MHz, but my logic analyzer does
        # not go that high
        self.spi.max_speed_hz = 5000000
        # CPOL = 0, CPHA = 0
        self.spi.mode = 0b00
        self.refclk = refclk
        # Initialize to some sort of known state
        self.init()


    def init(self):
        self.r5 = self.R5.LD_PIN_MODE_LOCK_DETECT
        self.r4 = self.R4.MTLD
        self.feedback_fundamental = True
        self.output_enable = True
        self.output_power = 3
        self.r3 = 0x00000000
        self.clock_divider_val = 150
        self.r2 = 0x00000000
        self.r_counter = 1
        self.charge_pump_current = 0b0111
        self.pd_polarity_positive = True
        self.r1 = 0x00000000
        self.r0 = 0x00000000


    def write(self, val):
        self.spi.xfer([(val >> x) & 0xff for x in range(24, -1, -8)])


    def set_frequency(self, fout, spacing = 100e3):
        # Based on https://ez.analog.com/thread/13743
        # TODO: Reference doubler/divider
        fpfd = self.refclk
        outdivval = 0
        outdiv = 1
        while fout * outdiv < 2200e6:
            outdiv *= 2
            outdivval += 1
        if self.feedback_fundamental:
            N = fout * outdiv / fpfd
        else:
            N = fout / fpfd
        INT = int(N)
        MOD = int(fpfd / spacing)
        FRAC = int((N - INT) * MOD)

        div = gcd(MOD, FRAC)
        MOD //= div
        FRAC //= div

        if MOD == 1:
            MOD = 2

        # TODO: PDF max error check

        # Band select clock speed
        fpfdm = fpfd / 1e6
        if self.band_select_high:
            bandseldiv = int(2 * fpfdm)
            if 2 * fpfdm - bandseldiv > 0:
                bandseldiv += 1
        else:
            bandseldiv = int(8 * fpfdm)
            if 8 * fpfd - bandseldiv > 0:
                bandseldiv += 1
        bandseldiv = min(bandseldiv, 255)

        # Write the register values
        r4 = insert_val(self.r4, bandseldiv,
                        self.R4.BAND_SELECT_CLOCK_DIV_OFF,
                        self.R4.BAND_SELECT_CLOCK_DIV_MASK)
        r4 = insert_val(r4, outdivval,
                        self.R4.DIVIDER_SELECT_OFF,
                        self.R4.DIVIDER_SELECT_MASK)
        r1 = insert_val(self.r1, MOD,
                        self.R1.MOD_OFF,
                        self.R1.MOD_MASK)
        r1 = insert_val(r1, 0b0001,
                        self.R1.PHASE_OFF,
                        self.R1.PHASE_MASK)
        r0 = insert_val(self.r0, FRAC,
                        self.R0.FRAC_OFF,
                        self.R0.FRAC_MASK)
        r0 = insert_val(r0, INT,
                        self.R0.INT_OFF,
                        self.R0.INT_MASK)
        self.r4 = r4
        self.r1 = r1
        self.r0 = r0


    def close(self):
        self.spi.close()
