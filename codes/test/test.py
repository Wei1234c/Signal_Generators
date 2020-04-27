def _set_int(self, value = True):
    # The 16 INT bits (Bits[DB30:DB15]) set the INT value, which determines the integer part of
    # the feedback division factor. The INT value is used in Equation 1 (see the INT, FRAC, MOD,
    # and R Counter Relationship section). Integer values from 23 to 65,535 are allowed for the
    # 4/5 prescaler; for the 8/9 prescaler, the minimum integer value is 75.

    self._adf._write_element_by_name('INT', int(bool(value)))



@property
def int(self):
    return self._adf.map.elements['INT']['element'].value



def _set_frac(self, value = True):
    # The 12 FRAC bits (Bits[DB14:DB3]) set the numerator of the fraction that is input to the
    # Σ-Δ modulator. This fraction, along with the INT value, specifies the new frequency
    # channel that the synthesizer locks to, as shown in the RF Synthesizer—A Worked Example
    # section. FRAC values from 0 to (MOD ? 1) cover channels over a frequency range equal to
    # the PFD refer- ence frequency.

    self._adf._write_element_by_name('FRAC', int(bool(value)))



@property
def frac(self):
    return self._adf.map.elements['FRAC']['element'].value



def _set_phase_adjust(self, value = True):
    # The phase adjust bit (Bit DB28) enables adjustment of the output phase of a given output
    # frequency. When phase adjustment is enabled (Bit DB28 is set to 1), the part does not
    # perform VCO band selection or phase resync when Register 0 is updated. When phase
    # adjustment is disabled (Bit DB28 is set to 0), the part performs VCO band selection and
    # phase resync (if phase resync is enabled in Register 3, Bits[DB16:DB15]) when Register 0
    # is updated. Disabling VCO band selection is recommended only for fixed frequency
    # applications or for frequency deviations of <1 MHz from the originally selected frequency.

    self._adf._write_element_by_name('Phase_Adjust', int(bool(value)))



@property
def phase_adjust(self):
    return self._adf.map.elements['Phase_Adjust']['element'].value



def _set_prescaler_value(self, value = True):
    # The dual-modulus prescaler (P/P + 1), along with the INT, FRAC, and MOD values, determines
    # the overall division ratio from the VCO output to the PFD input. The PR1 bit (DB27) in
    # Register 1 sets the prescaler value. Operating at CML levels, the prescaler takes the
    # clock from the VCO output and divides it down for the counters. The prescaler is based on
    # a synchronous 4/5 core. When the prescaler is set to 4/5, the maximum RF frequency allowed
    # is 3.6 GHz. Therefore, when operating the ADF4351 above 3.6 GHz, the prescaler must be set
    # to 8/9. The prescaler limits the INT value as follows: · Prescaler = 4/5: NMIN = 23 ·
    # Prescaler = 8/9: NMIN = 75

    self._adf._write_element_by_name('Prescaler_Value', int(bool(value)))



@property
def prescaler_value(self):
    return self._adf.map.elements['Prescaler_Value']['element'].value



def _set_phase_value(self, value = True):
    # Bits[DB26:DB15] control the phase word. The phase word must be less than the MOD value
    # programmed in Register 1. The phase word is used to program the RF output phase from 0° to
    # 360° with a resolution of 360°/MOD (see the Phase Resync section). In most applications,
    # the phase relationship between the RF signal and the reference is not important. In such
    # applications, the phase value can be used to optimize the fractional and sub- fractional
    # spur levels. For more information, see the Spur Consistency and Fractional Spur
    # Optimization section. If neither the phase resync nor the spurious optimization func- tion
    # is used, it is recommended that the phase word be set to 1.

    self._adf._write_element_by_name('Phase_Value', int(bool(value)))



@property
def phase_value(self):
    return self._adf.map.elements['Phase_Value']['element'].value



def _set_mod(self, value = True):
    # The 12 MOD bits (Bits[DB14:DB3]) set the fractional modulus. The fractional modulus is the
    # ratio of the PFD frequency to the channel step resolution on the RF output. For more
    # information, see the 12-Bit Programmable Modulus section.

    self._adf._write_element_by_name('MOD', int(bool(value)))



