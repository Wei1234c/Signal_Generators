# datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/ad9834.pdf


try:
    from ..ad98xx.ad98xx import *
except:
    from ad98xx import *



class ControlRegister(ControlRegister):

    def __init__(self, name = 'Control', code_name = None, address = None, description = 'AD9834 Control Register'):
        super().__init__(name = name, code_name = code_name, address = address, description = description)

        self._elements[-10] = Element(name = 'PIN_SW', idx_lowest_bit = 9, n_bits = 1, value = 0,
                                      description = '''Functions that select frequency and phase registers, reset internal registers, and power down the DAC can be implemented using either software or hardware. PIN/SW selects the source of control for these functions.
PIN/SW = 1 implies that the functions are being controlled using the appropriate control pins.
PIN/SW = 0 implies that the functions are being controlled using the appropriate control bits.''')

        self._elements[-5] = Element(name = 'SIGN_PIB', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                     description = '''The function of this bit is to control what is output at the SIGN BIT OUT pin.
SIGN/PIB = 1, the on-board comparator is connected to SIGN BIT OUT. After filtering the sinusoidal output from the DAC, the waveform can be applied to the comparator to generate a square waveform. Refer to Table 17.
SIGN/PIB = 0, the MSB (or MSB/2) of the DAC data is connected to the SIGN BIT OUT pin. Bit DIV2 controls whether it is the MSB or MSB/2 that is output.''')

        self.default_value = 0x2000



class AD9834(AD98xx):
    DEBUG_MODE = False
    REGISTERS_COUNT = 2
    FREQ_MCLK = int(75e6)


    def __init__(self, spi, ss,
                 freq = FREQ_DEFAULT, freq_correction = 0, phase = PHASE_DEFAULT, shape = SHAPE_DEFAULT,
                 freq_mclk = FREQ_MCLK, commands = None,
                 pin_fselect = None, pin_pselect = None, pin_reset = None, pin_sleep = None):

        super().__init__(spi, ss,
                         freq = freq, freq_correction = freq_correction, phase = phase, shape = shape,
                         freq_mclk = freq_mclk, commands = commands)

        self.pin_fselect = pin_fselect
        self.pin_pselect = pin_pselect
        self.pin_reset = pin_reset
        self.pin_sleep = pin_sleep

        self.control_register = ControlRegister()  # need to use AD9834's own ControlRegister
        self.init()


    def enable_comparator(self, value = True):
        self._action = 'enable_comparator {}'.format(value)
        if value:
            self.control_register.elements['OPBITEN'].value = 1
            self.control_register.elements['Mode'].value = 0
            self.control_register.elements['SIGN_PIB'].value = 1
            self.control_register.elements['DIV2'].value = 1
        else:
            self.shape = self.shape
            self.control_register.elements['SIGN_PIB'].value = 0
        self._update_control_register()


    @property
    def pin_control_enabled(self):
        return bool(self.control_register.elements['PIN_SW'].value)


    def enable_pin_control(self, value = True):
        self._action = 'enable_pin_control {}'.format(value)
        self.control_register.elements['PIN_SW'].value = int(bool(value))
        self._update_control_register()


    def enable_output(self, value = True):
        if self.pin_control_enabled:
            _ = self.pin_reset.low() if value else self.pin_reset.high()
        super().enable_output(value)


    def select_freq_source(self, idx):
        if self.pin_control_enabled:
            _ = self.pin_fselect.low() if (idx & 0x1 == 0) else self.pin_fselect.high()
        super().select_freq_source(idx)


    def select_phase_source(self, idx):
        if self.pin_control_enabled:
            _ = self.pin_pselect.low() if (idx & 0x1 == 0) else self.pin_pselect.high()
        super().select_phase_source(idx)



    def _enable_DAC(self, value = True):
        if self.pin_control_enabled:
            _ = self.pin_sleep.low() if value else self.pin_sleep.high()
        super()._enable_DAC(value)