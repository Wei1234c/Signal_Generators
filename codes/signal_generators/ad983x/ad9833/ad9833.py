# datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/ad9833.pdf


try:
    from ...interfaces import Device
    from ...register import Register, Element, math
    # from signal_generators.adapters import SPI
    from ...adapters import SPI
except:
    from interfaces import Device
    from register import Register, Element, math
    from adapters import SPI

SPEED_OF_LIGHT_M_S = 299792458

PI2 = 2 * math.pi
DEGREES_IN_PI2 = 360
FREQ_DEFAULT = 440
FREQ_MCLK = int(25e6)
POW2_28 = 2 ** 28

PHASE_DEFAULT = 0
POW2_12 = 2 ** 12
BITS_PER_DEG = POW2_12 / DEGREES_IN_PI2
DEGREE_TO_RAD = PI2 / DEGREES_IN_PI2
RAD_TO_DEGREE = DEGREES_IN_PI2 / PI2

SHAPES_CONFIG = {'sine'       : {'OPBITEN': 0, 'SLEEP12': 0, 'Mode': 0, 'DIV2': 0},
                 'triangle'   : {'OPBITEN': 0, 'SLEEP12': 0, 'Mode': 1, 'DIV2': 0},
                 'square'     : {'OPBITEN': 1, 'SLEEP12': 1, 'Mode': 0, 'DIV2': 1},
                 'half_square': {'OPBITEN': 1, 'SLEEP12': 1, 'Mode': 0, 'DIV2': 0}, }

SHAPE_DEFAULT = 'sine'



