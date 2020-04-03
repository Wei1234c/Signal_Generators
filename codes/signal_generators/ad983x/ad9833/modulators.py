# https://en.wikipedia.org/wiki/Quadrature_amplitude_modulation

import time


try:
    from ...ad983x.ad9833.ad9833 import AD9833, FREQ_DEFAULT
except:
    from ad9833 import AD9833, FREQ_DEFAULT



class Modulator(AD9833):
    ON = 1
    OFF = 0
    SYMBOLS = (ON, OFF)


    def __init__(self, spi, ss, freq = FREQ_DEFAULT, time_ratio = 1):
        super().__init__(spi, ss, freq = freq)
        self.freq = freq
        self.time_ratio = time_ratio
        self.initialize()


    def initialize(self):
        super().reset()
        self.enable_output(False)
        self.set_frequency(freq = self.freq)
        self._symbol = self.OFF


    def reset(self):
        self.initialize()


    @property
    def symbol(self):
        return self._symbol


    @symbol.setter
    def symbol(self, symbol):
        assert symbol in self.SYMBOLS, 'Symbol must be in {}'.format(self.SYMBOLS)
        self._symbol = symbol
        self._process_symbol(symbol)


    def _process_symbol(self, symbol):
        raise NotImplementedError


    def on(self):
        self.symbol = self.ON


    def off(self):
        self.symbol = self.OFF


    def send_sequence(self, sequence):
        self.update()
        self.enable_output(True)

        try:
            for (symbol, duration) in sequence:
                self.symbol = symbol
                time.sleep(duration * self.time_ratio)
        except KeyboardInterrupt:
            print('User interrupts.')

        self.enable_output(False)



class PM(Modulator):
    FREQ_CARRIER = int(1e5)
    ON = 1
    OFF = -1


    def __init__(self, spi, ss, freq = FREQ_CARRIER):
        super().__init__(spi, ss, freq = freq)


    @Modulator.symbol.setter
    def symbol(self, symbol):
        assert self.OFF <= symbol <= self.ON, 'Must {} <= symbol <= {}.'.format(self.OFF, self.ON)
        self._symbol = symbol
        self._process_symbol(symbol)


    def _process_symbol(self, symbol):
        self.set_phase(phase = 90 * symbol)



class FM(PM):
    FREQ_CARRIER = int(1e5)
    BANDWIDTH = int(1e4)


    def __init__(self, spi, ss, freq = FREQ_CARRIER, bandwidth = BANDWIDTH):
        self.bandwidth = bandwidth
        super().__init__(spi, ss, freq = freq)
        self.initialize()


    def _process_symbol(self, symbol):
        self.set_frequency(freq = self.freq + self.bandwidth * symbol)



class OOK(Modulator):
    FREQ_CARRIER = int(4e4)


    def __init__(self, spi, ss, freq = FREQ_CARRIER, time_ratio = 500 / 517):
        super().__init__(spi, ss, freq = freq, time_ratio = time_ratio)


    def initialize(self):
        super().initialize()
        self.shape = 'sine'


    def _process_symbol(self, symbol):
        self.enable_output(symbol == self.ON)



class BFSK(Modulator):
    FREQ_CARRIER = int(1e5)
    FREQ_OFFSET = int(1e3)
    FREQ_ON = FREQ_CARRIER + FREQ_OFFSET
    FREQ_OFF = FREQ_CARRIER - FREQ_OFFSET


    def __init__(self, spi, ss, freq_on = FREQ_ON, freq_off = FREQ_OFF):
        self.freq_on = freq_on
        self.freq_off = freq_off
        super().__init__(spi, ss)


    def initialize(self):
        super().initialize()
        self.set_frequency(idx = self.ON, freq = self.freq_on)
        self.set_frequency(idx = self.OFF, freq = self.freq_off)


    def _process_symbol(self, symbol):
        self.select_freq_source(idx = symbol)