@property
def mod(self):
    return self._adf.map.elements['MOD']['element'].value



def _set_low_noise_and_low_spur_modes(self, value = True):
    # The noise mode on the ADF4351 is controlled by setting Bits[DB30:DB29] in Register 2 (see
    # Figure 26). The noise mode allows the user to optimize a design either for improved
    # spurious performance or for improved phase noise performance. When the low spur mode is
    # selected, dither is enabled. Dither randomizes the fractional quantization noise so that
    # it resembles white noise rather than spurious noise. As a result, the part is optimized
    # for improved spurious performance. Low spur mode is normally used for fast-locking
    # applications when the PLL closed-loop bandwidth is wide. Wide loop bandwidth is a loop
    # bandwidth greater than 1/10 of the RFOUT channel step resolu- tion (fRES). A wide loop
    # filter does not attenuate the spurs to the same level as a narrow loop bandwidth. For best
    # noise performance, use the low noise mode option. When the low noise mode is selected,
    # dither is disabled. This mode ensures that the charge pump operates in an optimum region
    # for noise performance. Low noise mode is extremely useful when a narrow loop filter
    # bandwidth is available. The synthesizer ensures extremely low noise, and the filter
    # attenuates the spurs. Figure 10 through Figure 12 show the trade-offs in a typical W-CDMA
    # setup for different noise and spur settings.

    self._adf._write_element_by_name('Low_Noise_and_Low_Spur_Modes', int(bool(value)))



@property
def low_noise_and_low_spur_modes(self):
    return self._adf.map.elements['Low_Noise_and_Low_Spur_Modes']['element'].value



def _set_muxout(self, value = True):
    # The on-chip multiplexer is controlled by Bits[DB28:DB26] (see Figure 26). Note that N
    # counter output must be disabled for VCO band selection to operate correctly.

    self._adf._write_element_by_name('MUXOUT', int(bool(value)))



@property
def muxout(self):
    return self._adf.map.elements['MUXOUT']['element'].value



def _set_reference_doubler(self, value = True):
    # Setting the DB25 bit to 0 disables the doubler and feeds the REFIN signal directly into
    # the 10-bit R counter. Setting this bit to 1 multi- plies the REFIN frequency by a factor
    # of 2 before feeding it into the 10-bit R counter. When the doubler is disabled, the REFIN
    # falling edge is the active edge at the PFD input to the fractional synthesizer. When the
    # doubler is enabled, both the rising and falling edges of REFIN become active edges at the
    # PFD input. When the doubler is enabled and the low spur mode is selected, the in-band
    # phase noise performance is sensitive to the REFIN duty cycle. The phase noise degradation
    # can be as much as 5 dB for REFIN duty cycles outside a 45% to 55% range. The phase noise
    # is insensitive to the REFIN duty cycle in the low noise mode and when the doubler is
    # disabled. The maximum allowable REFIN frequency when the doubler is enabled is 30 MHz.

    self._adf._write_element_by_name('Reference_Doubler', int(bool(value)))



@property
def reference_doubler(self):
    return self._adf.map.elements['Reference_Doubler']['element'].value



def _set_rdiv2(self, value = True):
    # Setting the DB24 bit to 1 inserts a divide-by-2 toggle flip-flop between the R counter and
    # the PFD, which extends the maximum REFIN input rate. This function allows a 50% duty cycle
    # signal to appear at the PFD input, which is necessary for cycle slip reduction.

    self._adf._write_element_by_name('RDIV2', int(bool(value)))



@property
def rdiv2(self):
    return self._adf.map.elements['RDIV2']['element'].value



def _set_r_counter(self, value = True):
    # The 10-bit R counter (Bits[DB23:DB14]) allows the input reference frequency (REFIN) to be
    # divided down to produce the reference clock to the PFD. Division ratios from 1 to 1023 are
    # allowed.

    self._adf._write_element_by_name('R_Counter', int(bool(value)))



@property
def r_counter(self):
    return self._adf.map.elements['R_Counter']['element'].value



