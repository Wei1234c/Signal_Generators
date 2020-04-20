try:
    from ..adf435x.adf435x import *
except Exception as e:
    from adf435x import *



class ADF4351(ADF435x):
    pass