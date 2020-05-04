try:
    from signal_generators.adf435x.adf4351 import ADF4351
    from utilities.adapters import peripherals
except:
    from adf4351 import ADF4351
    import gc


    gc.collect()
    print(gc.mem_free())

    import peripherals

with_hardware_device = True

if with_hardware_device:
    _spi = peripherals.SPI.get_uPy_spi(polarity = 1)
    _ss = peripherals.Pin.get_uPy_pin(15, output = True)
else:
    _spi = _ss = None  # using None for testing without actual hardware device.

adf = ADF4351(_spi, _ss)  # , freq_mclk = 13e6)

# adf.set_frequency(35e6)
adf.set_frequency(4.4e9, channel_resolution = 100e3, rf_divider_as = None)
print(adf.freq_resolution)

print(adf.status)