def _set_double_buffer(self, value = True):
    # The DB13 bit enables or disables double buffering of Bits[DB22:DB20] in Register 4. For
    # information about how double buffering works, see the Program Modes section.

    self._adf._write_element_by_name('Double_Buffer', int(bool(value)))



@property
def double_buffer(self):
    return self._adf.map.elements['Double_Buffer']['element'].value



def _set_charge_pump_current_setting(self, value = True):
    # Bits[DB12:DB9] set the charge pump current. This value should be set to the charge pump
    # current that the loop filter is designed with (see Figure 26).

    self._adf._write_element_by_name('Charge_Pump_Current_Setting', int(bool(value)))



@property
def charge_pump_current_setting(self):
    return self._adf.map.elements['Charge_Pump_Current_Setting']['element'].value



def _set_ldf(self, value = True):
    # The DB8 bit configures the lock detect function (LDF). The LDF controls the number of PFD
    # cycles monitored by the lock detect circuit to ascertain whether lock has been achieved.
    # When DB8 is set to 0, the number of PFD cycles monitored is 40. When DB8 is set to 1, the
    # number of PFD cycles monitored is 5. It is recom- mended that the DB8 bit be set to 0 for
    # fractional-N mode and to 1 for integer-N mode.

    self._adf._write_element_by_name('LDF', int(bool(value)))



@property
def ldf(self):
    return self._adf.map.elements['LDF']['element'].value



def _set_ldp(self, value = True):
    # The lock detect precision bit (Bit DB7) sets the comparison window in the lock detect
    # circuit. When DB7 is set to 0, the comparison window is 10 ns; when DB7 is set to 1, the
    # window is 6 ns. The lock detect circuit goes high when n consecutive PFD cycles are less
    # than the comparison window value; n is set by the LDF bit (DB8). For example, with DB8 = 0
    # and DB7 = 0, 40 consecutive PFD cycles of 10 ns or less must occur before digital lock
    # detect goes high. For fractional-N applications, the recommended setting for Bits[DB8:DB7]
    # is 00; for integer-N applications, the recom- mended setting for Bits[DB8:DB7] is 11.

    self._adf._write_element_by_name('LDP', int(bool(value)))



@property
def ldp(self):
    return self._adf.map.elements['LDP']['element'].value



def _set_phase_detector_polarity(self, value = True):
    # The DB6 bit sets the phase detector polarity. When a passive loop filter or a noninverting
    # active loop filter is used, this bit should be set to 1. If an active filter with an
    # inverting charac- teristic is used, this bit should be set to 0.

    self._adf._write_element_by_name('Phase_Detector_Polarity', int(bool(value)))



@property
def phase_detector_polarity(self):
    return self._adf.map.elements['Phase_Detector_Polarity']['element'].value



def _set_power_down(self, value = True):
    # The DB5 bit provides the programmable power-down mode. Setting this bit to 1 performs a
    # power-down. Setting this bit to 0 returns the synthesizer to normal operation. In software
    # power- down mode, the part retains all information in its registers. The register contents
    # are lost only if the supply voltages are removed. When power-down is activated, the
    # following events occur: · Synthesizer counters are forced to their load state conditions.
    # · VCO is powered down. · Charge pump is forced into three-state mode. · Digital lock
    # detect circuitry is reset. · RFOUT buffers are disabled. · Input registers remain active
    # and capable of loading and latching data.

    self._adf._write_element_by_name('Power_Down', int(bool(value)))



@property
def power_down(self):
    return self._adf.map.elements['Power_Down']['element'].value



def _set_charge_pump_three_state(self, value = True):
    # Setting the DB4 bit to 1 puts the charge pump into three-state mode. This bit should be
    # set to 0 for normal operation.

    self._adf._write_element_by_name('Charge_Pump_Three_State', int(bool(value)))



@property
def charge_pump_three_state(self):
    return self._adf.map.elements['Charge_Pump_Three_State']['element'].value



def _set_counter_reset(self, value = True):
    # The DB3 bit is the reset bit for the R counter and the N counter of the ADF4351. When this
    # bit is set to 1, the RF synthesizer N counter and R counter are held in reset. For normal
    # opera- tion, this bit should be set to 0.

    self._adf._write_element_by_name('Counter_Reset', int(bool(value)))



