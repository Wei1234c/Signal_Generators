from signal_generators.adf435x import ADF4351
from utilities.adapters import peripherals
from utilities.shift_register import ShiftRegister


ADF4351.DEBUG_MODE_SHOW_BUS_DATA = False  # whether to show SPI written data.
ADF4351.DEBUG_MODE_PRINT_REGISTER = False  # whether to print registers.

with_hardware_device = True

if with_hardware_device:
    # _clk = peripherals.Pin.get_Ftdi_pin(pin_id = 4)
    # _data = peripherals.Pin.get_Ftdi_pin(pin_id = 1)
    # _ss = peripherals.Pin.get_Ftdi_pin(pin_id = 3)
    # # _ss2 = peripherals.Pin.get_Ftdi_pin(pin_id = 0)
    #
    # _spi = ShiftRegister(stb_pin = _ss, clk_pin = _clk, data_pin = _data, polarity = 0)

    from array import array


    _clk = peripherals.Pin.get_Ftdi_pin(pin_id = 4)
    _data = peripherals.Pin.get_Ftdi_pin(pin_id = 1)
    _ss = peripherals.Pin.get_Ftdi_pin(pin_id = 3)
    _spi = ShiftRegister(stb_pin = _ss, clk_pin = _clk, data_pin = _data, polarity = 0)#, phase = 0)

    # spi = peripherals.SPI(_spi, _ss, ss_polarity = 1)
else:
    _spi = _ss = None  # using None for testing without actual hardware device.

adf = ADF4351(_spi, _ss)  # , freq_mclk = 13e6)

# adf.set_frequency(35e6)
# adf.set_frequency(4.4e9, channel_resolution = 100e3, rf_divider_as = None)
# adf.set_frequency(1.6002e9, channel_resolution = 100e3, rf_divider_as = None)
# adf.set_frequency(50.4e6, channel_resolution = 100e3, rf_divider_as = None)
adf.set_frequency(int(1.5e9), channel_resolution=100e3)#, rf_divider_as=2)

print(adf.current_dividers)
print(adf.registers_values)

df_dividers, df_controls = adf.current_configuration
print(df_dividers)
