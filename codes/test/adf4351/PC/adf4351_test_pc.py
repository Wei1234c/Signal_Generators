from signal_generators.adf435x import ADF4351
from utilities.adapters import peripherals
from utilities.shift_register import ShiftRegister


peripherals.SPI.DEBUG_MODE = False  # whether to show SPI written data.
ADF4351.DEBUG_MODE = False  # whether to print registers.

with_hardware_device = False

if with_hardware_device:
    _clk = peripherals.Pin.get_Ftdi_pin(pin_id = 4)
    _data = peripherals.Pin.get_Ftdi_pin(pin_id = 1)
    _ss = peripherals.Pin.get_Ftdi_pin(pin_id = 3)
    # _ss2 = peripherals.Pin.get_Ftdi_pin(pin_id = 0)

    _spi = ShiftRegister(stb_pin = _ss, clk_pin = _clk, data_pin = _data, polarity = 1)
else:
    _spi = _ss = None  # using None for testing without actual hardware device.

adf = ADF4351(_spi, _ss)  # , freq_mclk = 13e6)


# adf.set_frequency(35e6)
adf.set_frequency(4.4e9, channel_resolution = 100e3, rf_divider_as = None)
print(adf.freq_resolution)

df_dividers, df_controls = adf.current_configuration
print(df_dividers)
