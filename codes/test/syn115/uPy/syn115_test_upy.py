try:
    import fx2lp
    from signal_generators.syn115 import SYN115


    pin_ask = fx2lp.GPIO().Pin(id = 1, mode = fx2lp.Pin.OUT, value = 1)

except:

    #  for ESP32 ===========================
    import peripherals
    from syn115 import SYN115


    with_hardware_device = True

    if with_hardware_device:
        pin_ask = peripherals.Pin.get_uPy_pin(15, output = True)
    else:
        pin_ask = None  # using None for testing without actual hardware device.

    #  for ESP32 ===========================

syn = SYN115(pin_ask = pin_ask)

syn.enable(True)
syn.enable(False)
syn.on()
syn.off()

print(syn.frequency)
