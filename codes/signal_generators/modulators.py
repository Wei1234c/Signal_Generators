# https://en.wikipedia.org/wiki/Quadrature_amplitude_modulation

import time


DEFAULT_CARRIER_FREQ = int(1e5)



class Modulator:
    ON = 1
    OFF = 0
    SYMBOLS = (ON, OFF)


    def __init__(self, device, freq = DEFAULT_CARRIER_FREQ, time_ratio = 1):
        self._device = device
        self.freq = freq
        self.time_ratio = time_ratio
        self.initialize()


    def initialize(self):
        self._device.reset()
        self.enable_output(False)
        self._device.set_frequency(freq = self.freq)
        self._symbol = self.OFF


    def reset(self):
        self.initialize()


    def enable_output(self, value = True):
        self._device.enable_output(value)


    def update(self):
        self._device.update()


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
        self.reset()
        self.enable_output(True)

        try:
            for (symbol, duration) in sequence:
                self.symbol = symbol
                time.sleep(duration * self.time_ratio)
        except KeyboardInterrupt:
            print('User interrupts.')

        self.enable_output(False)



class PM(Modulator):
    ON = 1
    OFF = -1


    def __init__(self, device, freq = DEFAULT_CARRIER_FREQ):
        super().__init__(device, freq = freq)


    @Modulator.symbol.setter
    def symbol(self, symbol):
        assert self.OFF <= symbol <= self.ON, 'Must {} <= symbol <= {}.'.format(self.OFF, self.ON)
        self._symbol = symbol
        self._process_symbol(symbol)


    def _process_symbol(self, symbol):
        self._device.set_phase(phase = 90 * symbol)



class FM(PM):
    BANDWIDTH = int(1e4)


    def __init__(self, device, freq = DEFAULT_CARRIER_FREQ, bandwidth = BANDWIDTH):
        self.bandwidth = bandwidth
        super().__init__(device, freq = freq)
        self.initialize()


    def _process_symbol(self, symbol):
        self._device.set_frequency(freq = self.freq + self.bandwidth * symbol)



class OOK(Modulator):
    FREQ_CARRIER = int(4e4)


    def __init__(self, device, freq = FREQ_CARRIER, time_ratio = 500 / 517):
        super().__init__(device, freq = freq, time_ratio = time_ratio)


    def initialize(self):
        super().initialize()
        self._device.shape = 'sine'


    def _process_symbol(self, symbol):
        self._device.enable_output(symbol == self.ON)



class BFSK(Modulator):
    FREQ_OFFSET = int(1e3)
    FREQ_ON = DEFAULT_CARRIER_FREQ + FREQ_OFFSET
    FREQ_OFF = DEFAULT_CARRIER_FREQ - FREQ_OFFSET


    def __init__(self, device, freq_on = FREQ_ON, freq_off = FREQ_OFF):
        self.freq_on = freq_on
        self.freq_off = freq_off
        super().__init__(device)


    def initialize(self):
        super().initialize()
        self._device.set_frequency(idx = self.ON, freq = self.freq_on)
        self._device.set_frequency(idx = self.OFF, freq = self.freq_off)


    def _process_symbol(self, symbol):
        self._device.select_freq_source(idx = symbol)



class BPSK(Modulator):
    PHASE_ON = 0
    PHASE_OFF = 180


    def __init__(self, device, freq = DEFAULT_CARRIER_FREQ, phase_on = PHASE_ON, phase_off = PHASE_OFF):
        self.phase_on = phase_on
        self.phase_off = phase_off
        super().__init__(device, freq = freq)


    def initialize(self):
        super().initialize()
        self._device.set_phase(idx = self.ON, phase = self.phase_on)
        self._device.set_phase(idx = self.OFF, phase = self.phase_off)


    def select_phase_source(self, idx):
        self._device.select_phase_source(idx)


    def _process_symbol(self, symbol):
        self._device.select_phase_source(idx = symbol)