class ControlRegister(Register):

    def __init__(self, name = 'Control', code_name = None, address = None, description = 'AD9833 Control Register'):
        super().__init__(name = name,
                         code_name = code_name,
                         address = address,
                         description = description,
                         elements = [
                             Element(name = 'D15', idx_lowest_bit = 15, n_bits = 1, value = 0, read_only = True,
                                     description = '''D15'''),
                             Element(name = 'D14', idx_lowest_bit = 14, n_bits = 1, value = 0, read_only = True,
                                     description = '''D14'''),
                             Element(name = 'B28', idx_lowest_bit = 13, n_bits = 1, value = 1,
                                     description = '''Two write operations are required to load a complete word into either of the frequency registers. B28 = 1 allows a complete word to be loaded into a frequency register in two consecutive writes. The first write contains the 14 LSBs of the frequency word, and the next write contains the 14 MSBs. The first two bits of each 16-bit word define the frequency register to which the word is loaded, and should therefore be the same for both of the consecutive writes. See Table 8 for the appropriate addresses. The write to the frequency register occurs after both words have been loaded; therefore, the register never holds an intermediate value. An example of a complete 28-bit write is shown in Table 9. When B28 = 0, the 28-bit frequency register operates as two 14-bit registers, one containing the 14 MSBs and the other containing the 14 LSBs. This means that the 14 MSBs of the frequency word can be altered independent of the 14 LSBs, and vice versa. To alter the 14 MSBs or the 14 LSBs, a single write is made to the appropriate frequency address. The control bit D12 (HLB) informs the AD9833 whether the bits to be altered are the 14 MSBs or 14 LSBs.'''),
                             Element(name = 'HLB', idx_lowest_bit = 12,
                                     description = '''This control bit allows the user to continuously load the MSBs or LSBs of a frequency register while ignoring the remaining 14 bits. This is useful if the complete 28-bit resolution is not required. HLB is used in conjunction with D13 (B28). This control bit indicates whether the 14 bits being loaded are being transferred to the 14 MSBs or 14 LSBs of the addressed frequency register. D13 (B28) must be set to 0 to be able to change the MSBs and LSBs of a frequency word separately. When D13 (B28) = 1, this control bit is ignored. HLB = 1 allows a write to the 14 MSBs of the addressed frequency register. HLB = 0 allows a write to the 14 LSBs of the addressed frequency register.'''),
                             Element(name = 'FSELECT', idx_lowest_bit = 11,
                                     description = '''The FSELECT bit defines whether the FREQ0 register or the FREQ1 register is used in the phase accumulator.'''),
                             Element(name = 'PSELECT', idx_lowest_bit = 10,
                                     description = '''The PSELECT bit defines whether the PHASE0 register or the PHASE1 register data is added to the output of the phase accumulator.'''),
                             Element(name = 'Reserved_9', idx_lowest_bit = 9, read_only = True,
                                     description = '''This bit should be set to 0.'''),
                             Element(name = 'Reset', idx_lowest_bit = 8,
                                     description = '''Reset = 1 resets internal registers to 0, which corresponds to an analog output of midscale. Reset = 0 disables reset. This function is explained further in Table 13.'''),
                             Element(name = 'SLEEP1', idx_lowest_bit = 7,
                                     description = '''When SLEEP1 = 1, the internal MCLK clock is disabled, and the DAC output remains at its present value because the NCO is no longer accumulating. When SLEEP1 = 0, MCLK is enabled. This function is explained further in Table 14.'''),
                             Element(name = 'SLEEP12', idx_lowest_bit = 6,
                                     description = '''SLEEP12 = 1 powers down the on-chip DAC. This is useful when the AD9833 is used to output the MSB of the DAC data. SLEEP12 = 0 implies that the DAC is active. This function is explained further in Table 14.'''),
                             Element(name = 'OPBITEN', idx_lowest_bit = 5,
                                     description = '''The function of this bit, in association with D1 (mode), is to control what is output at the VOUT pin. This is explained further in Table 15. When OPBITEN = 1, the output of the DAC is no longer available at the VOUT pin. Instead, the MSB (or MSB/2) of the DAC data is connected to the VOUT pin. This is useful as a coarse clock source. The DIV2 bit controls whether it is the MSB or MSB/2 that is output. When OPBITEN = 0, the DAC is connected to VOUT. The mode bit determines whether it is a sinusoidal or a ramp output that is available.'''),
                             Element(name = 'Reserved_4', idx_lowest_bit = 4, read_only = True,
                                     description = '''This bit should be set to 0.'''),
                             Element(name = 'DIV2', idx_lowest_bit = 3,
                                     description = '''DIV2 is used in association with D5 (OPBITEN). This is explained further in Table 15. When DIV2 = 1, the MSB of the DAC data is passed directly to the VOUT pin. When DIV2 = 0, the MSB/2 of the DAC data is output at the VOUT pin.'''),
                             Element(name = 'Reserved_2', idx_lowest_bit = 2, read_only = True,
                                     description = '''This bit should be set to 0.'''),
                             Element(name = 'Mode', idx_lowest_bit = 1,
                                     description = '''This bit is used in association with OPBITEN (D5). The function of this bit is to control what is output at the VOUT pin when the on-chip DAC is connected to VOUT. This bit should be set to 0 if the control bit OPBITEN = 1. This is explained further in Table 15. When mode = 1, the SIN ROM is bypassed, resulting in a triangle output from the DAC. When mode = 0, the SIN ROM is used to convert the phase information into amplitude information, which results in a sinusoidal signal at the output.'''),
                             Element(name = 'Reserved_0', idx_lowest_bit = 0, read_only = True,
                                     description = '''This bit should be set to 0.''')],
                         default_value = 0x2000)



