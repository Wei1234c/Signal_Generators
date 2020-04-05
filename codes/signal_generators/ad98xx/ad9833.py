# datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/ad983x.pdf


try:
    from ..ad98xx.ad98xx import *
except:
    from ad983x import *



class AD9833(AD98xx):
    REGISTERS_COUNT = 2
    DEBUG_MODE = False
