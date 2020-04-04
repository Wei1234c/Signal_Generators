# datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/ad983x.pdf


try:
    from ..ad983x.ad983x import *
except:
    from ad983x import *



class AD9833(AD983x):
    REGISTERS_COUNT = 2
    DEBUG_MODE = False
