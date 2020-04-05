# datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/ad983x.pdf


try:
    from ..ad98xx.ad98xx import *
    from ..adapters import SPI
    from ..register import Element
except:
    from ad983x import *
    from adapters import SPI
    from register import Element



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

        self._default_value = 0x2000



class AD9834(AD98xx):
    REGISTERS_COUNT = 2
    DEBUG_MODE = False
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
        self.control_register.elements['PIN_SW'].value = int(bool(value))
        self._update_control_register()


    def enable_output(self, value = True):
        if self.pin_control_enabled:
            _ = self.pin_reset.low() if value else self.pin_reset.high()

        self.control_register.elements['Reset'].value = int(not bool(value))
        self._update_control_register()


    def select_freq_source(self, idx):
        if self.pin_control_enabled:
            _ = self.pin_fselect.low() if (idx & 0x1 == 0) else self.pin_fselect.high()

        self.control_register.elements['FSELECT'].value = idx & 0x1
        self._update_control_register()


    def select_phase_source(self, idx):
        if self.pin_control_enabled:
            _ = self.pin_pselect.low() if (idx & 0x1 == 0) else self.pin_pselect.high()

        self.control_register.elements['PSELECT'].value = idx
        self._update_control_register()


    def _enable_DAC(self, value = True):
        if self.pin_control_enabled:
            _ = self.pin_sleep.low() if value else self.pin_sleep.high()

        self.control_register.elements['SLEEP12'].value = int(not bool(value))
        self._update_control_register()