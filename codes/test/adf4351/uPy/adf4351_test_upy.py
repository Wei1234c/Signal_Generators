try:
    from utilities.adapters import peripherals
    from signal_generators.adf435x import ADF4351
except:
    import gc


    gc.collect()
    # print(gc.mem_free())
    from adf4351 import ADF4351


    gc.collect()
    # print(gc.mem_free())

    import peripherals

with_hardware_device = True

if with_hardware_device:
    _spi = peripherals.SPI.get_uPy_spi(polarity = 0)
    _ss = peripherals.Pin.get_uPy_pin(15, output = True)
else:
    _spi = _ss = None  # using None for testing without actual hardware device.

bus = peripherals.SPI(_spi, _ss)
adf = ADF4351(bus)

# adf.set_frequency(35e6)
adf.set_frequency(1.5002e9, channel_resolution = 100e3, rf_divider_as = None)

print(adf.current_dividers)
print(adf.registers_values)