class FrequencyRegister(Register):

    def __init__(self, idx, freq = FREQ_DEFAULT, freq_mclk = FREQ_MCLK,
                 name = 'Frequency', code_name = None, address = None, description = 'AD9833 Frequency Register'):
        super().__init__(name = name,
                         code_name = code_name,
                         address = address,
                         description = description,
                         elements = [
                             Element(name = 'Index', idx_lowest_bit = 14, n_bits = 2, value = idx + 1, read_only = True,
                                     description = '''Index'''),
                             Element(name = 'Frequency', idx_lowest_bit = 0, n_bits = 14, value = 0,
                                     description = '''Frequency''')],
                         default_value = int((idx + 1) << 14))
        self.idx = idx
        self._frequency = freq
        self.freq_mclk = freq_mclk


    def reset(self):
        self.frequency = FREQ_DEFAULT
        super().reset()


    def dump(self, as_hex = False):
        len_name_field = super().dump(as_hex = as_hex)
        print('{:<{}s}:  {:0.2f}'.format('[ Hz ]', len_name_field + 5, self.frequency))
        if self.frequency != 0:
            print('{:<{}s}:  {:0.5e}'.format('[ Wave length (m) ]', len_name_field + 5,
                                             SPEED_OF_LIGHT_M_S / self.frequency))
            print('{:<{}s}:  {:0.5e}'.format('[ Period (s) ]', len_name_field + 5,
                                             1 / self.frequency))
        print('{:<{}s}:  {}'.format('[ MCLK ]', len_name_field + 5, self.freq_mclk))


    @property
    def frequency(self):
        return self._frequency


    @frequency.setter
    def frequency(self, frequency):
        assert abs(frequency) <= self.freq_mclk // 2, \
            'Must frequency <= freq_mclk // 2 = {}'.format(self.freq_mclk // 2)
        self._frequency = frequency
        self._value_28_bits = int(round(frequency * POW2_28 / self.freq_mclk)) & 0xFFFFFFF


    @property
    def msw(self):
        self.elements['Frequency'].value = self._value_28_bits // 0x3FFF
        return self.bytes


    @property
    def lsw(self):
        self.elements['Frequency'].value = self._value_28_bits & 0x3FFF
        return self.bytes



class PhaseRegister(Register):

    def __init__(self, idx, phase = PHASE_DEFAULT,
                 name = 'Phase', code_name = None, address = None, description = 'AD9833 Phase Register'):
        super().__init__(name = name,
                         code_name = code_name,
                         address = address,
                         description = description,
                         elements = [Element(name = 'D15', idx_lowest_bit = 15, n_bits = 1, value = 1, read_only = True,
                                             description = '''D15'''),
                                     Element(name = 'D14', idx_lowest_bit = 14, n_bits = 1, value = 1, read_only = True,
                                             description = '''D14'''),
                                     Element(name = 'Index', idx_lowest_bit = 13, n_bits = 1, value = idx,
                                             read_only = True,
                                             description = '''Index'''),
                                     Element(name = 'Phase', idx_lowest_bit = 0, n_bits = 12, value = 0,
                                             description = '''Phase''')],
                         default_value = int(3 << 14) + int(idx << 13))
        self.idx = idx
        self._phase = phase


    def reset(self):
        self._phase = PHASE_DEFAULT
        super().reset()


    def dump(self, as_hex = False):
        len_name_field = super().dump(as_hex = as_hex)
        print('{:<{}s}:  {:0.2f}'.format('[ Degree ]', len_name_field + 5, self.phase))


    @property
    def phase(self):
        return self._phase


    @phase.setter
    def phase(self, phase):
        self._phase = phase
        self.elements['Phase'].value = int(round((phase % DEGREES_IN_PI2) * POW2_12 / DEGREES_IN_PI2)) & 0xFFF



class AD9833(Device):
    REGISTERS_COUNT = 2
    DEBUG_MODE = False


    def __init__(self, spi, ss, freq = FREQ_DEFAULT, freq_correction = 0, phase = PHASE_DEFAULT, shape = 'sine',
                 freq_mclk = FREQ_MCLK,
                 commands = None):
        Device.__init__(self, freq = freq, freq_correction = freq_correction, phase = phase, shape = shape,
                        commands = commands)
        self._spi = SPI(spi, ss)
        self.freq_mclk = freq_mclk
        self.control_register = ControlRegister()
        self.frequency_registers = {i: FrequencyRegister(idx = i) for i in range(self.REGISTERS_COUNT)}
        self.phase_registers = {i: PhaseRegister(idx = i) for i in range(self.REGISTERS_COUNT)}
        self._active_freq_reg_idx = 0
        self._active_phase_reg_idx = 0
        self.init()


    def init(self):
        self.enable_output(False)
        for i in range(self.REGISTERS_COUNT):
            self.set_frequency(idx = i, freq = self.frequency, freq_mclk = self.freq_mclk)
            self.set_phase(idx = i, phase = self.phase)
        self.select_freq_source(0)
        self.select_phase_source(0)
        self.shape = self.shape
        self.start()


    def _update_register(self, register, reset = False):
        if reset:
            register.reset()
        self._spi.write(register.bytes)
        self._dump_register(register)


    def _update_control_register(self, reset = False):
        self._update_register(self.control_register, reset = reset)


    def _update_frequency_register(self, register, reset = False):
        if reset:
            register.reset()
        self._enable_B28(True)
        self._spi.write(register.lsw)
        self._spi.write(register.msw)
        self._dump_register(register)


    def _update_all_registers(self, reset = False):
        self._update_control_register(reset = reset)
        for i in range(self.REGISTERS_COUNT):
            self._update_frequency_register(self.frequency_registers[i], reset = reset)
            self._update_register(self.phase_registers[i], reset = reset)


    def update(self):
        self._update_all_registers(reset = False)


    def reset(self):
        self._update_all_registers(reset = True)


    def dump(self, as_hex = False):
        self.control_register.dump(as_hex = as_hex)
        for i in range(self.REGISTERS_COUNT):
            self.frequency_registers[i].dump(as_hex = as_hex)
            self.phase_registers[i].dump(as_hex = as_hex)


    @property
    def freq_resolution(self):
        return self.freq_mclk / POW2_28


    @property
    def phase_resolution(self):
        return DEGREES_IN_PI2 / POW2_12


    def set_frequency(self, freq, idx = None, freq_correction = 0, freq_mclk = None):
        freq_reg = self.frequency_registers[self._active_freq_reg_idx if idx is None else idx]
        freq_reg.frequency = freq + (self.freq_correction if freq_correction is None else freq_correction)
        freq_reg.freq_mclk = self.freq_mclk if freq_mclk is None else freq_mclk
        self._update_frequency_register(freq_reg)


    def set_phase(self, phase, idx = None):
        phase_reg = self.phase_registers[self._active_phase_reg_idx if idx is None else idx]
        phase_reg.phase = phase
        self._update_register(phase_reg)


    def select_freq_source(self, idx):
        self._active_freq_reg_idx = idx
        self.control_register.elements['FSELECT'].value = idx
        self._update_control_register()


    def select_phase_source(self, idx):
        self._active_phase_reg_idx = idx
        self.control_register.elements['PSELECT'].value = idx
        self._update_control_register()


    @property
    def current_frequency_register(self):
        return self.frequency_registers[self._active_freq_reg_idx]


    @property
    def current_frequency(self):
        return self.current_frequency_register.frequency


    @property
    def current_phase_register(self):
        return self.phase_registers[self._active_phase_reg_idx]


    @property
    def current_phase(self):
        return self.current_phase_register.phase


    @Device.shape.setter
    def shape(self, shape):
        assert shape in SHAPES_CONFIG.keys(), 'Must be either {}'.format('/'.join(SHAPES_CONFIG.keys()))
        self._shape = shape
        for k in SHAPES_CONFIG[shape].keys():
            self.control_register.elements[k].value = SHAPES_CONFIG[shape][k]
        self._update_control_register()


    def apply_signal(self, freq = None, freq_correction = None, freq_mclk = None, phase = None, shape = None):
        self.set_frequency(freq = self.frequency if freq is None else freq,
                           freq_correction = freq_correction,
                           freq_mclk = freq_mclk)
        self.set_phase(phase = self.phase if phase is None else phase)
        self.shape = self.shape if shape is None else shape


    def enable(self, value):
        self.enabled = value
        if value:
            self.shape = self.shape  # restore bit SLEEP12 according to shape.
        self._enable_internal_clock(value)
        self.enable_output(value)


    def enable_output(self, value = True):
        self.control_register.elements['Reset'].value = int(not bool(value))
        self._update_control_register()


    def start(self):
        self.enable(True)


    def pause(self):
        self.enable(False)


    def resume(self):
        self.enable(True)


    def stop(self):
        self._enable_DAC(False)
        self.pause()


    def close(self):
        self.stop()


    def _dump_register(self, register):
        if self.DEBUG_MODE:
            register.dump()


    def _enable_internal_clock(self, value = True):
        self.control_register.elements['SLEEP1'].value = int(not bool(value))
        self._update_control_register()


    def _enable_DAC(self, value = True):
        self.control_register.elements['SLEEP12'].value = int(not bool(value))
        self._update_control_register()


    def _enable_B28(self, value = True):
        self.control_register.elements['B28'].value = int(bool(value))
        self._update_control_register()
