import os
import sys


try:
    machine_name = os.uname().machine
except Exception:
    machine_name = os.name

IS_PC = machine_name.startswith('x86_64') or machine_name.startswith('nt')
IS_RPi = machine_name.startswith('armv')
IS_MICROPYTHON = (sys.implementation.name == 'micropython')

try:
    from bridges.ftdi.controllers.gpio import GpioController
    from bridges.ftdi.adapters.micropython.machine import Pin as ftdi_Pin
    from .shift_register import ShiftRegister


    GPIO_PORT = GpioController()
except Exception as e:
    if not isinstance(e, ImportError):
        print(e)

try:
    from .shift_register import ShiftRegister
except:
    from shift_register import ShiftRegister



class Mock:
    pass



class Pin:

    @classmethod
    def get_uPy_pin(cls, pin_id, output = True):
        import machine

        pin = machine.Pin(pin_id, machine.Pin.OUT if output else machine.Pin.IN)
        new_pin = Mock()

        if output:
            new_pin.low = lambda: pin.value(0)
            new_pin.high = lambda: pin.value(1)
        else:
            new_pin.value = pin.value

        return new_pin


    @classmethod
    def get_RPi_pin(cls, pin_id, output = True):
        import RPi.GPIO as GPIO

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(pin_id, GPIO.OUT if output else GPIO.IN)
        new_pin = Mock()

        if output:
            new_pin.low = lambda: GPIO.output(pin_id, GPIO.LOW)
            new_pin.high = lambda: GPIO.output(pin_id, GPIO.HIGH)
        else:
            new_pin.value = lambda: GPIO.input(pin_id)

        return new_pin


    @classmethod
    def get_Ftdi_pin(cls, pin_id, output = True):
        return ftdi_Pin(pin_id, mode = ftdi_Pin.OUT if output else ftdi_Pin.IN, gpio_port = GPIO_PORT)



class SPI:
    SPI_MSB = 0
    SPI_LSB = 1

    DEBUG_MODE = False


    def __init__(self, spi, ss):
        self._spi = spi
        self._ss = ss


    def write(self, bytes_array):

        if self.DEBUG_MODE:
            print('Sending: {}'.format(hex(int.from_bytes(bytes_array, 'big'))))

        if self._spi is not None:
            self._ss.low()

            if IS_RPi:
                self._spi.writebytes(bytes_array)
            elif IS_MICROPYTHON:
                self._spi.write(bytes_array)
            elif IS_PC:
                self._spi.write(bytes_array)

            self._ss.high()


    @classmethod
    def get_uPy_spi(cls, id = -1, baudrate = 10000000, polarity = 0, phase = 0, bits = 8, firstbit = SPI_MSB,
                    pin_id_sck = 14, pin_id_mosi = 13, pin_id_miso = 12):
        import machine

        spi = machine.SPI(id, baudrate = baudrate, polarity = polarity, phase = phase, bits = bits, firstbit = firstbit,
                          sck = machine.Pin(pin_id_sck, machine.Pin.OUT,
                                            machine.Pin.PULL_UP if polarity else machine.Pin.PULL_DOWN),
                          mosi = machine.Pin(pin_id_mosi, machine.Pin.OUT),  # , machine.Pin.PULL_UP),
                          miso = machine.Pin(pin_id_miso, machine.Pin.IN))  # , machine.Pin.PULL_UP))
        spi.init()

        return spi


    @classmethod
    def get_RPi_spi(cls, mode = 0b00):
        import spidev

        spi = None

        try:
            spi = spidev.SpiDev()
            bus = 0
            device = 0
            spi.open(bus, device)
            spi.max_speed_hz = 10000000
            spi.mode = mode
            spi.lsbfirst = False

        except Exception as e:
            print(e)

        return spi


    @classmethod
    def get_Ftdi_spi(cls, stb_pin, clk_pin, data_pin,
                     bits = ShiftRegister.BITS_IN_BYTE, lsbfirst = False,
                     polarity = ShiftRegister.POLARITY_DEFAULT, phase = ShiftRegister.PHASE_DEFAULT):

        return ShiftRegister(stb_pin = stb_pin, clk_pin = clk_pin, data_pin = data_pin, bits = bits,
                             lsbfirst = lsbfirst,
                             polarity = polarity, phase = phase)
