import fx2lp
from signal_generators.syn115 import SYN115


pin_ask = fx2lp.GPIO().Pin(id = 1, mode = fx2lp.Pin.OUT, value = 1)

syn = SYN115(pin_ask = pin_ask)

syn.enable(True)
syn.enable(False)
syn.on()
syn.off()
syn.toggle()
syn.toggle()
print(syn.frequency)
