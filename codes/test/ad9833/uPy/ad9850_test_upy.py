import ad9850
import peripherals
from shift_register import ShiftRegister


_ss = peripherals.Pin.get_uPy_pin(15, output = True)
_clk = peripherals.Pin.get_uPy_pin(14, output = True)
_data = peripherals.Pin.get_uPy_pin(13, output = True)
_spi = ShiftRegister(stb_pin = _ss, clk_pin = _clk, data_pin = _data, lsbfirst = True, polarity = 1)
bus = peripherals.SPI(_spi, _ss)

_reset = peripherals.Pin.get_uPy_pin(4, output = True)
ad = ad9850.AD9850(bus = bus, pin_reset = _reset)
ad.reset()

ad.set_frequency(10.2e6)
