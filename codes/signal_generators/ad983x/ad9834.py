# datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/ad983x.pdf


try:
    from ..ad983x.ad983x import *
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



class AD9834(AD983x):
    REGISTERS_COUNT = 2
    DEBUG_MODE = False


    def __init__(self, spi, ss, freq = FREQ_DEFAULT, freq_correction = 0, phase = PHASE_DEFAULT, shape = SHAPE_DEFAULT,
                 freq_mclk = FREQ_MCLK, commands = None):
        Device.__init__(self, freq = freq, freq_correction = freq_correction, phase = phase, shape = shape,
                        commands = commands)
        self._spi = SPI(spi, ss)
        self.freq_mclk = freq_mclk
        self.control_register = ControlRegister()
        self.frequency_registers = {i: FrequencyRegister(idx = i) for i in range(self.REGISTERS_COUNT)}
        self.phase_registers = {i: PhaseRegister(idx = i) for i in range(self.REGISTERS_COUNT)}

        self.init()