class BPSK(Modulator):
    FREQ_CARRIER = int(1e5)
    PHASE_ON = 0
    PHASE_OFF = 180


    def __init__(self, spi, ss, freq = FREQ_CARRIER, phase_on = PHASE_ON, phase_off = PHASE_OFF):
        self.phase_on = phase_on
        self.phase_off = phase_off
        super().__init__(spi, ss, freq = freq)


    def initialize(self):
        super().initialize()
        self.set_phase(idx = self.ON, phase = self.phase_on)
        self.set_phase(idx = self.OFF, phase = self.phase_off)


    def _process_symbol(self, symbol):
        self.select_phase_source(idx = symbol)



class QPSK(Modulator):
    FREQ_CARRIER = int(1e5)
    # PHASE_11 = 45
    # PHASE_01 = 135
    # PHASE_00 = 225
    # PHASE_10 = 315
    PHASES = {3: 45, 1: 135, 0: 225, 2: 315}
    SYMBOLS = list(PHASES.keys())
    ON = 3
    OFF = 0


    def __init__(self, spi, ss, freq = FREQ_CARRIER):
        super().__init__(spi, ss, freq = freq)


    def _process_symbol(self, symbol):
        self.set_phase(phase = self.PHASES[symbol])



class MultipleChannels:
    ON = 1
    OFF = 0
    SYMBOLS = (ON, OFF)


    def __init__(self, spi, ss1, ss2):
        self.generators = (Modulator(spi, ss1),
                           Modulator(spi, ss2))
        self.initialize()


    def initialize(self):
        for g in self.generators:
            g.initialize()
            g.enable_output(False)
            g._symbol = None


    def update(self):
        for g in self.generators:
            g.update()


    def enable_output(self, value = True):
        for g in self.generators:
            g.enable_output(value)


    def reset(self):
        self.initialize()


    @property
    def symbol(self):
        return self._symbol


    @symbol.setter
    def symbol(self, symbol):
        assert symbol in self.SYMBOLS, 'Symbol must be in {}'.format(self.SYMBOLS)
        self._symbol = symbol
        self._process_symbol(symbol)


    def _process_symbol(self, symbol):
        raise NotImplementedError


    def on(self):
        self.symbol = self.ON


    def off(self):
        self.symbol = self.OFF


    def send_sequence(self, sequence):
        self.update()
        self.enable_output(True)

        try:
            for (symbol, duration) in sequence:
                self.symbol = symbol
                time.sleep(duration)
        except KeyboardInterrupt:
            print('User interrupts.')

        self.enable_output(False)



class IQ(MultipleChannels):
    FREQ_CARRIER = int(1e5)
    PHASE_ON = 0
    PHASE_OFF = 180
    QUADRATURE = 90
    # PHASE_11 = 45
    # PHASE_01 = 135
    # PHASE_00 = 225
    # PHASE_10 = 315
    PHASES = {3: 45, 1: 135, 0: 225, 2: 315}
    SYMBOLS = list(PHASES.keys())
    MASK_I = 2
    MASK_Q = 1
    ON = 3
    OFF = 0
    IDX_I = 0
    IDX_Q = 1


    def __init__(self, spi, ss_I, ss_Q, freq = FREQ_CARRIER, phase_on = PHASE_ON, phase_off = PHASE_OFF):
        self.generators = (BPSK(spi, ss_I, freq = freq, phase_on = phase_on, phase_off = phase_off),
                           BPSK(spi, ss_Q, freq = freq,
                                phase_on = phase_on + self.QUADRATURE,
                                phase_off = phase_off + self.QUADRATURE))
        self.freq = freq
        self.phase_on = phase_on
        self.phase_off = phase_off
        self.initialize()


    def _process_symbol(self, symbol):
        self.generators[self.IDX_I].select_phase_source(idx = symbol & self.MASK_I)
        self.generators[self.IDX_Q].select_phase_source(idx = symbol & self.MASK_Q)



