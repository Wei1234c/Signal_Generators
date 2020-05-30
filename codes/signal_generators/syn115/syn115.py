# datasheet: https://datasheet.lcsc.com/szlcsc/1912111437_Synoxo-F115_C105184.pdf


try:
    from ..interfaces import Device
except:
    from interfaces import Device



class SYN115(Device):
    FREQ_MIN = int(300e6)
    FREQ_MAX = int(450e6)
    FREQ_REF = 9843750  # for 315MHz
    DIVIDER = 32


    def __init__(self, pin_ask, freq = FREQ_REF * DIVIDER):
        assert self.FREQ_MIN <= freq <= self.FREQ_MAX

        Device.__init__(self, freq = freq)
        self._pin_ask = pin_ask
        self.init()


    def init(self):
        self.off()


    def reset(self):
        self.init()


    def on(self):
        self.enable(True)


    def off(self):
        self.enable(False)


    def enable_output(self, value = True):
        self._enabled = value
        if self._pin_ask is not None:
            _ = self._pin_ask.high() if value else self._pin_ask.low()


    def set_frequency(self, freq):
        pass
