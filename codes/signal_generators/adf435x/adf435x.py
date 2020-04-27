# datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/ADF4351.pdf


try:
    from collections import OrderedDict
    from ..interfaces import *
    from utilities.register import Register, Element, array
    from utilities.adapters.peripherals import SPI
except:
    from collections import OrderedDict
    from interfaces import *
    from register import Register, Element, array
    from peripherals import SPI

FREQ_MCLK = int(25e6)
POW2_32 = 2 ** 32
POW2_28 = 2 ** 28
POW2_12 = 2 ** 12
POW2_5 = 2 ** 5
BITS_PER_DEG = POW2_12 / DEGREES_IN_PI2



def _section_value(value, idx_msb, idx_lsb):
    mask = (2 ** (idx_msb - idx_lsb + 1) - 1) << idx_lsb
    return (value & mask) >> idx_lsb



def _value_key(dictionary):
    return {v: k for k, v in dictionary.items()}



class ADF435x(Device):
    FREQ_MCLK = int(25e6)


    class _DividerBase:
        DIVIDER_MIN = None
        DIVIDER_MAX = None
        DIVIDER_DEFAULT = None

        DENOMINATOR_BITS = 0
        DENOMINATOR_MAX = 2 ** DENOMINATOR_BITS - 1


        def __init__(self, adf, source):
            self._adf = adf

            # set divider first, source second.
            self.denominator_max = self.DENOMINATOR_MAX
            self._set_divider(self.DIVIDER_DEFAULT)
            self.set_input_source(source)


        @property
        def name(self):
            return self.__class__.__name__


        @property
        def status(self):
            return OrderedDict({'type'       : self.__class__.__name__,
                                'source_type': self.source.__class__.__name__,
                                'source_freq': self.source.freq,
                                'my_divider' : self.divider,
                                'my_freq'    : self.freq})


        @property
        def source(self):
            return self._source


        @property
        def divider(self):
            return self._divider


        @property
        def freq(self):
            return math.floor(self.source.freq / self.divider)


        def set_input_source(self, source):
            self._source = source
            self._frequency = self.freq


        def set_frequency(self, freq):
            self._adf._action = 'set_frequency {}'.format(freq)
            d = self.source.freq / freq
            self._set_divider(d)
            self._frequency = freq
            return True


        def restore_frequency(self):
            self._adf._action = 'restore_frequency'
            self.set_frequency(self._frequency)


        def _set_parameters(self, a, b, c):
            raise NotImplementedError()


        def _set_integer_mode(self, value = True):
            raise NotImplementedError()


        @property
        def is_in_integer_mode(self):
            raise NotImplementedError()


        def _set_divider(self, divider):
            a, b, c, _is_even_integer = self._validate_divider(divider)

            result = self._set_parameters(a, b, c)
            self._set_integer_mode(_is_even_integer)
            self._divider = divider
            self._post_set_divider()
            return result


        def _validate_divider(self, divider):
            assert self.DIVIDER_MIN <= divider <= self.DIVIDER_MAX, \
                'Must {} <=  ({})  <= {}'.format(self.DIVIDER_MIN, divider, self.DIVIDER_MAX)

            a = math.floor(divider)
            b = math.floor(self.denominator_max * (divider - a))
            c = self.denominator_max  # vcxo and pll use different denominators to fill up P3 register value,

            _is_even_integer = self._is_even_integer(divider)

            return a, b, c, _is_even_integer


        def _is_even_integer(self, divider):
            d = math.floor(divider)
            return d == divider and d % 2 == 0


        def _post_set_divider(self):
            pass


    class _ReferenceInput(_DividerBase):
        # The PFD frequency (fPFD) equation is
        # fPFD = REFIN × [(1 + D)/(R × (1 + T))] (2)
        # where:
        # REFIN is the reference input frequency.
        # D is the REFIN doubler bit (0 or 1).
        # R is the preset divide ratio of the binary 10-bit programmable
        # reference counter (1 to 1023).
        # T is the REFIN divide-by-2 bit (0 or 1).

        DIVIDER_DEFAULT = 1


        def __init__(self, adf, freq):
            self.set_frequency(freq)
            super().__init__(adf, None)


        @property
        def status(self):
            return OrderedDict({'type'   : self.__class__.__name__,
                                'my_freq': self.freq})


        def set_input_source(self, _ = None):
            self._source = None


        def _set_divider(self, _ = None):
            self._divider = 1


        @property
        def is_in_integer_mode(self):
            return True


        def set_frequency(self, freq):
            self._frequency = self._freq = freq


        def power_down(self, value = True):
            # The reference input stage is shown in Figure 16. The SW1 and
            # SW2 switches are normally closed. The SW3 switch is normally
            # open. When power-down is initiated, SW3 is closed, and SW1
            # and SW2 are opened. In this way, no loading of the REFIN pin
            # occurs during power-down.

            pass


    class _R_Counter(_DividerBase):
        # R Counter
        # The 10-bit R counter allows the input reference frequency
        # (REFIN) to be divided down to produce the reference clock
        # to the PFD. Division ratios from 1 to 1023 are allowed.

        DENOMINATOR_BITS = 10
        DENOMINATOR_MAX = 2 ** DENOMINATOR_BITS - 1

        DIVIDER_MIN = 1
        DIVIDER_MAX = DENOMINATOR_MAX
        DIVIDER_DEFAULT = DIVIDER_MAX

        DIVIDERS = range(1, DIVIDER_MIN, DIVIDER_MAX + 1)


        @property
        def freq(self):
            return math.floor(self.source.freq / self.divider)


        def set_input_source(self, source):
            self._source = source


        def set_frequency(self, freq):
            raise NotImplementedError()


        def restore_frequency(self):
            raise NotImplementedError()


        def _set_parameters(self, divider):
            self._adf._write_element_by_name('R_Counter', divider)


        def _set_integer_mode(self, value = True):
            raise NotImplementedError()


        @property
        def is_in_integer_mode(self):
            return True


        def _set_divider(self, divider):
            self._validate_divider(divider)
            self._set_parameters(divider)
            self._divider = divider
            self._post_set_divider()
            return True


        def _validate_divider(self, divider):
            assert divider in self.DIVIDERS, 'divider must be in {}.'.format(self.DIVIDERS)


    class _BandSelectClockDivider(_R_Counter):
        # The R counter output is used as the clock for the band select
        # logic. A programmable divider is provided at the R counter
        # output to allow division by an integer from 1 to 255; the divider
        # value is set using Bits[DB19:DB12] in Register 4 (R4). When the
        # required PFD frequency is higher than 125 kHz, the divide ratio
        # should be set to allow enough time for correct band selection.
        # Band selection takes 10 cycles of the PFD frequency, equal to
        # 80 µs. If faster lock times are required, Bit DB23 in Register 3
        # (R3) must be set to 1. This setting allows the user to select a
        # higher band select clock frequency of up to 500 kHz, which
        # speeds up the minimum band select time to 20 µs. For phase
        # adjustments and small (<1 MHz) frequency adjustments, the
        # user can disable VCO band selection by setting Bit DB28 in
        # Register 1 (R1) to 1. This setting selects the phase adjust feature.

        DENOMINATOR_BITS = 8
        DENOMINATOR_MAX = 2 ** DENOMINATOR_BITS - 1

        DIVIDER_MIN = 1
        DIVIDER_MAX = DENOMINATOR_MAX
        DIVIDER_DEFAULT = DIVIDER_MAX

        DIVIDERS = range(1, DIVIDER_MIN, DIVIDER_MAX + 1)


        def _set_parameters(self, divider):
            self._adf._write_element_by_name('Band_Select_Clock_Divider_Value', divider)


    class _RF_Divider(_R_Counter):
        # After band selection, normal PLL action resumes. The nominal
        # value of KV is 40 MHz/V when the N divider is driven from the
        # VCO output or from this value divided by D. D is the output
        # divider value if the N divider is driven from the RF divider output
        # (selected by programming Bits[DB22:DB20] in Register 4). The
        # ADF4351 contains linearization circuitry to minimize any variation of the product of ICP and KV to keep the loop bandwidth
        # constant.

        DIVIDERS = [2 ** i for i in range(7)]
        DIVIDER_CODES = {2 ** i: i for i in range(7)}

        DIVIDER_MIN = min(DIVIDERS)
        DIVIDER_MAX = max(DIVIDERS)
        DIVIDER_DEFAULT = DIVIDER_MAX


        def _set_parameters(self, divider):
            self._adf._write_element_by_name('RF_Divider_Select', self.DIVIDER_CODES[divider])


    class _ReferenceDivider(_R_Counter):
        # The reference divide-by-2 divides the reference signal by 2,
        # resulting in a 50% duty cycle PFD frequency. This is necessary
        # for the correct operation of the cycle slip reduction (CSR)
        # function. For more information, see the Cycle Slip Reduction
        # for Faster Lock Times section.
        
        DENOMINATOR_MAX = None

        DIVIDERS = (1, 2)
        DIVIDER_MIN = min(DIVIDERS)
        DIVIDER_MAX = max(DIVIDERS)
        DIVIDER_DEFAULT = DIVIDER_MIN


    class _ReferenceDoubler(_ReferenceDivider):
        # The on-chip reference doubler allows the input reference signal
        # to be doubled. Doubling the reference signal doubles the PFD
        # comparison frequency, which improves the noise performance of
        # the system. Doubling the PFD frequency usually improves noise
        # performance by 3 dB. Note that in fractional-N mode, the PFD
        # cannot operate above 32 MHz due to a limitation in the speed
        # of the Σ-Δ circuit of the N divider. For integer-N applications,
        # the PFD can operate up to 90 MHz.
        @property
        def freq(self):
            return math.floor(self.source.freq * self.divider)


    class _N_Divider(_DividerBase):

        INT_BITS = 16
        INT_MIN = {'4/5': 23, '8/9': 75}
        INT_MAX = 2 ** INT_BITS - 1

        MOD_BITS = 12
        MOD_MIN = 2
        MOD_MAX = 2 ** MOD_BITS - 1

        FRAC_BITS = 12
        FRAC_MIN = 0
        FRAC_MAX = MOD_MAX - 1

        DIVIDER_MIN = None
        DIVIDER_MAX = INT_MAX + FRAC_MAX / MOD_MAX
        DIVIDER_DEFAULT = INT_MAX

        DENOMINATOR_BITS = MOD_BITS
        DENOMINATOR_MAX = MOD_MAX

        #
        # B. Note that in fractional-N mode, the PFD
        # cannot operate above 32 MHz due to a limitation in the speed
        # of the Σ-Δ circuit of the N divider. For integer-N applications,
        # the PFD can operate up to 90 MHz.


        def _validate_divider(self, divider):
            assert self.DIVIDER_MIN <= divider <= self.DIVIDER_MAX, \
                'Must {} <=  ({})  <= {}'.format(self.DIVIDER_MIN, divider, self.DIVIDER_MAX)

            a = math.floor(divider)
            b = math.floor(self.denominator_max * (divider - a))
            c = self.denominator_max  # vcxo and pll use different denominators to fill up P3 register value,

            _is_even_integer = self._is_even_integer(divider)

            return a, b, c, _is_even_integer


        def _set_parameters(self, a, b, c):
            # RF N DIVIDER
            # The RF N divider allows a division ratio in the PLL feedback
            # path. The division ratio is determined by the INT, FRAC, and
            # MOD values, which build up this divider (see Figure 17)
            #
            # INT, FRAC, MOD, and R Counter Relationship
            # The INT, FRAC, and MOD values, in conjunction with the
            # R counter, make it possible to generate output frequencies that
            # are spaced by fractions of the PFD frequency. For more information, see the RF Synthesizer—A Worked Example section.
            # The RF VCO frequency (RFOUT) equation is
            #  RFOUT = fPFD × (INT + (FRAC/MOD)) (1)
            # where:
            #  RFOUT is the output frequency of the voltage controlled oscillator (VCO).
            #  INT is the preset divide ratio of the binary 16-bit counter
            #   (23 to 65,535 for the 4/5 prescaler;
            #    75 to 65,535 for the 8/9 prescaler).
            #  FRAC is the numerator of the fractional division (0 to MOD − 1).
            #  MOD is the preset fractional modulus (2 to 4095).

            # todo
            # INT = a  # 4/5: 23 to 65535 ,
            # FRAC = b  # 0 to MOD-1
            # MOD = c  # 2 to 4095

            self._adf._write_element_by_name('INT', a)
            self._adf._write_element_by_name('FRAC', b)
            self._adf._write_element_by_name('MOD', c)
            self._adf._confirm_double_buffer()


        def _set_integer_mode(self, value = True):
            # Integer-N Mode
            # If FRAC = 0 and the DB8 (LDF) bit in Register 2 is set to 1, the
            # synthesizer operates in integer-N mode. The DB8 bit in Register 2
            # should be set to 1 for integer-N digital lock detect.

            # The PFD includes a programmable delay element that sets the
            # width of the antibacklash pulse (ABP). This pulse ensures that
            # there is no dead zone in the PFD transfer function. Bit DB22 in
            # Register 3 (R3) is used to set the ABP as follows:
            #  When Bit DB22 is set to 0, the ABP width is programmed to
            # 6 ns, the recommended value for fractional-N applications.
            #  When Bit DB22 is set to 1, the ABP width is programmed to
            # 3 ns, the recommended value for integer-N applications.
            # For integer-N applications, the in-band phase noise is improved
            # by enabling the shorter pulse width. The PFD frequency can
            # operate up to 90 MHz in this mode. To operate with PFD
            # frequencies higher than 45 MHz, VCO band select must be disabled by setting the phase adjust bit (DB28) to 1 in Register 1.

            self._adf._write_element_by_name('LDF', int(bool(value)))
            self._adf.phase_detector.set_width_of_antibacklash_pulse(self, width = '3ns' if value else '6ns')


        @property
        def is_in_integer_mode(self):
            return self._adf.map.elements['LDF']['element'].value == 1


    class _Prescaler:
        PRESCALERS = {'4/5': 0, '8/9': 1}
        PRESCALERS_value_key = _value_key(PRESCALERS)


        def __init__(self, adf, prescaler):
            self._adf = adf
            self.set_prescaler(prescaler)


        @property
        def prescaler(self):
            return self.PRESCALERS_value_key[self._adf.map.elements['Prescaler_Value']['element'].value]


        def set_prescaler(self, prescaler = '4/5'):
            valids = self.PRESCALERS.keys()
            assert prescaler in valids, 'valid prescaler: {}'.format(valids)

            self._adf._write_element_by_name('Prescaler_Value', self.PRESCALERS[prescaler])


    class _Phaser(_R_Counter):

        DENOMINATOR_BITS = 12
        DENOMINATOR_MAX = 2 ** DENOMINATOR_BITS - 1

        DIVIDER_MIN = 0
        DIVIDER_MAX = DENOMINATOR_MAX
        DIVIDER_DEFAULT = 1


        def _set_parameters(self, divider):
            self._adf._write_element_by_name('Phase_Value', divider)


    class _PhaseDetector:
        # PHASE FREQUENCY DETECTOR (PFD) AND CHARGE PUMP

        # The phase frequency detector (PFD) takes inputs from the
        # R counter and N counter and produces an output proportional
        # to the phase and frequency difference between them. Figure 18
        # is a simplified schematic of the phase frequency detector.

        # The PFD includes a programmable delay element that sets the
        # width of the antibacklash pulse (ABP). This pulse ensures that
        # there is no dead zone in the PFD transfer function. Bit DB22 in
        # Register 3 (R3) is used to set the ABP as follows:
        #  When Bit DB22 is set to 0, the ABP width is programmed to
        # 6 ns, the recommended value for fractional-N applications.
        #  When Bit DB22 is set to 1, the ABP width is programmed to
        # 3 ns, the recommended value for integer-N applications.
        # For integer-N applications, the in-band phase noise is improved
        # by enabling the shorter pulse width. The PFD frequency can
        # operate up to 90 MHz in this mode. To operate with PFD
        # frequencies higher than 45 MHz, VCO band select must be disabled by setting the phase adjust bit (DB28) to 1 in Register 1.
        #  =====================================================================================
        ABP_WIDTH = {'6ns': 0,  # for fractional-N applications.
                     '3ns': 1}  # for integer-N applications}

        FREQUENCY_PFD_MAX = int(90e6)
        FREQUENCY_PFD_MAX_HALF = FREQUENCY_PFD_MAX / 2

        # B. Note that in fractional-N mode, the PFD
        # cannot operate above 32 MHz due to a limitation in the speed
        # of the Σ-Δ circuit of the N divider. For integer-N applications,
        # the PFD can operate up to 90 MHz.

        def __init__(self, adf: Device, n_divider, r_counter):
            self._adf = adf
            self.set_input_source(n_divider, r_counter)


        def freq_pfd_changed(self):
            self._valid_freq_pfd()

            if self.n_divider.freq > self.FREQUENCY_PFD_MAX_HALF or self.n_divider.freq > self.FREQUENCY_PFD_MAX_HALF:
                self._adf.vco.enable_vco_band_select(False)


        def _valid_freq_pfd(self):
            assert self.n_divider.freq <= self.FREQUENCY_PFD_MAX, \
                'freq of n_divider need to be lower than {}'.format(self.FREQUENCY_PFD_MAX)
            assert self.r_counter.freq <= self.FREQUENCY_PFD_MAX, \
                'freq of r_counter need to be lower than {}'.format(self.FREQUENCY_PFD_MAX)


        def set_input_source(self, n_divider, r_counter):
            self.n_divider = n_divider
            self.r_counter = r_counter
            self._valid_freq_pfd()


        def set_width_of_antibacklash_pulse(self, width = '6ns'):
            valids = self.ABP_WIDTH.keys()
            assert width in valids, 'valid width: {}'.format(valids)

            self._adf._write_element_by_name('ABP', self.ABP_WIDTH[width])


    class _BandSelector:
        pass


    class _NoiseMode:
        pass


    class _ChargePump:
        pass


    class _MuxOut:
        # MUXOUT AND LOCK DETECT
        # The multiplexer output on the ADF4351 allows the user to access
        # various internal points on the chip. The state of MUXOUT is
        # controlled by the M3, M2, and M1 bits in Register 2 (see Figure 26).
        # Figure 19 shows the MUXOUT section in block diagram form.

        SOURCES = {'THREE_STATE'        : 0,
                   'D_VDD'              : 1,
                   'D_GND'              : 2,
                   'R_COUNTER'          : 3,
                   'N_DIVIDER'          : 4,
                   'ANALOG_LOCK_DETECT' : 5,
                   'DIGITAL_LOCK_DETECT': 6}


        def __init__(self, adf):
            self._adf = adf


        def select_source(self, source = 'N_DIVIDER'):
            self._adf._write_element_by_name('MUXOUT', self.SOURCES[source])


    class _VCO:

        # VCO
        # The VCO core in the ADF4351 consists of three separate VCOs,
        # each of which uses 16 overlapping bands, as shown in Figure 20,
        # to allow a wide frequency range to be covered without a large
        # VCO sensitivity (KV) and resultant poor phase noise and spurious performance.
        #
        # The correct VCO and band are selected automatically by the
        # VCO and band select logic at power-up or whenever Register 0
        # (R0) is updated.
        # VCO and band selection take 10 PFD cycles multiplied by the
        # value of the band select clock divider. The VCO VTUNE is disconnected from the output of the loop filter and is connected to an
        # internal reference voltage.

        # The R counter output is used as the clock for the band select
        # logic. A programmable divider is provided at the R counter
        # output to allow division by an integer from 1 to 255; the divider
        # value is set using Bits[DB19:DB12] in Register 4 (R4). When the
        # required PFD frequency is higher than 125 kHz, the divide ratio
        # should be set to allow enough time for correct band selection.
        # Band selection takes 10 cycles of the PFD frequency, equal to
        # 80 µs. If faster lock times are required, Bit DB23 in Register 3
        # (R3) must be set to 1. This setting allows the user to select a
        # higher band select clock frequency of up to 500 kHz, which
        # speeds up the minimum band select time to 20 µs. For phase
        # adjustments and small (<1 MHz) frequency adjustments, the
        # user can disable VCO band selection by setting Bit DB28 in
        # Register 1 (R1) to 1. This setting selects the phase adjust feature.
        # After band selection, normal PLL action resumes. The nominal
        # value of KV is 40 MHz/V when the N divider is driven from the
        # VCO output or from this value divided by D. D is the output
        # divider value if the N divider is driven from the RF divider output
        # (selected by programming Bits[DB22:DB20] in Register 4). The
        # ADF4351 contains linearization circuitry to minimize any variation of the product of ICP and KV to keep the loop bandwidth
        # constant.
        # The VCO shows variation of KV as the VTUNE varies within the
        # band and from band to band. For wideband applications covering a wide frequency range (and changing output dividers), a
        # value of 40 MHz/V provides the most accurate KV because this
        # value is closest to an average value. Figure 21 shows how KV
        # varies with fundamental VCO frequency, along with an average
        # value for the frequency band. Users may prefer this figure when
        # using narrow-band designs.
        BAND_SELECT_CLOCK_MODES = {'LOW': 0, 'HIGH': 1}

        # Note that the ADF4351 VCO operates in the frequency range
        # of 2.2 GHz to 4.4 GHz. 

        def __init__(self, adf):
            self._adf = adf


        def enable_vco_band_select(self, value = True):
            # Band selection takes 10 cycles of the PFD frequency, equal to
            # 80 µs. If faster lock times are required, Bit DB23 in Register 3
            # (R3) must be set to 1. This setting allows the user to select a
            # higher band select clock frequency of up to 500 kHz, which
            # speeds up the minimum band select time to 20 µs. For phase
            # adjustments and small (<1 MHz) frequency adjustments, the
            # user can disable VCO band selection by setting Bit DB28 in
            # Register 1 (R1) to 1. This setting selects the phase adjust feature.

            self._adf._write_element_by_name('Phase_Adjust', int(not bool(value)))


        def select_band(self):
            # The correct VCO and band are selected automatically by the
            # VCO and band select logic at power-up or whenever Register 0 (R0) is updated.
            #
            # When the required PFD frequency is higher than 125 kHz, the divide ratio
            # should be set to allow enough time for correct band selection.
            pass


        def set_band_select_clock_mode(self, mode = 'HIGH'):
            # Band selection takes 10 cycles of the PFD frequency, equal to
            # 80 µs. If faster lock times are required, Bit DB23 in Register 3
            # (R3) must be set to 1. This setting allows the user to select a
            # higher band select clock frequency of up to 500 kHz, which
            # speeds up the minimum band select time to 20 µs. For phase
            # adjustments and small (<1 MHz) frequency adjustments, the
            # user can disable VCO band selection by setting Bit DB28 in
            # Register 1 (R1) to 1. This setting selects the phase adjust feature.

            valids = self.BAND_SELECT_CLOCK_MODES.keys()
            assert mode in valids, 'valid mode: {}'.format(valids)

            self._adf._write_element_by_name('Band_Select_Clock_Mode', self.BAND_SELECT_CLOCK_MODES[mode])


    class _RF_Output:
        # The RFOUTA+ and RFOUTA− pins of the ADF4351 are connected
        # to the collectors of an NPN differential pair driven by buffered
        # outputs of the VCO, as shown in Figure 22.

        # To allow the user to optimize the power dissipation vs. the
        # output power requirements, the tail current of the differential
        # pair is programmable using Bits[DB4:DB3] in Register 4 (R4).
        # Four current levels can be set. These levels give output power
        # levels of −4 dBm, −1 dBm, +2 dBm, and +5 dBm, using a 50 Ω
        # resistor to AVDD and ac coupling into a 50 Ω load. Alternatively,
        # both outputs can be combined in a 1 + 1:1 transformer or a 180°
        # microstrip coupler (see the Output Matching section).
        # If the outputs are used individually, the optimum output stage
        # consists of a shunt inductor to VVCO. The unused complementary
        # output must be terminated with a similar circuit to the used output.
        # An auxiliary output stage exists on the RFOUTB+ and RFOUTB−
        # pins, providing a second set of differential outputs that can be
        # used to drive another circuit. The auxiliary output stage can be
        # used only if the primary outputs are enabled. If the auxiliary
        # output stage is not used, it can be powered down.
        # Another feature of the ADF4351 is that the supply current to
        # the RF output stage can be shut down until the part achieves
        # lock, as measured by the digital lock detect circuitry. This
        # feature is enabled by setting the mute till lock detect (MTLD)
        # bit in Register 4 (R4).

        POWER_DBM_LEVELS = {-4: 0, -1: 1, 2: 2, 5: 3}


        def __init__(self, adf):
            self._adf = adf


        def power_down(self, value = True):
            pass


        def set_output_power(self, power_level = -4):
            self._adf._write_element_by_name('Output_Power', self.POWER_DBM_LEVELS[power_level])


        def mute_till_lock_detected(self, value = True):
            self._adf._write_element_by_name('MTLD', int(bool(value)))


    class _AuxOutput(_RF_Output):
        pass


    def __init__(self, spi, ss, ss_polarity = 1,
                 freq = FREQ_DEFAULT, freq_correction = 0, phase = PHASE_DEFAULT, shape = SHAPE_DEFAULT,
                 freq_mclk = FREQ_MCLK,
                 registers_map = None, registers_values = None,
                 commands = None):

        super().__init__(freq = freq, freq_correction = freq_correction, phase = phase, shape = shape,
                         registers_map = registers_map, registers_values = registers_values,
                         commands = commands)

        self._spi = SPI(spi, ss, ss_polarity = ss_polarity)
        self.freq_mclk = freq_mclk

        self.init()


    def enable_rf_divider_select_double_buffered(self, value = True):
        # The divider select value in Register 4
        # (R4) is also double buffered, but only if the DB13 bit of
        # Register 2 (R2) is set to 1.

        self._write_element_by_name('Double_Buffer', int(bool(value)))


    def _build(self):

        # internal components
        self.mclk = self._ReferenceInput(self, self.freq_mclk)
        self.doubler = self._Doubler(self, self.mclk)
        self.r_counter = self._R_Counter(self, self.doubler)
        self.divider_2 = self._2_Divider(self, self.r_counter)
        self.n_divider = self._N_Divider(self, self.divider_2)
        self.phase_detector = self._PhaseDetector(self, self.n_divider, self.r_counter)

        self.band_select_clock_divider = self._BandSelectClockDivider(self, self.r_counter)
        self.vco = self._VCO(self)

        self.plls = {k: self._PLL(self, name = k) for k in self._PLL.NAMES.keys()}
        self.multisynths = [self._Multisynth(self, i) for i in range(self.n_channels)]
        self.clocks = [self._Clock(self, i) for i in range(self.n_channels)]
        self.spread_spectrum = self._SpreadSpectrum(self)  # PLL_A as source
        if self.HAS_VCXO:
            self.vcxo = self._VCXO(self)  # PLL_B as source, changes PLL_B's denominator(P3) if used.


    def init(self):
        self._action = 'init'

        self._build()

        self.reset_plls()
        self.start()


    @property
    def is_virtual_device(self):
        return self._spi._spi is None


    @property
    def status(self):
        raise NotImplementedError()


    @property
    def freq_resolution(self):
        raise NotImplementedError()


    @property
    def phase_resolution(self):
        raise NotImplementedError()


    def apply_signal(self, freq = None, freq_correction = None, phase = None, shape = None):
        raise NotImplementedError()


    def set_frequency(self, freq, idx = None, freq_correction = None):
        self._action = 'set_frequency {} idx {}'.format(freq, idx)
        raise NotImplementedError()


    def set_phase(self, phase, idx = None):
        self._action = 'set_phase {} idx {}'.format(phase, idx)
        raise NotImplementedError()


    def select_freq_source(self, idx):
        raise NotImplementedError()


    def select_phase_source(self, idx):
        raise NotImplementedError()


    @property
    def current_frequency(self):
        raise NotImplementedError()


    @property
    def current_phase(self):
        raise NotImplementedError()


    def enable_output(self, value = True):
        self._action = 'enable_output: {}'.format(value)
        raise NotImplementedError()


    def enable_output_channel(self, idx, value = True):
        self._action = 'enable_output_channel: {} {}'.format(idx, value)
        raise NotImplementedError()


    # =================================================================
    def write_all_registers(self, reset = False):
        for reg in self.map._registers[::-1]:
            self._write_register(reg, reset = reset)


    def _write_register(self, register, reset = False):
        super()._write_register(register, reset = reset)
        self._spi.write(register.bytes)


    def _confirm_double_buffer(self):
        self._write_register(self.map._registers[0])
