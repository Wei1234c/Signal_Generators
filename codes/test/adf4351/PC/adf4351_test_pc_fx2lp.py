from signal_generators.adf435x import ADF4351
from signal_generators.adf435x.fx2 import AnalogDeviceFX2LP


ADF4351.DEBUG_MODE_SHOW_BUS_DATA = False  # whether to show SPI written data.
ADF4351.DEBUG_MODE_PRINT_REGISTER = False  # whether to print registers.

bus = AnalogDeviceFX2LP()
adf = ADF4351(bus)

# adf.set_frequency(35e6)
# adf.set_frequency(4.4e9, channel_resolution = 100e3, rf_divider_as = None)
# adf.set_frequency(1.6002e9, channel_resolution = 100e3, rf_divider_as = None)
# adf.set_frequency(50.4e6, channel_resolution = 100e3, rf_divider_as = None)
adf.set_frequency(1.5002e9, channel_resolution = 100e3)

print(adf.current_dividers)
print(adf.registers_values)

df_dividers, df_controls = adf.current_configuration
print(df_dividers)
