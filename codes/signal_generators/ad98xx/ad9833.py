# datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/ad9833.pdf


try:
    from ..ad98xx.ad98xx import *
except:
    from ad98xx import *



class AD9833(AD98xx):
    DEBUG_MODE = False
    REGISTERS_COUNT = 2
    FREQ_MCLK = int(25e6)