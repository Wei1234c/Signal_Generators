# https://ez.analog.com/rf/f/discussions/75850/adf4350-and-adf4351-software-and-usb-microcontroller-firmware-source-codes#52311

import usb
import usb.backend.libusb0 as libusb0
import usb.backend.libusb1 as libusb1

from utilities.adapters.peripherals import Bus



class AnalogDeviceFX2LP(Bus):

    def __init__(self, use_libusb0 = True):

        self.dev = usb.core.find(idVendor = 0X0456, idProduct = 0XB40D,
                                 backend = libusb0.get_backend() if use_libusb0 else libusb1.get_backend())
        if self.dev is not None:
            self.dev.set_configuration()

        super().__init__(self.dev)


    def init(self):
        pass


    def write(self, bytes_array):
        if not self.is_virtual_device:
            bytes_array.insert(0, 8 * len(bytes_array))
            return self.dev.ctrl_transfer(bmRequestType = 0x40, bRequest = 0xDD, wValue = 0, wIndex = 0,
                                          data_or_wLength = bytes_array[::-1])
