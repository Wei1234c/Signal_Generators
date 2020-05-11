from signal_generators.ad98xx.ad9833 import *
from utilities.adapters import peripherals
from utilities.shift_register import ShiftRegister


AD9833.DEBUG_MODE_SHOW_BUS_DATA = False  # whether to show SPI written data.
AD9833.DEBUG_MODE_PRINT_REGISTER = False  # whether to print registers.

with_hardware_device = True

if with_hardware_device:
    _clk = peripherals.Pin.get_Ftdi_pin(pin_id = 4)
    _data = peripherals.Pin.get_Ftdi_pin(pin_id = 1)

    # _ss = peripherals.Pin.get_Ftdi_pin(pin_id = 3)
    _ss = peripherals.Pin.get_Ftdi_pin(pin_id = 0)

    _spi = ShiftRegister(stb_pin = _ss, clk_pin = _clk, data_pin = _data, polarity = 1)
else:
    _spi = _ss = None  # using None for testing without actual hardware device.

bus = peripherals.SPI(_spi, _ss, ss_polarity = 1)
ad = AD9833(bus)
ad.reset()

for f in dir(AD9833):
    if not f.startswith('_'):
        print('ad.{}()'.format(f))