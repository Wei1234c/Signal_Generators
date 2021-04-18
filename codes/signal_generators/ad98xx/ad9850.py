# datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/AD9850.pdf


try:
    from ..ad98xx.ad98xx import *
except:
    from ad98xx import *

FREQ_MCLK = int(125e6)
BITS_PER_DEG = POW2_5 / DEGREES_IN_PI2



class ControlRegister(Register):

    def __init__(self, freq = FREQ_DEFAULT, freq_mclk = FREQ_MCLK, phase = PHASE_DEFAULT,
                 name = 'Control', code_name = None, address = None, description = 'AD9850 Control Register'):
        super().__init__(name = name,
                         code_name = code_name,
                         address = address,
                         description = description,
                         elements = [
                             Element(name = 'Phase', idx_lowest_bit = 35, n_bits = 5, value = 0,
                                     description = '''Phase'''),
                             Element(name = 'Power_Down', idx_lowest_bit = 34, n_bits = 1, value = 0,
                                     description = '''Power_Down'''),
                             Element(name = 'Control', idx_lowest_bit = 32, n_bits = 2, value = 0, read_only = True,
                                     description = '''Control'''),
                             Element(name = 'Frequency', idx_lowest_bit = 0, n_bits = 32, value = 0,
                                     description = '''Frequency''')],
                         default_value = 0x0400000000)

        self._frequency = freq
        self._phase = phase
        self.freq_mclk = freq_mclk


    def reset(self):
        self.frequency = FREQ_DEFAULT
        self.phase = PHASE_DEFAULT
        super().reset()


    @property
    def frequency(self):
        return self._frequency


    @frequency.setter
    def frequency(self, frequency):
        assert abs(frequency) <= self.freq_mclk // 2, \
            'Must frequency <= freq_mclk // 2 = {}'.format(self.freq_mclk // 2)
        self._frequency = frequency
        self.elements['Frequency'].value = int(round(frequency * POW2_32 / self.freq_mclk)) & 0xFFFFFFFF


    @property
    def phase(self):
        return self._phase


    @phase.setter
    def phase(self, phase):
        self._phase = phase
        self.elements['Phase'].value = int(round((phase % DEGREES_IN_PI2) * POW2_5 / DEGREES_IN_PI2)) & 0x1F


    @property
    def bytes(self):
        return array('B', self.value.to_bytes(self.n_bytes, 'little'))  # byteorder: LSB first


    def print(self, as_hex = False):
        len_name_field = super().print(as_hex = as_hex)
        print('{:<{}s}:  {:0.2f}'.format('[ Hz ]', len_name_field + 5, self.frequency))
        if self.frequency != 0:
            print('{:<{}s}:  {:0.5e}'.format('[ Wave length (m) ]', len_name_field + 5,
                                             SPEED_OF_LIGHT_M_S / self.frequency))
            print('{:<{}s}:  {:0.5e}'.format('[ Period (s) ]', len_name_field + 5,
                                             1 / self.frequency))
        print('{:<{}s}:  {}'.format('[ MCLK ]', len_name_field + 5, self.freq_mclk))
        print('{:<{}s}:  {:0.2f}'.format('[ Phase degree ]', len_name_field + 5, self.phase))



class AD9850(AD98xx):
    DEBUG_MODE = False
    REGISTERS_COUNT = 1
    FREQ_MCLK = int(125e6)

    SHAPES_CONFIG = {'sine': None}


    def __init__(self, bus, pin_reset, freq = FREQ_DEFAULT, freq_correction = 0, phase = PHASE_DEFAULT,
                 shape = SHAPE_DEFAULT,
                 freq_mclk = FREQ_MCLK, commands = None):

        Device.__init__(self, freq = freq, freq_correction = freq_correction, phase = phase, shape = shape,
                        commands = commands)
        self._bus = bus
        self.pin_reset = pin_reset
        self.freq_mclk = freq_mclk
        self.control_register = ControlRegister()
        self.init()


    def init(self):
        self._action = 'init'
        self.reset()
        self.enable_output(False)
        self.set_frequency(freq = self.frequency, freq_mclk = self.freq_mclk)
        self.set_phase(phase = self.phase)
        self.shape = self.shape
        self.start()


    def _update_frequency_register(self, register, reset = False):
        raise NotImplementedError()


    def write_all_registers(self, reset = False):
        self._update_control_register(reset = reset)


    def print(self, as_hex = False):
        self.control_register.print(as_hex = as_hex)


    @property
    def freq_resolution(self):
        return self.freq_mclk / POW2_32


    @property
    def phase_resolution(self):
        return DEGREES_IN_PI2 / POW2_5


    def set_frequency(self, freq, freq_correction = None, freq_mclk = None):
        freq = freq + (self.freq_correction if freq_correction is None else freq_correction)
        self._action = 'set_frequency {}'.format(freq)

        self.control_register.frequency = freq
        self.control_register.freq_mclk = self.freq_mclk if freq_mclk is None else freq_mclk
        self._update_control_register()


    def set_phase(self, phase):
        self._action = 'set_phase {}'.format(phase)
        self.control_register.phase = phase
        self._update_control_register()


    def select_freq_source(self, idx):
        self._action = 'select_freq_source {}'.format(idx)
        raise NotImplementedError()


    def select_phase_source(self, idx):
        self._action = 'select_phase_source {}'.format(idx)
        raise NotImplementedError()


    @property
    def active_freq_reg_idx(self):
        raise NotImplementedError()


    @property
    def active_phase_reg_idx(self):
        raise NotImplementedError()


    @property
    def current_frequency_register(self):
        return self.control_register


    @property
    def current_frequency(self):
        return self.control_register.frequency


    @property
    def current_phase_register(self):
        return self.control_register


    @property
    def current_phase(self):
        return self.control_register.phase


    @AD98xx.shape.setter
    def shape(self, shape):
        self._action = 'set shape {}'.format(shape)
        self._shape = shape


    def reset(self):
        self._action = 'reset'
        if self.pin_reset is not None:
            self.pin_reset.high()
            self.pin_reset.low()
        super().reset()


    def enable_output(self, value = True):
        self._action = 'enable_output {}'.format(value)
        self._power_down(not value)


    def _power_down(self, value = True):
        self.control_register.elements['Power_Down'].value = int(bool(value))
        self._update_control_register()


    def _enable_internal_clock(self, value = True):
        self._action = '_enable_internal_clock {}'.format(value)
        self._power_down(not value)


    def _enable_DAC(self, value = True):
        self._power_down(not value)


    def _enable_B28(self, value = True):
        raise NotImplementedError()
