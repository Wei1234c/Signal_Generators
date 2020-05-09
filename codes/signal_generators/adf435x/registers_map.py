try:
    from utilities.register import *
except:
    from register import *



def _get_all_registers():
    registers = []

    registers.append(Register(name = 'REGISTER_0', address = 0, description = 'REGISTER_0',
                              elements = [Element(name = 'Reserved_31', idx_lowest_bit = 31, n_bits = 1, value = 0,
                                                  read_only = True,
                                                  description = '''Reserved'''),
                                          Element(name = 'INT', idx_lowest_bit = 15, n_bits = 16, value = 0,
                                                  description = '''The 16 INT bits (Bits[DB30:DB15]) set the INT value, which determines the integer part of the feedback division factor. The INT value is used in Equation 1 (see the INT, FRAC, MOD, and R Counter Relationship section). Integer values from 23 to 65,535 are allowed for the 4/5 prescaler; for the 8/9 prescaler, the minimum integer value is 75.'''),
                                          Element(name = 'FRAC', idx_lowest_bit = 3, n_bits = 12, value = 0,
                                                  description = '''The 12 FRAC bits (Bits[DB14:DB3]) set the numerator of the fraction that is input to the Σ-Δ modulator. This fraction, along with the INT value, specifies the new frequency channel that the synthesizer locks to, as shown in the RF Synthesizer—A Worked Example section. FRAC values from 0 to (MOD ? 1) cover channels over a frequency range equal to the PFD refer- ence frequency.'''),
                                          Element(name = 'Index', idx_lowest_bit = 0, n_bits = 3, value = 0,
                                                  description = '''When Bits[C3:C1] are set to 000, Register 0 is programmed. Figure 24 shows the input data format for programming this register.'''),
                                          ], default_value = 0))

    registers.append(Register(name = 'REGISTER_1', address = 1, description = 'REGISTER_1',
                              elements = [Element(name = 'Reserved_29', idx_lowest_bit = 29, n_bits = 3, value = 0,
                                                  read_only = True,
                                                  description = '''Reserved'''),
                                          Element(name = 'Phase_Adjust', idx_lowest_bit = 28, n_bits = 1, value = 0,
                                                  description = '''The phase adjust bit (Bit DB28) enables adjustment of the output phase of a given output frequency. When phase adjustment is enabled (Bit DB28 is set to 1), the part does not perform VCO band selection or phase resync when Register 0 is updated.
When phase adjustment is disabled (Bit DB28 is set to 0), the part performs VCO band selection and phase resync (if phase resync is enabled in Register 3, Bits[DB16:DB15]) when Register 0 is updated. Disabling VCO band selection is recommended only for fixed frequency applications or for frequency deviations of
<1 MHz from the originally selected frequency.'''),
                                          Element(name = 'Prescaler_Value', idx_lowest_bit = 27, n_bits = 1, value = 0,
                                                  description = '''The dual-modulus prescaler (P/P + 1), along with the INT, FRAC, and MOD values, determines the overall division ratio from the VCO output to the PFD input. The PR1 bit (DB27) in Register 1 sets the prescaler value.
Operating at CML levels, the prescaler takes the clock from the VCO output and divides it down for the counters. The prescaler is based on a synchronous 4/5 core. When the prescaler is set to 4/5, the maximum RF frequency allowed is 3.6 GHz. Therefore, when operating the ADF4351 above 3.6 GHz, the prescaler must be set to 8/9. The prescaler limits the INT value as follows:
·??????????? Prescaler = 4/5: NMIN = 23
·??????????? Prescaler = 8/9: NMIN = 75'''),
                                          Element(name = 'Phase_Value', idx_lowest_bit = 15, n_bits = 12, value = 0,
                                                  description = '''Bits[DB26:DB15] control the phase word. The phase word must be less than the MOD value programmed in Register 1. The phase word is used to program the RF output phase from 0° to 360° with a resolution of 360°/MOD (see the Phase Resync section).
In most applications, the phase relationship between the RF signal and the reference is not important. In such applications, the phase value can be used to optimize the fractional and sub- fractional spur levels. For more information, see the Spur Consistency and Fractional Spur Optimization section.
If neither the phase resync nor the spurious optimization func- tion is used, it is recommended that the phase word be set to 1.'''),
                                          Element(name = 'MOD', idx_lowest_bit = 3, n_bits = 12, value = 0,
                                                  description = '''The 12 MOD bits (Bits[DB14:DB3]) set the fractional modulus. The fractional modulus is the ratio of the PFD frequency to the channel step resolution on the RF output. For more information, see the 12-Bit Programmable Modulus section.'''),
                                          Element(name = 'Index', idx_lowest_bit = 0, n_bits = 3, value = 0,
                                                  description = '''When Bits[C3:C1] are set to 001, Register 1 is programmed. Figure 25 shows the input data format for programming this register.'''),
                                          ], default_value = 0))

    registers.append(Register(name = 'REGISTER_2', address = 2, description = 'REGISTER_2',
                              elements = [Element(name = 'Reserved_31', idx_lowest_bit = 31, n_bits = 1, value = 0,
                                                  read_only = True,
                                                  description = '''Reserved'''),
                                          Element(name = 'Low_Noise_and_Low_Spur_Modes', idx_lowest_bit = 29,
                                                  n_bits = 2, value = 0,
                                                  description = '''The noise mode on the ADF4351 is controlled by setting Bits[DB30:DB29] in Register 2 (see Figure 26). The noise mode allows the user to optimize a design either for improved spurious performance or for improved phase noise performance.
When the low spur mode is selected, dither is enabled. Dither randomizes the fractional quantization noise so that it resembles white noise rather than spurious noise. As a result, the part is optimized for improved spurious performance. Low spur mode is normally used for fast-locking applications when the PLL closed-loop bandwidth is wide. Wide loop bandwidth is a loop bandwidth greater than 1/10 of the RFOUT channel step resolu- tion (fRES). A wide loop filter does not attenuate the spurs to the same level as a narrow loop bandwidth.
For best noise performance, use the low noise mode option. When the low noise mode is selected, dither is disabled. This mode ensures that the charge pump operates in an optimum region for noise performance. Low noise mode is extremely useful when a narrow loop filter bandwidth is available. The synthesizer ensures extremely low noise, and the filter attenuates the spurs. Figure 10 through Figure 12 show the trade-offs in a typical W-CDMA setup for different noise and spur settings.'''),
                                          Element(name = 'MUXOUT', idx_lowest_bit = 26, n_bits = 3, value = 0,
                                                  description = '''The on-chip multiplexer is controlled by Bits[DB28:DB26] (see Figure 26). Note that N counter output must be disabled for VCO band selection to operate correctly.'''),
                                          Element(name = 'Reference_Doubler', idx_lowest_bit = 25, n_bits = 1,
                                                  value = 0,
                                                  description = '''Setting the DB25 bit to 0 disables the doubler and feeds the REFIN signal directly into the 10-bit R counter. Setting this bit to 1 multi- plies the REFIN frequency by a factor of 2 before feeding it into the 10-bit R counter. When the doubler is disabled, the REFIN falling edge is the active edge at the PFD input to the fractional synthesizer. When the doubler is enabled, both the rising and falling edges of REFIN become active edges at the PFD input.
When the doubler is enabled and the low spur mode is selected, the in-band phase noise performance is sensitive to the REFIN duty cycle. The phase noise degradation can be as much as 5 dB for REFIN duty cycles outside a 45% to 55% range. The phase noise is insensitive to the REFIN duty cycle in the low noise mode and when the doubler is disabled.
The maximum allowable REFIN frequency when the doubler is enabled is 30 MHz.'''),
                                          Element(name = 'RDIV2', idx_lowest_bit = 24, n_bits = 1, value = 0,
                                                  description = '''Setting the DB24 bit to 1 inserts a divide-by-2 toggle flip-flop between the R counter and the PFD, which extends the maximum REFIN input rate. This function allows a 50% duty cycle signal to appear at the PFD input, which is necessary for cycle slip reduction.'''),
                                          Element(name = 'R_Counter', idx_lowest_bit = 14, n_bits = 10, value = 0,
                                                  description = '''The 10-bit R counter (Bits[DB23:DB14]) allows the input reference frequency (REFIN) to be divided down to produce the reference clock to the PFD. Division ratios from 1 to 1023 are allowed.'''),
                                          Element(name = 'Double_Buffer', idx_lowest_bit = 13, n_bits = 1, value = 0,
                                                  description = '''The DB13 bit enables or disables double buffering of Bits[DB22:DB20] in Register 4. For information about how double buffering works, see the Program Modes section.'''),
                                          Element(name = 'Charge_Pump_Current_Setting', idx_lowest_bit = 9, n_bits = 4,
                                                  value = 0,
                                                  description = '''Bits[DB12:DB9] set the charge pump current. This value should be set to the charge pump current that the loop filter is designed with (see Figure 26).'''),
                                          Element(name = 'LDF', idx_lowest_bit = 8, n_bits = 1, value = 0,
                                                  description = '''The DB8 bit configures the lock detect function (LDF). The LDF controls the number of PFD cycles monitored by the lock detect circuit to ascertain whether lock has been achieved. When DB8 is set to 0, the number of PFD cycles monitored is 40. When DB8 is set to 1, the number of PFD cycles monitored is 5. It is recom- mended that the DB8 bit be set to 0 for fractional-N mode and to 1 for integer-N mode.'''),
                                          Element(name = 'LDP', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = '''The lock detect precision bit (Bit DB7) sets the comparison window in the lock detect circuit. When DB7 is set to 0, the comparison window is 10 ns; when DB7 is set to 1, the window is 6 ns. The lock detect circuit goes high when n consecutive PFD cycles are less than the comparison window value; n is set by the LDF bit (DB8). For example, with DB8 = 0 and DB7 = 0, 40 consecutive PFD cycles of 10 ns or less must occur before digital lock detect goes high.
For fractional-N applications, the recommended setting for Bits[DB8:DB7] is 00; for integer-N applications, the recom- mended setting for Bits[DB8:DB7] is 11.'''),
                                          Element(name = 'Phase_Detector_Polarity', idx_lowest_bit = 6, n_bits = 1,
                                                  value = 0,
                                                  description = '''The DB6 bit sets the phase detector polarity. When a passive loop filter or a noninverting active loop filter is used, this bit should be set to 1. If an active filter with an inverting charac- teristic is used, this bit should be set to 0.'''),
                                          Element(name = 'Power_Down', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = '''The DB5 bit provides the programmable power-down mode. Setting this bit to 1 performs a power-down. Setting this bit to 0 returns the synthesizer to normal operation. In software power- down mode, the part retains all information in its registers. The register contents are lost only if the supply voltages are removed.
When power-down is activated, the following events occur:
·??????????? Synthesizer counters are forced to their load state conditions.
·??????????? VCO is powered down.
·??????????? Charge pump is forced into three-state mode.
·??????????? Digital lock detect circuitry is reset.
·??????????? RFOUT buffers are disabled.
·??????????? Input registers remain active and capable of loading and latching data.'''),
                                          Element(name = 'Charge_Pump_Three_State', idx_lowest_bit = 4, n_bits = 1,
                                                  value = 0,
                                                  description = '''Setting the DB4 bit to 1 puts the charge pump into three-state mode. This bit should be set to 0 for normal operation.'''),
                                          Element(name = 'Counter_Reset', idx_lowest_bit = 3, n_bits = 1, value = 0,
                                                  description = '''The DB3 bit is the reset bit for the R counter and the N counter of the ADF4351. When this bit is set to 1, the RF synthesizer N counter and R counter are held in reset. For normal opera- tion, this bit should be set to 0.'''),
                                          Element(name = 'Index', idx_lowest_bit = 0, n_bits = 3, value = 0,
                                                  description = '''When Bits[C3:C1] are set to 010, Register 2 is programmed. Figure 26 shows the input data format for programming this register.'''),
                                          ], default_value = 0))

    registers.append(Register(name = 'REGISTER_3', address = 3, description = 'REGISTER_3',
                              elements = [Element(name = 'Reserved_24', idx_lowest_bit = 24, n_bits = 8, value = 0,
                                                  read_only = True,
                                                  description = '''Reserved'''),
                                          Element(name = 'Band_Select_Clock_Mode', idx_lowest_bit = 23, n_bits = 1,
                                                  value = 0,
                                                  description = '''Setting the DB23 bit to 1 selects a faster logic sequence of band selection, which is suitable for high PFD frequencies and is necessary for fast lock applications. Setting the DB23 bit to 0 is recommended for low PFD (<125 kHz) values. For the faster band select logic modes (DB23 set to 1), the value of the band select clock divider must be less than or equal to 254.'''),
                                          Element(name = 'ABP', idx_lowest_bit = 22, n_bits = 1, value = 0,
                                                  description = '''Bit DB22 sets the PFD antibacklash pulse width. When Bit DB22 is set to 0, the PFD antibacklash pulse width is 6 ns. This setting is recommended for fractional-N use. When Bit DB22 is set to 1, the PFD antibacklash pulse width is 3 ns, which results in phase noise and spur improvements in integer-N operation. For fractional-N operation, the 3 ns setting is not recommended.'''),
                                          Element(name = 'Charge_Cancelation', idx_lowest_bit = 21, n_bits = 1,
                                                  value = 0,
                                                  description = '''Setting the DB21 bit to 1 enables charge pump charge cancel- ation. This has the effect of reducing PFD spurs in integer-N mode. In fractional-N mode, this bit should be set to 0.'''),
                                          Element(name = 'Reserved_19', idx_lowest_bit = 19, n_bits = 2, value = 0,
                                                  read_only = True,
                                                  description = '''Reserved'''),
                                          Element(name = 'CSR_Enable', idx_lowest_bit = 18, n_bits = 1, value = 0,
                                                  description = '''Setting the DB18 bit to 1 enables cycle slip reduction. CSR is a method for improving lock times. Note that the signal at the phase frequency detector (PFD) must have a 50% duty cycle for cycle slip reduction to work. The charge pump current setting must also be set to a minimum. For more information, see the Cycle Slip Reduction for Faster Lock Times section.'''),
                                          Element(name = 'Reserved_17', idx_lowest_bit = 17, n_bits = 1, value = 0,
                                                  read_only = True,
                                                  description = '''Reserved'''),
                                          Element(name = 'Clock_Divider_Mode', idx_lowest_bit = 15, n_bits = 2,
                                                  value = 0,
                                                  description = '''Bits[DB16:DB15] must be set to 10 to activate phase resync (see the Phase Resync section). These bits must be set to 01 to activate fast lock (see the Fast Lock Timer and Register Sequences section). Setting Bits[DB16:DB15] to 00 disables the clock divider (see Figure 27).'''),
                                          Element(name = 'Clock_Divider_Value', idx_lowest_bit = 3, n_bits = 12,
                                                  value = 0,
                                                  description = '''Bits[DB14:DB3] set the 12-bit clock divider value. This value is the timeout counter for activation of phase resync (see the Phase Resync section). The clock divider value also sets the timeout counter for fast lock (see the Fast Lock Timer and Register Sequences section).'''),
                                          Element(name = 'Index', idx_lowest_bit = 0, n_bits = 3, value = 0,
                                                  description = '''When Bits[C3:C1] are set to 011, Register 3 is programmed. Figure 27 shows the input data format for programming this register.'''),
                                          ], default_value = 0))

    registers.append(Register(name = 'REGISTER_4', address = 4, description = 'REGISTER_4',
                              elements = [Element(name = 'Reserved_24', idx_lowest_bit = 24, n_bits = 8, value = 0,
                                                  read_only = True,
                                                  description = '''Reserved'''),
                                          Element(name = 'Feedback_Select', idx_lowest_bit = 23, n_bits = 1, value = 0,
                                                  description = '''The DB23 bit selects the feedback from the VCO output to the N counter. When this bit is set to 1, the signal is taken directly from the VCO. When this bit is set to 0, the signal is taken from the output of the output dividers. The dividers enable coverage of the wide frequency band (34.375 MHz to 4.4 GHz). When the dividers are enabled and the feedback signal is taken from the output, the RF output signals of two separately configured PLLs are in phase. This is useful in some applications where the positive interference of signals is required to increase the power.'''),
                                          Element(name = 'RF_Divider_Select', idx_lowest_bit = 20, n_bits = 3,
                                                  value = 0,
                                                  description = '''Bits[DB22:DB20] select the value of the RF output divider (see Figure 28).'''),
                                          Element(name = 'Band_Select_Clock_Divider_Value', idx_lowest_bit = 12,
                                                  n_bits = 8, value = 0,
                                                  description = '''Bits[DB19:DB12] set a divider for the band select logic clock input. By default, the output of the R counter is the value used to clock the band select logic, but, if this value is too high (>125 kHz), a divider can be switched on to divide the R counter output to a smaller value (see Figure 28).'''),
                                          Element(name = 'VCO_Power-Down', idx_lowest_bit = 11, n_bits = 1, value = 0,
                                                  description = '''Setting the DB11 bit to 0 powers the VCO up; setting this bit to 1 powers the VCO down.'''),
                                          Element(name = 'MTLD', idx_lowest_bit = 10, n_bits = 1, value = 0,
                                                  description = '''When the DB10 bit is set to 1, the supply current to the RF output stage is shut down until the part achieves lock, as measured by the digital lock detect circuitry.'''),
                                          Element(name = 'AUX_Output_Select', idx_lowest_bit = 9, n_bits = 1, value = 0,
                                                  description = '''The DB9 bit sets the auxiliary RF output. If DB9 is set to 0, the auxiliary RF output is the output of the RF dividers; if DB9 is set to 1, the auxiliary RF output is the fundamental VCO frequency.'''),
                                          Element(name = 'AUX_Output_Enable', idx_lowest_bit = 8, n_bits = 1, value = 0,
                                                  description = '''The DB8 bit enables or disables the auxiliary RF output. If DB8 is set to 0, the auxiliary RF output is disabled; if DB8 is set to 1, the auxiliary RF output is enabled.'''),
                                          Element(name = 'AUX_Output_Power', idx_lowest_bit = 6, n_bits = 2, value = 0,
                                                  description = '''Bits[DB7:DB6] set the value of the auxiliary RF output power level (see Figure 28).'''),
                                          Element(name = 'RF_Output_Enable', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = '''The DB5 bit enables or disables the primary RF output. If DB5 is set to 0, the primary RF output is disabled; if DB5 is set to 1, the primary RF output is enabled.'''),
                                          Element(name = 'Output_Power', idx_lowest_bit = 3, n_bits = 2, value = 0,
                                                  description = '''Bits[DB4:DB3] set the value of the primary RF output power level (see Figure 28).'''),
                                          Element(name = 'Index', idx_lowest_bit = 0, n_bits = 3, value = 0,
                                                  description = '''When Bits[C3:C1] are set to 100, Register 4 is programmed. Figure 28 shows the input data format for programming this register.'''),
                                          ], default_value = 0))

    registers.append(Register(name = 'REGISTER_5', address = 5, description = 'REGISTER_5',
                              elements = [Element(name = 'Reserved_24', idx_lowest_bit = 24, n_bits = 8, value = 0,
                                                  read_only = True,
                                                  description = '''Reserved'''),
                                          Element(name = 'Lock_Detect_Pin_Operation', idx_lowest_bit = 22, n_bits = 2,
                                                  value = 0,
                                                  description = '''Bits[DB23:DB22] set the operation of the lock detect (LD) pin (see Figure 29).'''),
                                          Element(name = 'Reserved_21', idx_lowest_bit = 21, n_bits = 1, value = 0,
                                                  read_only = True,
                                                  description = '''Reserved'''),
                                          Element(name = 'Reserved_19', idx_lowest_bit = 19, n_bits = 2, value = 0,
                                                  read_only = True,
                                                  description = '''Reserved'''),
                                          Element(name = 'Reserved_3', idx_lowest_bit = 3, n_bits = 16, value = 0,
                                                  read_only = True,
                                                  description = '''Reserved'''),
                                          Element(name = 'Index', idx_lowest_bit = 0, n_bits = 3, value = 0,
                                                  description = '''When Bits[C3:C1] are set to 101, Register 5 is programmed. Figure 29 shows the input data format for programming this register.'''),
                                          ], default_value = 0))

    return registers



def _get_registers_map():
    regs_map = RegistersMap(name = 'ADF4351', description = 'ADF4351 registers.', registers = _get_all_registers())

    reg = regs_map.registers['REGISTER_4']
    reg.elements['Feedback_Select'].value = 1
    reg.default_value = reg.value


    reg = regs_map.registers['REGISTER_5']
    element = reg.elements['Reserved_19']
    element.read_only = False
    element.value = 3
    element.read_only = True
    reg.default_value = reg.value

    for reg in regs_map._registers:
        ele = reg.elements['Index']
        ele.value = reg.address
        ele.read_only = True

    return regs_map