@property
def counter_reset(self):
    return self._adf.map.elements['Counter_Reset']['element'].value



def _set_band_select_clock_mode(self, value = True):
    # Setting the DB23 bit to 1 selects a faster logic sequence of band selection, which is
    # suitable for high PFD frequencies and is necessary for fast lock applications. Setting the
    # DB23 bit to 0 is recommended for low PFD (<125 kHz) values. For the faster band select
    # logic modes (DB23 set to 1), the value of the band select clock divider must be less than
    # or equal to 254.

    self._adf._write_element_by_name('Band_Select_Clock_Mode', int(bool(value)))



@property
def band_select_clock_mode(self):
    return self._adf.map.elements['Band_Select_Clock_Mode']['element'].value



def _set_abp(self, value = True):
    # Bit DB22 sets the PFD antibacklash pulse width. When Bit DB22 is set to 0, the PFD
    # antibacklash pulse width is 6 ns. This setting is recommended for fractional-N use. When
    # Bit DB22 is set to 1, the PFD antibacklash pulse width is 3 ns, which results in phase
    # noise and spur improvements in integer-N operation. For fractional-N operation, the 3 ns
    # setting is not recommended.

    self._adf._write_element_by_name('ABP', int(bool(value)))



@property
def abp(self):
    return self._adf.map.elements['ABP']['element'].value



def _set_charge_cancelation(self, value = True):
    # Setting the DB21 bit to 1 enables charge pump charge cancel- ation. This has the effect of
    # reducing PFD spurs in integer-N mode. In fractional-N mode, this bit should be set to 0.

    self._adf._write_element_by_name('Charge_Cancelation', int(bool(value)))



@property
def charge_cancelation(self):
    return self._adf.map.elements['Charge_Cancelation']['element'].value



def _set_csr_enable(self, value = True):
    # Setting the DB18 bit to 1 enables cycle slip reduction. CSR is a method for improving lock
    # times. Note that the signal at the phase frequency detector (PFD) must have a 50% duty
    # cycle for cycle slip reduction to work. The charge pump current setting must also be set
    # to a minimum. For more information, see the Cycle Slip Reduction for Faster Lock Times
    # section.

    self._adf._write_element_by_name('CSR_Enable', int(bool(value)))



@property
def csr_enable(self):
    return self._adf.map.elements['CSR_Enable']['element'].value



def _set_clock_divider_mode(self, value = True):
    # Bits[DB16:DB15] must be set to 10 to activate phase resync (see the Phase Resync section).
    # These bits must be set to 01 to activate fast lock (see the Fast Lock Timer and Register
    # Sequences section). Setting Bits[DB16:DB15] to 00 disables the clock divider (see Figure
    # 27).

    self._adf._write_element_by_name('Clock_Divider_Mode', int(bool(value)))



@property
def clock_divider_mode(self):
    return self._adf.map.elements['Clock_Divider_Mode']['element'].value



def _set_clock_divider_value(self, value = True):
    # Bits[DB14:DB3] set the 12-bit clock divider value. This value is the timeout counter for
    # activation of phase resync (see the Phase Resync section). The clock divider value also
    # sets the timeout counter for fast lock (see the Fast Lock Timer and Register Sequences
    # section).

    self._adf._write_element_by_name('Clock_Divider_Value', int(bool(value)))



@property
def clock_divider_value(self):
    return self._adf.map.elements['Clock_Divider_Value']['element'].value



def _set_feedback_select(self, value = True):
    # The DB23 bit selects the feedback from the VCO output to the N counter. When this bit is
    # set to 1, the signal is taken directly from the VCO. When this bit is set to 0, the signal
    # is taken from the output of the output dividers. The dividers enable coverage of the wide
    # frequency band (34.375 MHz to 4.4 GHz). When the dividers are enabled and the feedback
    # signal is taken from the output, the RF output signals of two separately configured PLLs
    # are in phase. This is useful in some applications where the positive interference of
    # signals is required to increase the power.

    self._adf._write_element_by_name('Feedback_Select', int(bool(value)))