class QPSK(Modulator):
    # PHASE_11 = 45
    # PHASE_01 = 135
    # PHASE_00 = 225
    # PHASE_10 = 315
    PHASES = {3: 45, 1: 135, 0: 225, 2: 315}
    SYMBOLS = list(PHASES.keys())
    ON = 3
    OFF = 0


    def __init__(self, device, freq = DEFAULT_CARRIER_FREQ):
        super().__init__(device, freq = freq)


    def _process_symbol(self, symbol):
        self._device.set_phase(phase = self.PHASES[symbol])



class MultipleChannels:
    ON = 1
    OFF = 0
    SYMBOLS = (ON, OFF)


    def __init__(self, devices):
        self._devices = devices
        self.initialize()


    def initialize(self):
        for d in self._devices:
            d.reset()
            d.enable_output(False)
            d._symbol = None


    def update(self):
        for d in self._devices:
            d.update()


    def enable_output(self, value = True):
        for d in self._devices:
            d.enable_output(value)


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
        self.reset()
        self.enable_output(True)

        try:
            for (symbol, duration) in sequence:
                self.symbol = symbol
                time.sleep(duration)
        except KeyboardInterrupt:
            print('User interrupts.')

        self.enable_output(False)



class IQ(MultipleChannels):
    PHASE_ON = 0
    PHASE_OFF = 180
    QUADRATURE = 90
    # PHASE_11 = 45
    # PHASE_01 = 135
    # PHASE_00 = 225
    # PHASE_10 = 315
    PHASES = {3: 45, 1: 135, 0: 225, 2: 315}
    SYMBOLS = list(PHASES.keys())
    ON = 3
    OFF = 0
    IDX_I = 0
    IDX_Q = 1


    def __init__(self, devices, freq = DEFAULT_CARRIER_FREQ, phase_on = PHASE_ON, phase_off = PHASE_OFF):
        self._devices = (BPSK(devices[0], freq = freq, phase_on = phase_on, phase_off = phase_off),
                         BPSK(devices[1], freq = freq,
                              phase_on = phase_on + self.QUADRATURE,
                              phase_off = phase_off + self.QUADRATURE))
        self.freq = freq
        self.phase_on = phase_on
        self.phase_off = phase_off
        self.initialize()


    def initialize(self):
        super().initialize()
        for d in self._devices:
            d.initialize()


    def _process_symbol(self, symbol):
        self._devices[self.IDX_I].select_phase_source(idx = (symbol >> 1) & 0x01)
        self._devices[self.IDX_Q].select_phase_source(idx = (symbol >> 0) & 0x01)



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


    def _process_symbol(self, symbol):
        self._devices[self.IDX_FREQ_ROW].set_frequency(freq = self.TONES[symbol][self.IDX_FREQ_ROW])
        self._devices[self.IDX_FREQ_COLUMN].set_frequency(freq = self.TONES[symbol][self.IDX_FREQ_COLUMN])



class PWM:
    FREQ_PWM = 100
    CARRIER_FREQ_RATIO = 1000
    DUTY_CYCLE = 0.2


    def __init__(self, device,
                 duty_cycle = DUTY_CYCLE,
                 freq = FREQ_PWM, carrier_freq_ratio = CARRIER_FREQ_RATIO):
        self._device = device
        self._duty_cycle = duty_cycle
        self._freq = freq
        self._carrier_freq_ratio = carrier_freq_ratio
        self.initialize()


    def initialize(self):
        self._device.reset()
        self.running = False
        self._device.enable_output(False)
        self.freq = self.freq
        self._device.shape = 'half_square'


    def reset(self):
        self.initialize()


    @property
    def freq(self):
        return self._freq


    @freq.setter
    def freq(self, freq):
        self._freq = freq
        self._freq_carrier = self._freq * self._carrier_freq_ratio
        self._device.set_frequency(self._freq_carrier)
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
        self.reset()
        self.running = True

        try:
            while self.running:
                self._device.enable_output(True)
                time.sleep(self._period_on)
                self._device.enable_output(False)
                time.sleep(self._period_off)
        except KeyboardInterrupt:
            print('User interrupts.')

        self._device.enable_output(False)
