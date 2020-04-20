# datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/ADF4351.pdf


try:
    from ..interfaces import *
    from utilities.register import Register, Element, array
    from utilities.adapters.peripherals import SPI
except:
    from interfaces import *
    from register import Register, Element, array
    from peripherals import SPI

FREQ_MCLK = int(25e6)
POW2_32 = 2 ** 32
POW2_28 = 2 ** 28
POW2_12 = 2 ** 12
POW2_5 = 2 ** 5
BITS_PER_DEG = POW2_12 / DEGREES_IN_PI2


class ADF435x(Device):
    REGISTERS_COUNT = 2
    FREQ_MCLK = int(25e6)

    SHAPES_CONFIG = {'sine'       : {'OPBITEN': 0, 'SLEEP12': 0, 'Mode': 0, 'DIV2': 0},
                     'triangle'   : {'OPBITEN': 0, 'SLEEP12': 0, 'Mode': 1, 'DIV2': 0},
                     'square'     : {'OPBITEN': 1, 'SLEEP12': 1, 'Mode': 0, 'DIV2': 1},
                     'half_square': {'OPBITEN': 1, 'SLEEP12': 1, 'Mode': 0, 'DIV2': 0}, }


    def __init__(self, spi, ss, ss_polarity = 1, freq = FREQ_DEFAULT, freq_correction = 0, phase = PHASE_DEFAULT,
                 shape = SHAPE_DEFAULT,
                 freq_mclk = FREQ_MCLK, commands = None):

        Device.__init__(self, freq = freq, freq_correction = freq_correction, phase = phase, shape = shape,
                        commands = commands)
        self._spi = SPI(spi, ss, ss_polarity = ss_polarity)
        self.freq_mclk = freq_mclk

        self.control_register = ControlRegister()
        self.frequency_registers = {i: FrequencyRegister(idx = i) for i in range(self.REGISTERS_COUNT)}
        self.phase_registers = {i: PhaseRegister(idx = i) for i in range(self.REGISTERS_COUNT)}

        self.init()


    def init(self):
        self._action = 'init'
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

        self._show_bus_data(register.bytes, address = register.address)
        self._spi.write(register.bytes)
        self._print_register(register)


    def _update_control_register(self, reset = False):
        self._update_register(self.control_register, reset = reset)


    def _update_frequency_register(self, register, reset = False):
        if reset:
            register.reset()

        self._enable_B28(True)

        self._show_bus_data(register.lsw, address = register.address)
        self._spi.write(register.lsw)

        self._show_bus_data(register.msw, address = register.address)
        self._spi.write(register.msw)

        self._print_register(register)


    def _update_all_registers(self, reset = False):
        self._update_control_register(reset = reset)
        for i in range(self.REGISTERS_COUNT):
            self._update_frequency_register(self.frequency_registers[i], reset = reset)
            self._update_register(self.phase_registers[i], reset = reset)


    def update(self):
        self._action = 'update'
        self._update_all_registers(reset = False)


    def reset(self):
        self._action = 'reset'
        self._update_all_registers(reset = True)


    def print(self, as_hex = False):
        self._action = 'print'
        self.control_register.print(as_hex = as_hex)
        for i in range(self.REGISTERS_COUNT):
            self.frequency_registers[i].print(as_hex = as_hex)
            self.phase_registers[i].print(as_hex = as_hex)


    @property
    def freq_resolution(self):
        return self.freq_mclk / POW2_28


    @property
    def phase_resolution(self):
        return DEGREES_IN_PI2 / POW2_12


    def set_frequency(self, freq, idx = None, freq_correction = None, freq_mclk = None):
        freq = freq + (self.freq_correction if freq_correction is None else freq_correction)
        idx = self.active_freq_reg_idx if idx is None else idx
        freq_mclk = self.freq_mclk if freq_mclk is None else freq_mclk
        self._action = 'set_frequency {} idx {}'.format(freq, idx)

        freq_reg = self.frequency_registers[idx]
        freq_reg.frequency = freq
        freq_reg.freq_mclk = freq_mclk
        self._update_frequency_register(freq_reg)


    def set_phase(self, phase, idx = None):
        idx = self.active_phase_reg_idx if idx is None else idx
        self._action = 'set_phase {} idx {}'.format(phase, idx)

        phase_reg = self.phase_registers[idx]
        phase_reg.phase = phase
        self._update_register(phase_reg)


    def select_freq_source(self, idx):
        self._action = 'select_freq_source {}'.format(idx)
        self.control_register.elements['FSELECT'].value = idx & 0x1
        self._update_control_register()


    def select_phase_source(self, idx):
        self._action = 'select_phase_source {}'.format(idx)
        self.control_register.elements['PSELECT'].value = idx
        self._update_control_register()


    @property
    def active_freq_reg_idx(self):
        return self.control_register.elements['FSELECT'].value


    @property
    def active_phase_reg_idx(self):
        return self.control_register.elements['PSELECT'].value


    @property
    def current_frequency_register(self):
        return self.frequency_registers[self.active_freq_reg_idx]


    @property
    def current_frequency(self):
        return self.current_frequency_register.frequency


    @property
    def current_phase_register(self):
        return self.phase_registers[self.active_phase_reg_idx]


    @property
    def current_phase(self):
        return self.current_phase_register.phase


    @Device.shape.setter
    def shape(self, shape):
        self._action = 'set shape {}'.format(shape)
        assert shape in self.SHAPES_CONFIG.keys(), 'Must be either {}'.format('/'.join(self.SHAPES_CONFIG.keys()))
        self._shape = shape
        for k in self.SHAPES_CONFIG[shape].keys():
            self.control_register.elements[k].value = self.SHAPES_CONFIG[shape][k]
        self._update_control_register()


    def apply_signal(self, freq = None, freq_correction = None, freq_mclk = None, phase = None, shape = None):
        freq = self.frequency if freq is None else freq
        phase = self.phase if phase is None else phase
        shape = self.shape if shape is None else shape
        self._action = 'apply_signal freq={} phase={} shape={}'.format(freq, phase, shape)

        self.set_frequency(freq = freq, freq_correction = freq_correction, freq_mclk = freq_mclk)
        self.set_phase(phase = phase)
        self.shape = shape


    def enable(self, value):
        self._action = 'enable {}'.format(value)
        self._enabled = value
        if value:
            self.shape = self.shape  # restore bit SLEEP12 according to shape.
        self._enable_internal_clock(value)
        self.enable_output(value)


    def enable_output(self, value = True):
        self._action = 'enable_output: {}'.format(value)
        self.control_register.elements['Reset'].value = int(not bool(value))
        self._update_control_register()


    def start(self):
        self._action = 'start'
        self.enable(True)


    def pause(self):
        self._action = 'pause'
        self.enable(False)


    def resume(self):
        self._action = 'resume'
        self.enable(True)


    def stop(self):
        self._action = 'stop'
        self._enable_DAC(False)
        self.pause()


    def close(self):
        self._action = 'close'
        self.stop()


    def _enable_internal_clock(self, value = True):
        self.control_register.elements['SLEEP1'].value = int(not bool(value))
        self._update_control_register()


    def _enable_DAC(self, value = True):
        self.control_register.elements['SLEEP12'].value = int(not bool(value))
        self._update_control_register()


    def _enable_B28(self, value = True):
        self.control_register.elements['B28'].value = int(bool(value))
        self._update_control_register()
