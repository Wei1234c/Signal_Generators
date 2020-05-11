# datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/ADF4351.pdf


try:
    from collections import OrderedDict
    from ..interfaces import *
    from .registers_map import _get_registers_map, array
except:
    from collections import OrderedDict
    from interfaces import *
    from registers_map import _get_registers_map, array



def _section_value(value, idx_msb, idx_lsb):
    mask = (2 ** (idx_msb - idx_lsb + 1) - 1) << idx_lsb
    return (value & mask) >> idx_lsb



def _value_key(dictionary):
    return {v: k for k, v in dictionary.items()}



def _is_integer(n):
    return math.floor(n) == n



def _is_even_integer(n):
    i = math.floor(n)
    return i == n and i % 2 == 0



def _freq_trim(n):
    return n  # for accuracy
    # return math.floor(n)
    # return round(n)



class ADF4351(Device):
    FREQ_MCLK = int(25e6)
    INITIAL_REGISTERS_VALUES = (0x3C0000, 0x80087D1, 0x30041C2, 0xE404B3, 0x932224, 0X580005)


    class _DividerBase:

        DENOMINATOR_BITS = 0
        DENOMINATOR_MAX = 2 ** DENOMINATOR_BITS - 1

        DIVIDER_MIN = None
        DIVIDER_MAX = None
        DIVIDER_DEFAULT = None


        def __init__(self, adf, source):
            self._adf = adf
            self._denominator = self.DENOMINATOR_MAX
            self._set_divider(self.DIVIDER_DEFAULT)
            self._set_input_source(source)


        @property
        def status(self):
            return OrderedDict({'type'       : self.__class__.__name__,
                                'source_type': self.source.__class__.__name__,
                                'source_freq': self.source.freq,
                                'my_divider' : self.divider,
                                'is_integer' : self.is_in_integer_mode,
                                'my_freq'    : self.freq})


        @property
        def freq(self):
            return _freq_trim(self.source.freq / self.divider)


        @property
        def source(self):
            return self._source


        @property
        def divider(self):
            return self._divider


        def set_frequency(self, freq):
            self._adf._action = 'set_frequency {}'.format(freq)
            d = self.source.freq / freq
            self._set_divider(d)
            return True


        def _set_input_source(self, source):
            self._source = source
            self._frequency = self.freq  # validate freq


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
            a, b, c, is_integer = self._validate_divider(divider)

            self._set_parameters(a, b, c)
            self._set_integer_mode(is_integer)
            self._divider = divider
            self._post_set_divider()
            return True


        def _validate_divider(self, divider):
            assert self.DIVIDER_MIN <= divider <= self.DIVIDER_MAX, \
                'Must {} <=  ({})  <= {}'.format(self.DIVIDER_MIN, divider, self.DIVIDER_MAX)

            a = math.floor(divider)
            c = self._denominator
            b = math.floor(c * (divider - a))

            is_integer = _is_integer(divider)

            return a, b, c, is_integer


        def _post_set_divider(self):
            pass


    class _IntegerDivider(_DividerBase):
        # continuous
        DIVIDER_BITS = 1

        # if discrete
        DIVIDERS = None

        # default
        DIVIDER_DEFAULT = None


        def __init__(self, adf, source):
            self._divider_min = 1 if self.DIVIDERS is None else min(self.DIVIDERS)
            self._divider_max = 2 ** self.DIVIDER_BITS - 1 if self.DIVIDERS is None else max(self.DIVIDERS)
            if self.DIVIDER_DEFAULT is None:
                self.DIVIDER_DEFAULT = self._divider_max
            super().__init__(adf, source)


        def _set_divider(self, divider):
            self._validate_divider(divider)
            self._set_parameters(divider)
            self._divider = divider
            self._post_set_divider()
            return True


        def _validate_divider(self, divider):
            assert _is_integer(divider), 'divider {} need to be integer.'.format(divider)

            if self.DIVIDERS is not None:
                assert divider in self.DIVIDERS, 'valid divider: {}'.format(self.DIVIDERS)
            else:
                assert self._divider_min <= divider <= self._divider_max, \
                    'Must {} <=  ({})  <= {}'.format(self._divider_min, divider, self._divider_max)


        def _set_parameters(self, divider):
            pass


        @property
        def is_in_integer_mode(self):
            return True


        # ===== not used =====

        def _set_integer_mode(self, value = True):
            raise NotImplementedError()


        def set_frequency(self, freq):
            raise NotImplementedError()


        def restore_frequency(self):
            raise NotImplementedError()


    class _ReferenceInput(_IntegerDivider):

        # The PFD frequency (fPFD) equation is
        # fPFD = REFIN × [(1 + D)/(R × (1 + T))] (2)
        # where:
        # REFIN is the reference input frequency.
        # D is the REFIN doubler bit (0 or 1).
        # R is the preset divide ratio of the binary 10-bit programmable reference counter (1 to 1023).
        # T is the REFIN divide-by-2 bit (0 or 1).

        FREQ_MIN = 10e6
        FREQ_MAX = 250e6


        def __init__(self, adf, freq):
            self.set_frequency(freq)
            super().__init__(adf, None)


        @property
        def status(self):
            return OrderedDict({'type'   : self.__class__.__name__,
                                'my_freq': self.freq})


        @property
        def freq(self):
            assert self.FREQ_MIN <= self._freq <= self.FREQ_MAX, \
                'freq_ref ranges between {:0.1e} ~ {:0.1e} Hz, now is {:0.1e} Hz'.format(self.FREQ_MIN, self.FREQ_MAX,
                                                                                         self._freq)
            return self._freq


        def set_frequency(self, freq):
            self._freq = freq


    class _ReferenceDivider(_IntegerDivider):
        # The reference divide-by-2 divides the reference signal by 2,
        # resulting in a 50% duty cycle PFD frequency. This is necessary
        # for the correct operation of the cycle slip reduction (CSR)
        # function. For more information, see the Cycle Slip Reduction
        # for Faster Lock Times section.

        DIVIDERS = (1, 2)


        @property
        def freq(self):
            # Setting the DB24 bit to 1 inserts a divide-by-2 toggle flip-flop between the R counter and
            # the PFD, which extends the maximum REFIN input rate. This function allows a 50% duty cycle
            # signal to appear at the PFD input, which is necessary for cycle slip reduction.

            if (not self.enabled) and hasattr(self._adf, 'phase_frequency_detector'):
                assert not self._adf.phase_frequency_detector.cycle_slip_reduction_enabled, \
                    'CSR is enabled, need to enable freq_ref divided by 2.'

            freq = _freq_trim(self.source.freq / self.divider)

            return freq


        @property
        def enabled(self):
            return self._adf.map.value_of_element('RDIV2') == 1


        def _by_2(self, value = True):
            self._set_divider(2 if value else 1)


        def _set_parameters(self, divider):
            self._adf._write_element_by_name('RDIV2', int(divider == 2))
            self._adf._confirm_double_buffer()


    class _ReferenceDoubler(_ReferenceDivider):

        # The on-chip reference doubler allows the input reference signal to be doubled.
        # Doubling the reference signal doubles the PFD comparison frequency, which improves
        # the noise performance of the system. Doubling the PFD frequency usually improves
        # noise performance by 3 dB.

        FREQ_REF_MAX = 30e6


        @property
        def freq(self):
            if self.enabled:
                # The maximum allowable REFIN frequency when the doubler is enabled is 30 MHz.

                assert self.source.freq <= self.FREQ_REF_MAX, \
                    'Doubler is enabled, freq_ref should be less than 30 MHz.'

                # When the doubler is enabled:
                # . BOTH the rising and falling edges of REFIN become active edges at the PFD input.
                # . If the low spur mode is selected, the in-band phase noise performance is sensitive to
                #   the REFIN duty cycle. The phase noise degradation can be as much as 5 dB
                #   for REFIN duty cycles outside a 45% to 55% range.

                if self._adf.noise_control.mode == 'LOW_SPUR_MODE':
                    assert self._adf.ref_divider.enabled, \
                        '''LOW_SPUR_MODE is enabled, in-band phase noise performance is sensitive to the REFIN duty cycle.
                         Keep Ref_divided by 2.'''

            return _freq_trim(self.source.freq * self.divider)


        @property
        def enabled(self):
            return self._adf.map.value_of_element('Reference_Doubler') == 1


        def _set_parameters(self, divider):
            # Setting the DB25 bit to 0 disables the doubler and feeds the REFIN signal directly into
            # the 10-bit R counter.
            # Setting this bit to 1 multiplies the REFIN frequency by a factor of 2 before feeding it
            # into the 10-bit R counter.
            # When the doubler is disabled, the REFIN falling edge is the active edge at the PFD input
            # to the fractional synthesizer.
            # When the doubler is enabled, BOTH the rising and falling edges of REFIN become active edges at the
            # PFD input.
            # When the doubler is enabled and the low spur mode is selected, the in-band
            # phase noise performance is sensitive to the REFIN duty cycle. The phase noise degradation
            # can be as much as 5 dB for REFIN duty cycles outside a 45% to 55% range.
            # The phase noise is insensitive to the REFIN duty cycle in the low noise mode and when the doubler is
            # disabled. The maximum allowable REFIN frequency when the doubler is enabled is 30 MHz.

            self._adf._write_element_by_name('Reference_Doubler', int(divider == 2))
            self._adf._confirm_double_buffer()


    class _R_Counter(_IntegerDivider):
        # R Counter
        # The 10-bit R counter allows the input reference frequency
        # (REFIN) to be divided down to produce the reference clock
        # to the PFD. Division ratios from 1 to 1023 are allowed.

        DIVIDER_BITS = 10
        DIVIDER_DEFAULT = 1  # so freq_pfd can be as high as possble.


        def _set_parameters(self, divider):
            # The 10-bit R counter (Bits[DB23:DB14]) allows the input reference frequency (REFIN) to be
            # divided down to produce the reference clock to the PFD. Division ratios from 1 to 1023 are
            # allowed.

            self._adf._write_element_by_name('R_Counter', divider)
            self._adf._confirm_double_buffer()


    class _BandSelectClockDivider(_IntegerDivider):
        # The R counter output is used as the clock for the band select logic. A
        # programmable divider is provided at the R counter output to allow division by an
        # integer from 1 to 255; the divider value is set using Bits[DB19:DB12] in Register 4 (R4).

        DIVIDER_BITS = 8
        DIVIDER_MAX = 254

        MODES = {'LOW': 0, 'HIGH': 1}
        MODES_value_key = _value_key(MODES)
        BAND_SELECT_FREQ_MAX = {'LOW': 125e3, 'HIGH': 500e3}


        # BAND_SELECT_TIME = {'LOW': 8e-6, 'HIGH': 2e-6}

        def __init__(self, adf, source, mode = 'HIGH'):
            self._adf = adf
            self._set_mode(mode)
            super().__init__(adf, source)
            self._divider_max = self.DIVIDER_MAX


        @property
        def status(self):
            return OrderedDict({'type'       : self.__class__.__name__,
                                'source_type': self.source.__class__.__name__,
                                'source_freq': self.source.freq,
                                'enabled'    : self.band_select_enabled,
                                'mode'       : self.mode,
                                'my_divider' : self.divider,
                                'is_integer' : self.is_in_integer_mode,
                                'my_freq'    : self.freq})


        @property
        def freq(self):
            freq = _freq_trim(self.source.freq / self.divider)

            # When the required PFD frequency is higher than 125 kHz, the divide ratio
            # should be set to allow enough time for correct band selection. Band selection
            # takes 10 cycles of the PFD frequency, equal to 80 µs. If faster lock times are
            # required, Bit DB23 in Register 3 (R3) must be set to 1. This setting allows the
            # user to select a higher band select clock frequency of up to 500 kHz, which speeds
            # up the minimum band select time to 20 µs.
            # For phase adjustments and small (<1 MHz) frequency adjustments, the user can
            # disable VCO band selection by setting Bit DB28 in Register 1 (R1) to 1.
            # This setting selects the phase adjust feature.
            assert freq <= self.BAND_SELECT_FREQ_MAX[self.mode], 'Band select mode {}, mus freq {} <= {} Hz'.format(
                self.mode, freq, self.BAND_SELECT_FREQ_MAX[self.mode])

            return freq


        @property
        def mode(self):
            return self.MODES_value_key[self._adf.map.value_of_element('Band_Select_Clock_Mode')]


        def _set_mode(self, mode = 'HIGH'):
            # Setting the DB23 bit to 0 is recommended for low PFD (<125 kHz) values.
            # Setting the DB23 bit to 1 selects a faster logic sequence of band selection,
            # which is suitable for high PFD frequencies and is necessary for fast lock applications.
            # For the faster band select logic modes (DB23 set to 1), the value of the band select clock divider
            # must be less than or equal to 254.
            #
            # Band selection takes 10 cycles of the PFD frequency, equal to 80 µs.
            # If faster lock times are required, Bit DB23 in Register 3 (R3) must be set to 1.
            # This setting allows the user to select a higher band select clock frequency of up to 500 kHz,
            # which speeds up the minimum band select time to 20 µs.
            # For phase adjustments and small (<1 MHz) frequency adjustments, the user can disable VCO
            # band selection by setting Bit DB28 in Register 1 (R1) to 1. This setting selects the
            # phase adjust feature.

            # The correct VCO and band are selected automatically by the
            # VCO and band select logic at power-up or whenever Register 0 (R0) is updated.
            #
            # When the required PFD frequency is higher than 125 kHz, the divide ratio
            # should be set to allow enough time for correct band selection.

            valids = self.MODES.keys()
            assert mode in valids, 'valid mode: {}'.format(valids)

            self._adf._write_element_by_name('Band_Select_Clock_Mode', self.MODES[mode])


        def _refresh_divider(self):
            if self.source.freq / self.DIVIDER_MAX > self.BAND_SELECT_FREQ_MAX['LOW']:
                self._set_mode('HIGH')

            # _ = self._set_mode('HIGH') if self.source.freq / self.DIVIDER_MAX > self.BAND_SELECT_FREQ_MAX['LOW'] else \
            #     self._set_mode('LOW')

            # The on-chip multiplexer is controlled by Bits[DB28:DB26]
            # (see Figure 26). Note that N counter output must be disabled
            # for VCO band selection to operate correctly
            assert self._adf.muxout.source_type != 'N_DIVIDER', \
                'N counter output must be disabled @ MaxOut for VCO band selection to operate correctly.'

            # freq_band_select <= self.BAND_SELECT_FREQ_MAX[self.mode]
            # freq_pfd / band_select_divider <= self.BAND_SELECT_FREQ_MAX[self.mode]
            # band_select_divider => freq_pfd / self.BAND_SELECT_FREQ_MAX[self.mode]
            required_divider = math.ceil(self.source.freq / self.BAND_SELECT_FREQ_MAX[self.mode])
            divider = min((required_divider, self._divider_max))
            self._set_divider(divider)
            _ = self.freq  # validate
            return self.mode, required_divider, divider


        def _set_parameters(self, divider):
            # The correct VCO and band are selected automatically by the
            # VCO and band select logic at power-up or whenever Register 0 (R0) is updated.
            #
            # When the required PFD frequency is higher than 125 kHz, the divide ratio
            # should be set to allow enough time for correct band selection.

            # Bits[DB19:DB12] set a divider for the band select logic clock input. By default, the
            # output of the R counter is the value used to clock the band select logic, but, if this
            # value is too high (>125 kHz), a divider can be switched on to divide the R counter output
            # to a smaller value (see Figure 28).

            self._adf._write_element_by_name('Band_Select_Clock_Divider_Value', divider)


        @property
        def band_select_enabled(self):
            return not self._adf.phaser.phase_adjust_enabled


        def _enable_band_select(self, value = True):
            # Band selection takes 10 cycles of the PFD frequency, equal to 80 µs.
            # If faster lock times are required, Bit DB23 in Register 3 (R3) must be set to 1.
            # This setting allows the user to select a higher band select clock frequency of up to 500 kHz,
            # which speeds up the minimum band select time to 20 µs.
            # For phase adjustments and small (<1 MHz) frequency adjustments, the user can disable VCO
            # band selection by setting Bit DB28 in Register 1 (R1) to 1. This setting selects the
            # phase adjust feature.
            if value:
                self._refresh_divider()

            self._adf.phaser._enable_phase_adjust(not value)


    class _ClockDivider(_IntegerDivider):
        DIVIDER_BITS = 12
        DIVIDER_DEFAULT = 150

        MODES = {'CLOCK_DIVIDER_OFF': 0, 'FAST_LOCK_ENABLE': 1, 'RESYNC_ENABLE': 2}
        MODES_value_key = _value_key(MODES)


        def __init__(self, adf, source, mode = 'CLOCK_DIVIDER_OFF'):
            super().__init__(adf, source)
            self._set_mode(mode)  # todo: set mode resync ?


        @property
        def status(self):
            return OrderedDict({'type'       : self.__class__.__name__,
                                'source_type': self.source.__class__.__name__,
                                'source_freq': self.source.freq,
                                'mode'       : self.mode,
                                'my_divider' : self.divider,
                                'is_integer' : self.is_in_integer_mode,
                                'my_freq'    : self.freq})


        @property
        def mode(self):
            return self.MODES_value_key[self._adf.map.value_of_element('Clock_Divider_Mode')]


        def _set_mode(self, mode = 'CLOCK_DIVIDER_OFF'):
            # Bits[DB16:DB15] must be set to 10 to activate phase resync (see the Phase Resync section).
            # These bits must be set to 01 to activate fast lock (see the Fast Lock Timer and Register
            # Sequences section). Setting Bits[DB16:DB15] to 00 disables the clock divider (see Figure
            # 27).

            valids = self.MODES.keys()
            assert mode in valids, 'valid mode: {}'.format(valids)

            self._adf._write_element_by_name('Clock_Divider_Mode', self.MODES[mode])


        def _set_parameters(self, divider):
            # Bits[DB14:DB3] set the 12-bit clock divider value. This value is the timeout counter for
            # activation of phase resync (see the Phase Resync section). The clock divider value also
            # sets the timeout counter for fast lock (see the Fast Lock Timer and Register Sequences
            # section).

            self._adf._write_element_by_name('Clock_Divider_Value', divider)


    class _PhaseFrequencyDetector(_IntegerDivider):
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
        # frequencies higher than 45 MHz, VCO band select must be disabled
        # by setting the phase adjust bit (DB28) to 1 in Register 1.
        #  =====================================================================================

        # B. Note that in fractional-N mode, the PFD
        # cannot operate above 32 MHz due to a limitation in the speed
        # of the Σ-Δ circuit of the N divider. For integer-N applications,
        # the PFD can operate up to 90 MHz.

        ABP_WIDTH = {'6ns': 0,  # for fractional-N applications.
                     '3ns': 1}  # for integer-N applications}

        FREQUENCY_PFD_MAX = int(90e6)
        FREQUENCY_PFD_MAX_HALF = FREQUENCY_PFD_MAX / 2

        LOCK_DETECT_PIN_OPERATIONS = {'LOW'                : 0,
                                      'DIGITAL_LOCK_DETECT': 1,
                                      'HIGH'               : 3}


        def __init__(self, adf, source,
                     CSR_enabled = True, LD_pin_mode = 'DIGITAL_LOCK_DETECT', polarity_non_inverting = True):

            self._feedback_source = None
            super().__init__(adf, source)

            self._enable_cycle_slip_reduction(CSR_enabled)
            self._set_lock_detect_pin_operation(value = LD_pin_mode)
            self._set_polarity(non_inverting = polarity_non_inverting)


        @property
        def source(self):
            return self._source


        @property
        def reference_source(self):
            return self.source


        @property
        def feedback_source(self):
            return self._feedback_source


        @property
        def freq(self):
            self._valid_freq_pfd(self.source.freq)
            return self.source.freq


        @property
        def freq_pfd(self):
            return self.freq


        def _set_reference_source(self, source):
            self._set_input_source(source)


        def _set_feedback_source(self, source):
            self._feedback_source = source

            # =====================================================================


        def _valid_freq_pfd(self, freq):
            # For integer-N applications, the in-band phase noise is improved
            # by enabling the shorter pulse width. The PFD frequency can
            # operate up to 90 MHz in this mode.

            assert freq <= self.FREQUENCY_PFD_MAX, \
                'freq_pfd need to be lower than {}'.format(self.FREQUENCY_PFD_MAX)

            # To operate with PFD frequencies higher than 45 MHz, VCO band select must be disabled by
            # setting the phase adjust bit (DB28) to 1 in Register 1.

            if freq > self.FREQUENCY_PFD_MAX_HALF:
                assert not self._adf.vco.band_select_enabled, \
                    'PFD frequencies is higher than 45 MHz, VCO band select must be disabled'


        def _set_antibacklash_pulse_width(self, as_3_ns = True):
            # Bit DB22 sets the PFD antibacklash pulse width.
            # . When Bit DB22 is set to 0, the PFD antibacklash pulse width is 6 ns.
            #   This setting is recommended for fractional-N use.
            # . When Bit DB22 is set to 1, the PFD antibacklash pulse width is 3 ns,
            #   which results in phase noise and spur improvements in integer-N operation.
            #   For fractional-N operation, the 3 ns setting is not recommended.

            self._adf._write_element_by_name('ABP', int(as_3_ns))


        def _enable_lock_detect_function(self, value = True):
            # The DB8 bit configures the lock detect function (LDF). The LDF controls the number of PFD
            # cycles monitored by the lock detect circuit to ascertain whether lock has been achieved.
            # When DB8 is set to 0, the number of PFD cycles monitored is 40.
            # When DB8 is set to 1, the number of PFD cycles monitored is 5.
            # It is recommended that the DB8 bit be set to 0 for fractional-N mode and to 1 for integer-N mode.

            self._adf._write_element_by_name('LDF', int(bool(value)))


        @property
        def lock_detect_function_enabled(self):
            return self._adf.rf_n_divider.is_in_integer_mode


        def _enable_lock_detect_precision(self, value = True):
            # The lock detect precision bit (Bit DB7) sets the comparison window in the lock detect
            # circuit.
            # When DB7 is set to 0, the comparison window is 10 ns;
            # when DB7 is set to 1, the window is 6 ns.
            #
            # The lock detect circuit goes high when n consecutive PFD cycles are less
            # than the comparison window value; n is set by the LDF bit (DB8). For example, with DB8 = 0
            # and DB7 = 0, 40 consecutive PFD cycles of 10 ns or less must occur before digital lock
            # detect goes high. For fractional-N applications, the recommended setting for Bits[DB8:DB7]
            # is 00; for integer-N applications, the recommended setting for Bits[DB8:DB7] is 11.

            self._adf._write_element_by_name('LDP', int(bool(value)))


        @property
        def lock_detect_precision_enabled(self):
            return self._adf.map.value_of_element('LDP') == 1


        def _set_polarity(self, non_inverting = True):
            # The DB6 bit sets the phase detector polarity.
            # When a passive loop filter or a noninverting active loop filter is used, this bit should be set to 1.
            # If an active filter with an inverting characteristic is used, this bit should be set to 0.

            self._adf._write_element_by_name('Phase_Detector_Polarity', int(bool(non_inverting)))


        @property
        def with_inverted_polarity(self):
            return self._adf.map.value_of_element('Phase_Detector_Polarity') == 0


        @property
        def cycle_slip_reduction_enabled(self):
            return self._adf.map.value_of_element('CSR_Enable') == 1


        def _enable_cycle_slip_reduction(self, value = True):
            # Setting the DB18 bit to 1 enables cycle slip reduction. CSR is a method for
            # improving lock times. Note that the signal at the phase frequency detector
            # (PFD) must have a 50% duty cycle for cycle slip reduction to work. The charge
            # pump current setting must also be set to a minimum. For more information, see
            # the Cycle Slip Reduction for Faster Lock Times section.
            #
            # The reference divide-by-2 divides the reference signal by 2, resulting in a
            # 50% duty cycle PFD frequency. This is necessary for the correct operation of
            # the cycle slip reduction (CSR) function. For more information, see the Cycle
            # Slip Reduction for Faster Lock Times section.

            if value:
                assert self._adf.ref_divider.enabled, 'The reference divide-by-2 should be enabled, '
                assert self._adf.charge_pump.current == min(self._adf.charge_pump.CHARGE_PUMP_CURRENTS.keys())

            self._adf._write_element_by_name('CSR_Enable', int(bool(value)))


        def _set_lock_detect_pin_operation(self, value = 'DIGITAL_LOCK_DETECT'):
            # Bits[DB23:DB22] set the operation of the lock detect (LD) pin (see Figure 29).

            self._adf._write_element_by_name('Lock_Detect_Pin_Operation', self.LOCK_DETECT_PIN_OPERATIONS[value])


    class _VCO(_DividerBase):

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
        # value of the band select clock divider. The VCO VTUNE is disconnected from the output of the loop filter
        # and is connected to an internal reference voltage.

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
        # ADF4351 contains linearization circuitry to minimize any variation of the product of ICP and KV to
        # keep the loop bandwidth constant.
        #
        # The VCO shows variation of KV as the VTUNE varies within the
        # band and from band to band. For wideband applications covering a wide frequency range
        # (and changing output dividers), a value of 40 MHz/V provides the most accurate KV because this
        # value is closest to an average value. Figure 21 shows how KV
        # varies with fundamental VCO frequency, along with an average
        # value for the frequency band. Users may prefer this figure when
        # using narrow-band designs.

        DENOMINATOR_BITS = 16
        DENOMINATOR_MAX = 2 ** DENOMINATOR_BITS - 1

        DIVIDER_MIN = 1
        DIVIDER_MAX = DENOMINATOR_MAX
        DIVIDER_DEFAULT = None

        FREQ_MIN = 2.2e9
        FREQ_MAX = 4.4e9
        FREQ_DEFAULT = 3.0e9


        def __init__(self, adf, source):
            self._adf = adf
            self._denominator = self.DENOMINATOR_MAX
            self._set_divider(self.FREQ_DEFAULT / source.freq)
            self._set_input_source(source)


        def set_frequency(self, freq):
            d = freq / self._adf.freq_pfd
            self._adf.rf_n_divider._set_divider_equivalent(d)
            _ = self._adf.rf_n_divider.freq  # validate
            return True


        @property
        def freq(self):
            freq = _freq_trim(self.source.freq * self.divider)

            # Note that the ADF4351 VCO operates in the frequency range of 2.2 GHz to 4.4 GHz.
            assert self.FREQ_MIN <= freq <= self.FREQ_MAX, \
                'VCO operates at {:0.1e} ~ {:0.1e} Hz, now is {:0.1e} Hz'.format(self.FREQ_MIN, self.FREQ_MAX, freq)

            return freq


        @property
        def is_in_integer_mode(self):
            return self.source.feedback_source.is_in_integer_mode


        def _power_down(self, value = True):
            # Setting the DB11 bit to 0 powers the VCO up; setting this bit to 1 powers the VCO down.

            self._adf._write_element_by_name('VCO_Power-Down', int(bool(value)))


        @property
        def power_downed(self):
            return self._adf.map.value_of_element('VCO_Power-Down') == 1


        def _set_divider(self, divider):
            self._divider = divider


    class _RF_Divider(_IntegerDivider):
        # After band selection, normal PLL action resumes. The nominal value of KV is 40
        # MHz/V when the N divider is driven from the VCO output or from this value divided
        # by D. D is the output divider value if the N divider is driven from the RF divider
        # output (selected by programming Bits[DB22:DB20] in Register 4). The ADF4351
        # contains linearization circuitry to minimize any variation of the product of ICP
        # and KV to keep the loop bandwidth constant.

        DIVIDERS = [2 ** i for i in range(7)]
        DIVIDER_CODES = {2 ** i: i for i in range(7)}
        DIVIDER_DEFAULT = 2  # problematic if default as 64, and switch N-divider's source from VCO to RF_divider.


        def __init__(self, adf, source, double_buffered = False):
            super().__init__(adf, source)
            self._enable_double_buffered(double_buffered)


        def _enable_double_buffered(self, value = True):
            # The divider select value in Register 4 (R4) is also double buffered, but only
            # if the DB13 bit of Register 2 (R2) is set to 1.
            # The DB13 bit enables or disables double buffering of Bits[DB22:DB20] in Register 4. For
            # information about how double buffering works, see the Program Modes section.

            self._adf._write_element_by_name('Double_Buffer', int(bool(value)))


        def _set_parameters(self, divider):
            # Bits[DB22:DB20] select the value of the RF output divider (see Figure 28).

            self._adf._write_element_by_name('RF_Divider_Select', self.DIVIDER_CODES[divider])
            self._adf._confirm_double_buffer()


    class _RF_Output(_IntegerDivider):
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

        CHANNEL_RESOLUTION_DEFAULT = 100e3
        POWER_DBM_LEVELS = {-4: 0, -1: 1, 2: 2, 5: 3}
        POWER_DBM_LEVELS_value_key = _value_key(POWER_DBM_LEVELS)


        def __init__(self, adf, source,
                     channel_resolution = CHANNEL_RESOLUTION_DEFAULT,
                     output_power_dBm = -4, MTLD = False, enable = True):
            super().__init__(adf, source)
            self.channel_resolution = channel_resolution
            self.set_output_power(dBm = output_power_dBm)
            self._mute_till_lock_detected(MTLD)
            self.enable(enable)


        def _mute_till_lock_detected(self, value = True):
            # When the DB10 bit is set to 1, the supply current to the RF output stage is shut down
            # until the part achieves lock, as measured by the digital lock detect circuitry.

            self._adf._write_element_by_name('MTLD', int(bool(value)))


        def enable(self, value = True):
            # The DB5 bit enables or disables the primary RF output. If DB5 is set to 0, the primary RF
            # output is disabled; if DB5 is set to 1, the primary RF output is enabled.

            self._adf._write_element_by_name('RF_Output_Enable', int(bool(value)))


        @property
        def dBm(self):
            return self.POWER_DBM_LEVELS_value_key[self._adf.map.value_of_element('Output_Power')]


        def set_output_power(self, dBm = -4):
            # Bits[DB4:DB3] set the value of the primary RF output power level (see Figure 28).
            valids = self.POWER_DBM_LEVELS.keys()
            assert dBm in valids, 'valid dBm: {}'.format(valids)

            self._adf._write_element_by_name('Output_Power', self.POWER_DBM_LEVELS[dBm])


        @property
        def rf_divider(self):
            return self.source


        def set_frequency(self, freq, channel_resolution = None, rf_divider_as = None):
            if channel_resolution is not None:
                self.channel_resolution = channel_resolution

            self._adf._register_write_enabled = False

            for d in sorted(self.rf_divider.DIVIDERS, reverse = True) if rf_divider_as is None else (rf_divider_as,):
                try:
                    freq_vco = freq * d
                    self.rf_divider._set_divider(d)
                    self._adf.rf_n_divider._set_channel_resolution(self.channel_resolution)
                    self._adf.vco.set_frequency(freq_vco)
                    _ = self.freq  # validate

                    self._adf.write_all_registers()
                    return True

                except AssertionError as e:
                    if self._adf.DEBUG_MODE:
                        print(e)
                        err_msg = 'Failed in setting RF_out as {} Hz = {} Hz / {} (freq_vco / rf_divider).'
                        print(err_msg.format(freq, freq_vco, d))

            self._adf._register_write_enabled = True
            raise ValueError('Failed in setting frequency as {}.'.format(freq))


    class _AuxOutput(_IntegerDivider):

        SOURCES = {'DIVIDED': 0, 'FUNDAMENTAL': 1}
        POWER_DBM_LEVELS = {-4: 0, -1: 1, 2: 2, 5: 3}
        POWER_DBM_LEVELS_value_key = _value_key(POWER_DBM_LEVELS)


        def __init__(self, adf, source = 'FUNDAMENTAL', output_power_dBm = -4, enable = False):
            super().__init__(adf, source)
            self.set_output_power(dBm = output_power_dBm)
            self.enable(enable)


        def _set_input_source(self, source = 'FUNDAMENTAL'):
            # The DB9 bit sets the auxiliary RF output. If DB9 is set to 0, the auxiliary RF output is
            # the output of the RF dividers; if DB9 is set to 1, the auxiliary RF output is the
            # fundamental VCO frequency.

            valids = self.SOURCES.keys()
            assert source in valids, 'valid source: {}'.format(valids)

            self._adf._write_element_by_name('AUX_Output_Select', self.SOURCES[source])
            self._source = self._adf.vco if source == 'FUNDAMENTAL' else self._adf.rf_divider
            _ = self.freq  # validate freq


        def enable(self, value = True):
            # The DB8 bit enables or disables the auxiliary RF output. If DB8 is set to 0, the auxiliary
            # RF output is disabled; if DB8 is set to 1, the auxiliary RF output is enabled.

            self._adf._write_element_by_name('AUX_Output_Enable', int(bool(value)))


        @property
        def dBm(self):
            return self.POWER_DBM_LEVELS_value_key[self._adf.map.value_of_element('AUX_Output_Power')]


        def set_output_power(self, dBm = -4):
            # Bits[DB7:DB6] set the value of the auxiliary RF output power level (see Figure 28).

            self._adf._write_element_by_name('AUX_Output_Power', self.POWER_DBM_LEVELS[dBm])


    class _Prescaler(_DividerBase):

        DENOMINATOR_BITS = 1
        DENOMINATOR_MAX = 2 ** DENOMINATOR_BITS - 1

        DIVIDER_MIN = 4 / 5
        DIVIDER_MAX = 8 / 9
        DIVIDER_DEFAULT = DIVIDER_MAX

        PRESCALERS = {'4/5': 0, '8/9': 1}
        PRESCALERS_value_key = _value_key(PRESCALERS)
        FREQ_MAX_AT_PRESCALE_4_5 = 3.6e9


        @property
        def status(self):
            return OrderedDict({'type'       : self.__class__.__name__,
                                'source_type': self.source.__class__.__name__,
                                'source_freq': self.source.freq,
                                'prescaler'  : self.prescaler,
                                'my_divider' : self.divider,
                                'is_integer' : self.is_in_integer_mode,
                                'my_freq'    : self.freq})


        @property
        def freq(self):
            # When the prescaler is set to 4/5, the maximum RF frequency allowed is 3.6 GHz.
            # Therefore, when operating the ADF4351 above 3.6 GHz, the prescaler must be set to 8/9.

            if self.prescaler == '4/5' and hasattr(self._adf, 'rf_out'):
                assert self._adf.vco.freq <= self.FREQ_MAX_AT_PRESCALE_4_5, \
                    'When operating the ADF4351 above 3.6 GHz, the prescaler must be set to 8/9.'

            return _freq_trim(self.source.freq * self.divider)


        def _set_divider(self, divider):
            result = self._set_prescaler('4/5' if divider == 4 / 5 else '8/9')
            self._divider = 4 / 5 if divider == 4 / 5 else 8 / 9
            self._post_set_divider()
            return result


        @property
        def is_in_integer_mode(self):
            return False


        @property
        def prescaler(self):
            return self.PRESCALERS_value_key[self._adf.map.value_of_element('Prescaler_Value')]


        def _set_prescaler(self, prescaler):
            # The dual-modulus prescaler (P/P + 1), along with the INT, FRAC, and MOD values, determines
            # the overall division ratio from the VCO output to the PFD input. The PR1 bit (DB27) in
            # Register 1 sets the prescaler value. Operating at CML levels, the prescaler takes the
            # clock from the VCO output and divides it down for the counters. The prescaler is based on
            # a synchronous 4/5 core.
            #
            # When the prescaler is set to 4/5, the maximum RF frequency allowed is 3.6 GHz.
            # Therefore, when operating the ADF4351 above 3.6 GHz, the prescaler must be set to 8/9.
            #
            # The prescaler limits the INT value as follows:
            # · Prescaler = 4/5: NMIN = 23
            # · Prescaler = 8/9: NMIN = 75

            valids = self.PRESCALERS.keys()
            assert prescaler in valids, 'valid prescaler: {}'.format(valids)

            self._adf._write_element_by_name('Prescaler_Value', self.PRESCALERS[prescaler])
            self._adf._RF_N_Divider.DIVIDER_MIN = self._adf._RF_N_Divider.INT_MIN[prescaler]


    class _RF_N_Divider(_DividerBase):

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
        DIVIDER_DEFAULT = 120

        DENOMINATOR_BITS = MOD_BITS
        DENOMINATOR_MAX = MOD_MAX
        FREQ_MAX_FRACTIONAL_MODE = 32e6
        FREQ_MAX_INTEGER_MODE = 90e6

        SOURCES = {'DIVIDED': 0, 'FUNDAMENTAL': 1}
        SOURCES_value_key = _value_key(SOURCES)


        def __init__(self, adf, source = 'FUNDAMENTAL'):
            super().__init__(adf, source)


        @property
        def status(self):
            return OrderedDict({'type'              : self.__class__.__name__,
                                'source_type'       : self.source.__class__.__name__,
                                'source_freq'       : self.source.freq,
                                'my_divider'        : self.divider,
                                'divider_equivalent': self.divider_equivalent,
                                'is_integer'        : self.is_in_integer_mode,
                                'my_freq'           : self.freq})


        @property
        def fundamental_as_feedback(self):
            return self._adf.map.value_of_element('Feedback_Select') == 1


        def _set_input_source(self, source = 'FUNDAMENTAL'):
            # The DB23 bit selects the feedback from the VCO output to the N counter.
            # When this bit is set to 1, the signal is taken directly from the VCO.
            # When this bit is set to 0, the signal is taken from the output of the output dividers.
            # The dividers enable coverage of the wide frequency band (34.375 MHz to 4.4 GHz).
            # When the dividers are enabled and the feedback signal is taken from the output,
            # the RF output signals of two separately configured PLLs are in phase.
            # This is useful in some applications where the positive interference of
            # signals is required to increase the power.

            valids = self.SOURCES.keys()
            assert source in valids, 'valid source: {}'.format(valids)

            self._adf._write_element_by_name('Feedback_Select', int(source == 'FUNDAMENTAL'))

            self._source = self._adf.vco if source == 'FUNDAMENTAL' else self._adf.rf_divider

            self._synch_freq_pfd()  # set divider so my freq == freq_pfd.
            _ = self.freq  # validate freq


        @property
        def freq(self):
            # Note that in fractional-N mode, the PFD cannot operate above 32 MHz  due to a
            # limitation in the speed of the Σ-Δ circuit of the N divider.
            # For integer-N applications, the PFD can operate up to 90 MHz.

            freq = _freq_trim(self.source.freq / self.divider)

            freq_limit = self.FREQ_MAX_INTEGER_MODE if self.is_in_integer_mode else self.FREQ_MAX_FRACTIONAL_MODE
            assert freq <= freq_limit, 'freq should be less than {}'.format(freq_limit)

            self._adf.phase_frequency_detector._valid_freq_pfd(freq)  # ouput freq of N-divider is also freq_pfd.

            return freq


        @property
        def freq_resolution(self):
            return self._adf.freq_pfd / self.MOD


        def _synch_freq_pfd(self):
            self.set_frequency(self._adf.freq_pfd)


        @property
        def INT(self):
            return self._adf.map.value_of_element('INT')


        @property
        def FRAC(self):
            return self._adf.map.value_of_element('FRAC')


        @property
        def MOD(self):
            return self._adf.map.value_of_element('MOD')


        def step(self, steps):
            d, m = divmod(self.FRAC + steps, self.MOD)
            self._adf._write_element_by_name('INT', self.INT + d)
            self._adf._write_element_by_name('FRAC', m)


        def _set_channel_resolution(self, resolution = None):
            if resolution is None:
                self._denominator = self.DENOMINATOR_MAX
            else:
                self._denominator = math.ceil(self._adf.freq_pfd / resolution)

            self._adf._write_element_by_name('MOD', self._denominator)
            self._adf._confirm_double_buffer()


        @property
        def is_in_integer_mode(self):
            return self._adf.map.value_of_element('LDF') == 1


        @property
        def divider(self):
            return self.INT + self.FRAC / self.MOD


        def _set_divider(self, divider):
            super()._set_divider(divider)
            self._adf.vco._set_divider(self.divider_equivalent)  # re-assign VCO's divider.
            self._adf.band_select_clock_divider._refresh_divider()
            return True


        def _set_parameters(self, a, b, c):
            # RF N DIVIDER The RF N divider allows a division ratio in the PLL feedback
            # path. The division ratio is determined by the INT, FRAC, and MOD values, which
            # build up this divider (see Figure 17)
            #
            # INT, FRAC, MOD, and R Counter Relationship
            # The INT, FRAC, and MOD values, in conjunction with the R
            # counter, make it possible to generate output frequencies that are spaced by
            # fractions of the PFD frequency. For more information, see the RF Synthesizer—A
            # Worked Example section.
            #
            # The RF VCO frequency (RFOUT) equation is
            #  RFOUT = fPFD × (INT + (FRAC/MOD)) (1)
            # where:
            #  RFOUT is the output frequency of the voltage controlled oscillator (VCO).
            #  INT is the preset divide ratio of the binary 16-bit counter
            #   (23 to 65,535 for the 4/5 prescaler;
            #    75 to 65,535 for the 8/9 prescaler).
            #  FRAC is the numerator of the fractional division (0 to MOD − 1).
            #  MOD is the preset fractional modulus (2 to 4095).
            # self._adf._RF_N_Divider.INT_MIN[prescaler]

            assert self.INT_MIN[self._adf.prescaler.prescaler] <= a <= self.INT_MAX  # INT = a  # 4/5: 23 to 65535
            assert self.FRAC_MIN <= b <= self.FRAC_MAX  # FRAC = b  # 0 to MOD-1
            assert self.MOD_MIN <= c <= self.MOD_MAX  # MOD = c  # 2 to 4095

            # The 12 MOD bits (Bits[DB14:DB3]) set the fractional modulus. The fractional modulus is the
            # ratio of the PFD frequency to the channel step resolution on the RF output. For more
            # information, see the 12-Bit Programmable Modulus section.
            self._adf._write_element_by_name('MOD', c)

            # The 16 INT bits (Bits[DB30:DB15]) set the INT value, which determines the integer part of
            # the feedback division factor. The INT value is used in Equation 1 (see the INT, FRAC, MOD,
            # and R Counter Relationship section). Integer values from 23 to 65,535 are allowed for the
            # 4/5 prescaler; for the 8/9 prescaler, the minimum integer value is 75.
            self._adf._write_element_by_name('INT', a)

            # The 12 FRAC bits (Bits[DB14:DB3]) set the numerator of the fraction that is input to the
            # Σ-Δ modulator. This fraction, along with the INT value, specifies the new frequency
            # channel that the synthesizer locks to, as shown in the RF Synthesizer—A Worked Example
            # section. FRAC values from 0 to (MOD ? 1) cover channels over a frequency range equal to
            # the PFD reference frequency.
            self._adf._write_element_by_name('FRAC', b)

            # self._adf._confirm_double_buffer()  # write FRAC last so register_0 doesn't need to be written again.


        def _set_integer_mode(self, value = True):
            # Integer-N Mode
            # If FRAC = 0 and the DB8 (LDF) bit in Register 2 is set to 1, the
            # synthesizer operates in integer-N mode. The DB8 bit in Register 2
            # should be set to 1 for integer-N digital lock detect.

            # The DB8 bit configures the lock detect function (LDF). The LDF controls the number of PFD
            # cycles monitored by the lock detect circuit to ascertain whether lock has been achieved.
            # When DB8 is set to 0, the number of PFD cycles monitored is 40.
            # When DB8 is set to 1, the number of PFD cycles monitored is 5.
            # It is recommended that the DB8 bit be set to 0 for fractional-N mode and to 1 for integer-N mode.

            self._adf.phase_frequency_detector._enable_lock_detect_function(value)

            # The lock detect precision bit (Bit DB7) sets the comparison window in the lock detect circuit.
            # When DB7 is set to 0, the comparison window is 10 ns;
            # when DB7 is set to 1, the comparison window is  6 ns.
            #
            # The lock detect circuit goes high when n consecutive PFD cycles are less
            # than the comparison window value; n is set by the LDF bit (DB8).
            # For example, with DB8 = 0 and DB7 = 0, 40 consecutive PFD cycles of 10 ns or less must occur
            # before digital lock detect goes high.
            # For fractional-N applications, the recommended setting for Bits[DB8:DB7]
            # is 00; for integer-N applications, the recommended setting for Bits[DB8:DB7] is 11.

            self._adf.phase_frequency_detector._enable_lock_detect_precision(value)

            # The PFD includes a programmable delay element that sets the
            # width of the ABP (AntiBacklash Pulse). This pulse ensures that
            # there is no dead zone in the PFD transfer function.
            # Bit DB22 in Register 3 (R3) is used to set the PFD ABP (AntiBacklash Pulse) width.
            # . When Bit DB22 is set to 0, the PFD antibacklash pulse width is 6 ns.
            #   This setting is recommended for fractional-N use.
            # . When Bit DB22 is set to 1, the PFD antibacklash pulse width is 3 ns,
            #   which results in phase noise and spur improvements in integer-N operation.
            # For fractional-N operation, the 3 ns setting is not recommended.

            # For integer-N applications, the in-band phase noise is improved
            # by enabling the shorter pulse width. The PFD frequency can
            # operate up to 90 MHz in this mode. To operate with PFD
            # frequencies higher than 45 MHz, VCO band select must be disabled by
            # setting the phase adjust bit (DB28) to 1 in Register 1.

            self._adf.phase_frequency_detector._set_antibacklash_pulse_width(as_3_ns = value)

            # Setting the DB21 bit to 1 enables charge pump charge cancelation. This has the effect of
            # reducing PFD spurs in integer-N mode. In fractional-N mode, this bit should be set to 0.

            self._adf.charge_pump._enable_cancelation(value)


        @property
        def divider_equivalent(self):
            return self.divider * (1 if self.fundamental_as_feedback else self._adf.rf_divider.divider)


        def _set_divider_equivalent(self, divider_eqvilent):
            ratio = divider_eqvilent / self.divider_equivalent
            self._set_divider(self.divider * ratio)


    class _Phaser(_IntegerDivider):
        DIVIDER_BITS = 12
        DIVIDER_DEFAULT = 1


        def __init__(self, adf, source, phase_adjust = False):
            super().__init__(adf, source)
            self._divider_min = 0
            self._enable_phase_adjust(phase_adjust)


        @property
        def status(self):
            return OrderedDict({'type'                : self.__class__.__name__,
                                'source_type'         : self.source.__class__.__name__,
                                'source_freq'         : self.source.freq,
                                'phase_adjust_enabled': self.phase_adjust_enabled,
                                'phase'               : self.phase})


        @property
        def phase_adjust_enabled(self):
            return self._adf.map.value_of_element('Phase_Adjust') == 1


        def _enable_phase_adjust(self, value = True):
            # The phase adjust bit (Bit DB28) enables adjustment of the output phase of a given output frequency.
            # . When phase adjustment is enabled (Bit DB28 is set to 1), the part does not
            # perform VCO band selection or phase resync when Register 0 is updated.
            # . When phase adjustment is disabled (Bit DB28 is set to 0), the part performs VCO band selection and
            # phase resync (if phase resync is enabled in Register 3, Bits[DB16:DB15]) when Register 0
            # is updated.
            # Disabling VCO band selection is recommended only for fixed frequency
            # applications or for frequency deviations of <1 MHz from the originally selected frequency.

            self._adf._write_element_by_name('Phase_Adjust', int(bool(value)))


        @property
        def phase(self):
            phase_word = self._adf.map.value_of_element('Phase_Value')
            return (phase_word % self._adf.rf_n_divider.MOD) / self._adf.rf_n_divider.MOD * DEGREES_IN_PI2


        def set_phase(self, phase):
            # Bits[DB26:DB15] control the phase word. The phase word must be less than the MOD value
            # programmed in Register 1. The phase word is used to program the RF output phase from 0° to
            # 360° with a resolution of 360°/MOD (see the Phase Resync section). In most applications,
            # the phase relationship between the RF signal and the reference is not important. In such
            # applications, the phase value can be used to optimize the fractional and sub-fractional
            # spur levels. For more information, see the Spur Consistency and Fractional Spur
            # Optimization section. If neither the phase resync nor the spurious optimization function
            # is used, it is recommended that the phase word be set to 1.

            phase_word = math.floor((phase % DEGREES_IN_PI2) / DEGREES_IN_PI2 * self._adf.rf_n_divider.MOD)
            self._set_parameters(phase_word)


        def _set_parameters(self, divider):
            self._adf._write_element_by_name('Phase_Value', divider)
            self._adf._confirm_double_buffer()


    class _MuxOut(_IntegerDivider):
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
        SOURCES_value_key = _value_key(SOURCES)


        def __init__(self, adf, source = 'THREE_STATE'):
            super().__init__(adf, source)


        @property
        def status(self):
            return OrderedDict({'type'       : self.__class__.__name__,
                                'source_type': self.source_type,
                                'source_freq': self.source.freq if self.source is not None else None,
                                'my_divider' : self.divider,
                                'is_integer' : self.is_in_integer_mode,
                                'my_freq'    : self.freq if self.source is not None else None})


        @property
        def source_type(self):
            return self.SOURCES_value_key[self._adf.map.value_of_element('MUXOUT')]


        def _set_input_source(self, source = 'THREE_STATE'):
            # The on-chip multiplexer is controlled by Bits[DB28:DB26] (see Figure 26). Note that N
            # counter output must be disabled for VCO band selection to operate correctly.

            valids = self.SOURCES.keys()
            assert source in valids, 'valid source: {}'.format(valids)

            self._source = None

            self._adf._write_element_by_name('MUXOUT', self.SOURCES[source])

            if source == 'R_COUNTER':
                self._source = self._adf.r_counter
                _ = self.freq  # validate freq
            if source == 'N_DIVIDER':
                self._source = self._adf.rf_n_divider
                _ = self.freq  # validate freq


    class _NoiseControl:
        MODES = {'LOW_NOISE_MODE': 0, 'LOW_SPUR_MODE': 3}
        MODES_value_key = _value_key(MODES)


        def __init__(self, adf, mode = 'LOW_NOISE_MODE'):
            self._adf = adf
            self._set_mode(mode)


        @property
        def status(self):
            return OrderedDict({'type': self.__class__.__name__,
                                'mode': self.mode})


        def _set_mode(self, mode = 'LOW_NOISE_MODE'):
            # The noise mode on the ADF4351 is controlled by setting Bits[DB30:DB29] in Register 2 (see
            # Figure 26). The noise mode allows the user to optimize a design either for improved
            # spurious performance or for improved phase noise performance. When the low spur mode is
            # selected, dither is enabled. Dither randomizes the fractional quantization noise so that
            # it resembles white noise rather than spurious noise. As a result, the part is optimized
            # for improved spurious performance. Low spur mode is normally used for fast-locking
            # applications when the PLL closed-loop bandwidth is wide. Wide loop bandwidth is a loop
            # bandwidth greater than 1/10 of the RFOUT channel step resolution (fRES). A wide loop
            # filter does not attenuate the spurs to the same level as a narrow loop bandwidth. For best
            # noise performance, use the low noise mode option. When the low noise mode is selected,
            # dither is disabled. This mode ensures that the charge pump operates in an optimum region
            # for noise performance. Low noise mode is extremely useful when a narrow loop filter
            # bandwidth is available. The synthesizer ensures extremely low noise, and the filter
            # attenuates the spurs. Figure 10 through Figure 12 show the trade-offs in a typical W-CDMA
            # setup for different noise and spur settings.

            valids = self.MODES.keys()
            assert mode in valids, 'valid mode: {}'.format(valids)

            # When the doubler is enabled:
            # . BOTH the rising and falling edges of REFIN become active edges at the PFD input.
            # . If the low spur mode is selected, the in-band phase noise performance is sensitive to
            #   the REFIN duty cycle. The phase noise degradation can be as much as 5 dB
            #   for REFIN duty cycles outside a 45% to 55% range.

            if mode == 'LOW_SPUR_MODE':
                assert not self._adf.ref_doubler.enabled, \
                    'Doubler is enabled. In-band phase noise performance is sensitive to the REFIN duty cycle'

            self._adf._write_element_by_name('Low_Noise_and_Low_Spur_Modes', self.MODES[mode])


        @property
        def mode(self):
            return self.MODES_value_key[self._adf.map.value_of_element('Low_Noise_and_Low_Spur_Modes')]


    class _ChargePump:
        CHARGE_PUMP_CURRENTS = {0.31: 0,
                                0.63: 1,
                                0.94: 2,
                                1.25: 3,
                                1.56: 4,
                                1.88: 5,
                                2.19: 6,
                                2.50: 7,
                                2.81: 8,
                                3.13: 9,
                                3.44: 10,
                                3.75: 11,
                                4.06: 12,
                                4.38: 13,
                                4.69: 14,
                                5.00: 15}

        CHARGE_PUMP_CURRENTS_value_key = _value_key(CHARGE_PUMP_CURRENTS)


        def __init__(self, adf, current_mA = 0.31, three_state = False):
            self._adf = adf
            self._set_current(current_mA)
            self._enable_three_state(three_state)


        @property
        def status(self):
            return OrderedDict({'type'               : self.__class__.__name__,
                                'charge_pump_current': self.current,
                                'three_state_enabled': self.three_state_enabled,
                                'cancelation_enabled': self.cancelation_enabled})


        @property
        def current(self):
            return self.CHARGE_PUMP_CURRENTS_value_key[self._adf.map.value_of_element('Charge_Pump_Current_Setting')]


        def _set_current(self, current_mA = 0.31):
            # Bits[DB12:DB9] set the charge pump current. This value should be set to the charge pump
            # current that the loop filter is designed with (see Figure 26).

            valids = self.CHARGE_PUMP_CURRENTS.keys()
            assert current_mA in valids, 'valid current: {}'.format(valids)

            self._adf._write_element_by_name('Charge_Pump_Current_Setting', self.CHARGE_PUMP_CURRENTS[current_mA])
            self._adf._confirm_double_buffer()


        @property
        def three_state_enabled(self):
            return self._adf.map.value_of_element('Charge_Pump_Three_State') == 1


        def _enable_three_state(self, value = True):
            # Setting the DB4 bit to 1 puts the charge pump into three-state mode. This bit should be
            # set to 0 for normal operation.

            self._adf._write_element_by_name('Charge_Pump_Three_State', int(bool(value)))


        @property
        def cancelation_enabled(self):
            return self._adf.map.value_of_element('Charge_Cancelation') == 1


        def _enable_cancelation(self, value = True):
            # Setting the DB21 bit to 1 enables charge pump charge cancelation. This has the effect of
            # reducing PFD spurs in integer-N mode. In fractional-N mode, this bit should be set to 0.

            self._adf._write_element_by_name('Charge_Cancelation', int(bool(value)))


    def __init__(self, bus,
                 freq = FREQ_DEFAULT, freq_correction = 0, phase = PHASE_DEFAULT, shape = SHAPE_DEFAULT,
                 freq_mclk = FREQ_MCLK,
                 registers_map = None, registers_values = None,
                 commands = None):

        registers_map = _get_registers_map() if registers_map is None else registers_map

        super().__init__(freq = freq, freq_correction = freq_correction, phase = phase, shape = shape,
                         registers_map = registers_map, registers_values = registers_values,
                         commands = commands)

        self._bus = bus
        self._register_write_enabled = False
        self.freq_mclk = freq_mclk

        self.init()


    def reset(self):
        self._action = 'reset'
        self.init()


    def init(self):
        self._action = 'init'

        self._build()
        self.write_all_registers()

        self.start()


    def _build(self):
        self._register_write_enabled = False

        self.noise_control = self._NoiseControl(self)
        self.charge_pump = self._ChargePump(self)
        self.muxout = self._MuxOut(self)

        self.mclk = self._ReferenceInput(self, self.freq_mclk)
        self.ref_doubler = self._ReferenceDoubler(self, self.mclk)
        self.r_counter = self._R_Counter(self, self.ref_doubler)
        self.ref_divider = self._ReferenceDivider(self, self.r_counter)

        self.phase_frequency_detector = self._PhaseFrequencyDetector(self, self.ref_divider)
        self.vco = self._VCO(self, self.phase_frequency_detector)
        self.rf_divider = self._RF_Divider(self, self.vco)
        self.rf_out = self._RF_Output(self, self.rf_divider)
        self.auxout = self._AuxOutput(self)

        self.band_select_clock_divider = self._BandSelectClockDivider(self, self.ref_divider)
        self.clock_divider = self._ClockDivider(self, self.ref_divider)

        self.prescaler = self._Prescaler(self, self.vco)
        self.rf_n_divider = self._RF_N_Divider(self)
        self.phase_frequency_detector._set_feedback_source(self.rf_n_divider)

        self.phaser = self._Phaser(self, self.rf_n_divider)


    @property
    def is_virtual_device(self):
        return self._bus.is_virtual_device


    @property
    def status(self):
        return OrderedDict({name: getattr(self, name).status for name in
                            ('mclk', 'ref_doubler', 'r_counter', 'ref_divider', 'phase_frequency_detector',
                             'rf_n_divider', 'vco', 'rf_divider', 'rf_out', 'auxout')})


    @property
    def freq_pfd(self):
        return self.phase_frequency_detector.freq_pfd


    def apply_signal(self, freq, phase = 0):
        self.set_frequency(freq)
        self.set_phase(phase)


    def set_channel_resolution(self, resolution = None):
        self.rf_n_divider._set_channel_resolution(resolution)


    def set_frequency(self, freq, channel_resolution = None, rf_divider_as = None):
        self._action = 'set_frequency {}'.format(freq)
        self.rf_out.set_frequency(freq,
                                  channel_resolution = channel_resolution,
                                  rf_divider_as = rf_divider_as)


    @property
    def current_dividers(self):
        return {'d_ref_doubler' : self.ref_doubler.divider,
                'd_r_counter'   : self.r_counter.divider,
                'd_ref_divider' : self.ref_divider.divider,
                'd_rf_n_divider': self.rf_n_divider.divider,
                'd_rf_divider'  : self.rf_divider.divider}


    def set_dividers(self, d_ref_doubler = 2, d_r_counter = 1, d_ref_divider = 2,
                     d_rf_n_divider = 176, d_rf_divider = 1):

        self.ref_doubler._set_divider(d_ref_doubler)
        self.r_counter._set_divider(d_r_counter)
        self.ref_divider._set_divider(d_ref_divider)
        self.rf_divider._set_divider(d_rf_divider)
        self.rf_n_divider._set_divider(d_rf_n_divider)


    @property
    def current_frequency(self):
        return self.rf_out.freq


    @property
    def freq_resolution(self):
        return self.rf_n_divider.freq_resolution


    def set_phase(self, phase):
        self._action = 'set_phase {}'.format(phase)
        self.phaser.set_phase(phase)


    @property
    def current_phase(self):
        return self.phaser.phase


    @property
    def phase_resolution(self):
        return DEGREES_IN_PI2 / self.rf_n_divider.MOD


    def enable_output(self, value = True):
        self._action = 'enable_output: {}'.format(value)
        self._power_down(not value)
        self._enable_counters(value)


    @property
    def power_downed(self):
        return self.map.value_of_element('Power_Down') == 1


    # =================================================================

    @property
    def current_configuration(self):
        import pandas as pd

        dfs = [pd.DataFrame([getattr(self, n).status]) for n in
               ('mclk', 'ref_doubler', 'r_counter', 'ref_divider', 'phase_frequency_detector',
                'rf_n_divider', 'vco', 'rf_divider', 'rf_out', 'auxout')]
        df_dividers = pd.concat(dfs).reindex(columns = ['type', 'source_type', 'source_freq', 'my_divider',
                                                        'divider_equivalent', 'is_integer', 'my_freq'])
        df_dividers.index = range(len(df_dividers))

        dfs = [pd.DataFrame([getattr(self, n).status]) for n in (
            'phaser', 'prescaler', 'muxout', 'band_select_clock_divider', 'clock_divider', 'noise_control',
            'charge_pump')]
        df_controls = pd.concat(dfs)
        df_controls.index = range(len(df_controls))

        return df_dividers, df_controls


    def find_integer_N_dividers(self, freq_desired, freq_ref = FREQ_MCLK,
                                ref_doubled_by_2 = True, ref_divided_by_2 = True,
                                rf_divider_as = None,
                                torance_hz = 1):

        self._register_write_enabled = False

        results = []

        self.mclk.set_frequency(freq_ref)

        for d_ref_doubler in (2,) if ref_doubled_by_2 else self._ReferenceDoubler.DIVIDERS:
            for d_ref_divider in (2,) if ref_divided_by_2 else self._ReferenceDivider.DIVIDERS:
                for d_r_counter in range(1, self.r_counter._divider_max + 1):
                    for d_rf_divider in self.rf_divider.DIVIDERS if rf_divider_as is None else (rf_divider_as,):

                        try:
                            self.ref_doubler._set_divider(d_ref_doubler)
                            self.r_counter._set_divider(d_r_counter)
                            self.ref_divider._set_divider(d_ref_divider)
                            self.rf_divider._set_divider(d_rf_divider)

                            self.vco.set_frequency(freq_desired * d_rf_divider)
                            freq_rf_out = self.rf_out.freq  # validate

                            diff = abs(freq_rf_out - freq_desired)
                            d_rf_n_divider = self.rf_n_divider.divider

                            if diff < torance_hz and _is_integer(d_rf_n_divider):

                                match = ((d_ref_doubler, d_r_counter, d_ref_divider, d_rf_n_divider, d_rf_divider),
                                         (self.mclk.freq, self.ref_doubler.freq, self.r_counter.freq,
                                          self.ref_divider.freq,
                                          self.vco.freq, self.rf_divider.freq, self.rf_out.freq))

                                results.append(match)
                        except:
                            pass

            self.init()

        return sorted(results)


    # =================================================================
    def _power_down(self, value = True):
        # The DB5 bit provides the programmable power-down mode.
        # Setting this bit to 1 performs a power-down.
        # Setting this bit to 0 returns the synthesizer to normal operation.
        # In software power-down mode, the part retains all information in its registers. The register contents
        # are lost only if the supply voltages are removed.
        #
        # When power-down is activated, the following events occur:
        # · Synthesizer counters are forced to their load state conditions.
        # · VCO is powered down.
        # · Charge pump is forced into three-state mode.
        # · Digital lock detect circuitry is reset.
        # · RFOUT buffers are disabled.
        # · Input registers remain active and capable of loading and latching data.

        self._write_element_by_name('Power_Down', int(bool(value)))

        if not value:
            self.vco._power_down(value)
            self.charge_pump._enable_three_state(value)
            self.rf_out.enable(not value)


    def _enable_counters(self, value = True):
        # The DB3 bit is the reset bit for the R counter and the N counter of the ADF4351. When this
        # bit is set to 1, the RF synthesizer N counter and R counter are held in reset. For normal
        # operation, this bit should be set to 0.

        self._write_element_by_name('Counter_Reset', int(not bool(value)))

        if value:  # restore divider values
            self.r_counter._set_divider(self.r_counter.divider)
            self.rf_n_divider._set_divider(self.rf_n_divider.divider)


    # =================================================================

    def _write_register(self, register, reset = False):
        if self._register_write_enabled:
            super()._write_register(register, reset = reset)
            self._bus.write(register.bytes)


    def _write_register_0(self):
        self._write_register(self.map._registers[0])


    def _confirm_double_buffer(self):
        self._write_register_0()


    def write_all_registers(self, reset = False):
        self._register_write_enabled = True
        for reg in self.map._registers[::-1]:
            self._write_register(reg, reset = reset)
