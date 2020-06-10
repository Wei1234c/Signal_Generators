from signal_generators.ad98xx.ad9833 import *
from signal_generators.ad98xx.ad9834 import *
from signal_generators.ad98xx.ad9850 import *
from utilities.adapters import peripherals
from utilities.shift_register import ShiftRegister


cls = AD9833
cls = AD9834
# cls = AD9850

cls.DEBUG_MODE_SHOW_BUS_DATA = False  # whether to show SPI written data.
cls.DEBUG_MODE_PRINT_REGISTER = False  # whether to print registers.

with_hardware_device = True

if with_hardware_device:
    _clk = peripherals.Pin.get_Ftdi_pin(pin_id = 4)
    _data = peripherals.Pin.get_Ftdi_pin(pin_id = 1)
    _ss = peripherals.Pin.get_Ftdi_pin(pin_id = 3)
    #     _ss = peripherals.Pin.get_Ftdi_pin(pin_id = 0)
    # _reset = peripherals.Pin.get_Ftdi_pin(pin_id = 2)

    lsbfirst = False

    if cls in (AD9850,):
        _reset = peripherals.Pin.get_Ftdi_pin(pin_id = 2)
        lsbfirst = True

    _spi = ShiftRegister(stb_pin = _ss, clk_pin = _clk, data_pin = _data, lsbfirst = lsbfirst, polarity = 1)
else:
    _spi = _ss = _reset = None  # using None for testing without actual hardware device.

bus = peripherals.SPI(_spi, _ss)

ad = cls(bus = bus)
# ad = AD9850(bus = bus, pin_reset = _reset)
ad.reset()

ad.set_frequency(10.2e6)
ad.set_frequency(37.5e6)

for f in dir(cls):
    if not f.startswith('_'):
        print('ad.{}()'.format(f))