class DTMF(MultipleChannels):
    # https://en.wikipedia.org/wiki/Dual-tone_multi-frequency_signaling

    FREQUENCIES = {'row'   : (697, 770, 852, 941),
                   'column': (1209, 1336, 1477, 1633)}

    # # x 100 to be high enough to center at 115KHz for viewing spectrum with SDR
    # FREQUENCIES = {'row'   : (69700, 77000, 85200, 94100),
    #                'column': (120900, 133600, 147700, 163300)}

    TONES = {'1': (FREQUENCIES['row'][0], FREQUENCIES['column'][0]),
             '2': (FREQUENCIES['row'][0], FREQUENCIES['column'][1]),
             '3': (FREQUENCIES['row'][0], FREQUENCIES['column'][2]),
             'A': (FREQUENCIES['row'][0], FREQUENCIES['column'][3]),
             '4': (FREQUENCIES['row'][1], FREQUENCIES['column'][0]),
             '5': (FREQUENCIES['row'][1], FREQUENCIES['column'][1]),
             '6': (FREQUENCIES['row'][1], FREQUENCIES['column'][2]),
             'B': (FREQUENCIES['row'][1], FREQUENCIES['column'][3]),
             '7': (FREQUENCIES['row'][2], FREQUENCIES['column'][0]),
             '8': (FREQUENCIES['row'][2], FREQUENCIES['column'][1]),
             '9': (FREQUENCIES['row'][2], FREQUENCIES['column'][2]),
             'C': (FREQUENCIES['row'][2], FREQUENCIES['column'][3]),
             '*': (FREQUENCIES['row'][3], FREQUENCIES['column'][0]),
             '0': (FREQUENCIES['row'][3], FREQUENCIES['column'][1]),
             '#': (FREQUENCIES['row'][3], FREQUENCIES['column'][2]),
             'D': (FREQUENCIES['row'][3], FREQUENCIES['column'][3])}
    SYMBOLS = list(TONES.keys())
    IDX_FREQ_ROW = 0
    IDX_FREQ_COLUMN = 1


    def __init__(self, spi, ss_row, ss_column):
        self.generators = (Modulator(spi, ss_row), Modulator(spi, ss_column))
        self.initialize()


    def _process_symbol(self, symbol):
        self.generators[self.IDX_FREQ_ROW].set_frequency(freq = self.TONES[symbol][self.IDX_FREQ_ROW])
        self.generators[self.IDX_FREQ_COLUMN].set_frequency(freq = self.TONES[symbol][self.IDX_FREQ_COLUMN])



class PWM(AD9833):
    FREQ_PWM = 100
    CARRIER_FREQ_RATIO = 1000
    DUTY_CYCLE = 0.2


    def __init__(self, spi, ss,
                 duty_cycle = DUTY_CYCLE,
                 freq = FREQ_PWM, carrier_freq_ratio = CARRIER_FREQ_RATIO):
        super().__init__(spi, ss)
        self._duty_cycle = duty_cycle
        self._freq = freq
        self._carrier_freq_ratio = carrier_freq_ratio
        self.initialize()


    def initialize(self):
        super().reset()
        self.running = False
        self.enable_output(False)
        self.freq = self.freq
        self.shape = 'half_square'


    def reset(self):
        self.initialize()


    @property
    def freq(self):
        return self._freq


    @freq.setter
    def freq(self, freq):
        self._freq = freq
        self._freq_carrier = self._freq * self._carrier_freq_ratio
        self.set_frequency(idx = 0, freq = self._freq_carrier)
        self.select_freq_source(0)
        self.duty_cycle = self.duty_cycle  # refresh parameters


    @property
    def duty_cycle(self):
        return self._duty_cycle


    @duty_cycle.setter
    def duty_cycle(self, duty_cycle):
        self._duty_cycle = duty_cycle
        self._period = 1 / self.freq
        self._period_on = self._period * duty_cycle
        self._period_off = self._period - self._period_on


    def run(self):
        self.running = True
        self.update()

        try:
            while self.running:
                self.enable_output(True)
                time.sleep(self._period_on)
                self.enable_output(False)
                time.sleep(self._period_off)
        except KeyboardInterrupt:
            print('User interrupts.')

        self.enable_output(False)