@property
def feedback_select(self):
    return self._adf.map.elements['Feedback_Select']['element'].value



def _set_rf_divider_select(self, value = True):
    # Bits[DB22:DB20] select the value of the RF output divider (see Figure 28).

    self._adf._write_element_by_name('RF_Divider_Select', int(bool(value)))



@property
def rf_divider_select(self):
    return self._adf.map.elements['RF_Divider_Select']['element'].value



def _set_band_select_clock_divider_value(self, value = True):
    # Bits[DB19:DB12] set a divider for the band select logic clock input. By default, the
    # output of the R counter is the value used to clock the band select logic, but, if this
    # value is too high (>125 kHz), a divider can be switched on to divide the R counter output
    # to a smaller value (see Figure 28).

    self._adf._write_element_by_name('Band_Select_Clock_Divider_Value', int(bool(value)))



@property
def band_select_clock_divider_value(self):
    return self._adf.map.elements['Band_Select_Clock_Divider_Value']['element'].value



def _set_vco_power_down(self, value = True):
    # Setting the DB11 bit to 0 powers the VCO up; setting this bit to 1 powers the VCO down.

    self._adf._write_element_by_name('VCO_Power-Down', int(bool(value)))



@property
def vco_power_down(self):
    return self._adf.map.elements['VCO_Power-Down']['element'].value



def _set_mtld(self, value = True):
    # When the DB10 bit is set to 1, the supply current to the RF output stage is shut down
    # until the part achieves lock, as measured by the digital lock detect circuitry.

    self._adf._write_element_by_name('MTLD', int(bool(value)))



@property
def mtld(self):
    return self._adf.map.elements['MTLD']['element'].value



def _set_aux_output_select(self, value = True):
    # The DB9 bit sets the auxiliary RF output. If DB9 is set to 0, the auxiliary RF output is
    # the output of the RF dividers; if DB9 is set to 1, the auxiliary RF output is the
    # fundamental VCO frequency.

    self._adf._write_element_by_name('AUX_Output_Select', int(bool(value)))



@property
def aux_output_select(self):
    return self._adf.map.elements['AUX_Output_Select']['element'].value



def _set_aux_output_enable(self, value = True):
    # The DB8 bit enables or disables the auxiliary RF output. If DB8 is set to 0, the auxiliary
    # RF output is disabled; if DB8 is set to 1, the auxiliary RF output is enabled.

    self._adf._write_element_by_name('AUX_Output_Enable', int(bool(value)))



@property
def aux_output_enable(self):
    return self._adf.map.elements['AUX_Output_Enable']['element'].value



def _set_aux_output_power(self, value = True):
    # Bits[DB7:DB6] set the value of the auxiliary RF output power level (see Figure 28).

    self._adf._write_element_by_name('AUX_Output_Power', int(bool(value)))



@property
def aux_output_power(self):
    return self._adf.map.elements['AUX_Output_Power']['element'].value



def _set_rf_output_enable(self, value = True):
    # The DB5 bit enables or disables the primary RF output. If DB5 is set to 0, the primary RF
    # output is disabled; if DB5 is set to 1, the primary RF output is enabled.

    self._adf._write_element_by_name('RF_Output_Enable', int(bool(value)))



@property
def rf_output_enable(self):
    return self._adf.map.elements['RF_Output_Enable']['element'].value



def _set_output_power(self, value = True):
    # Bits[DB4:DB3] set the value of the primary RF output power level (see Figure 28).

    self._adf._write_element_by_name('Output_Power', int(bool(value)))



@property
def output_power(self):
    return self._adf.map.elements['Output_Power']['element'].value



def _set_lock_detect_pin_operation(self, value = True):
    # Bits[DB23:DB22] set the operation of the lock detect (LD) pin (see Figure 29).

    self._adf._write_element_by_name('Lock_Detect_Pin_Operation', int(bool(value)))



@property
def lock_detect_pin_operation(self):
    return self._adf.map.elements['Lock_Detect_Pin_Operation']['element'].value
