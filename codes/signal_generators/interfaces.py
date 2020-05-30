import math


SPEED_OF_LIGHT_M_S = 299792458
PI2 = 2 * math.pi
DEGREES_IN_PI2 = 360
FREQ_DEFAULT = 440
PHASE_DEFAULT = 0
DEGREE_TO_RAD = PI2 / DEGREES_IN_PI2
RAD_TO_DEGREE = DEGREES_IN_PI2 / PI2
SHAPE_DEFAULT = 'sine'



class Device:
    DEBUG_MODE = False
    DEBUG_MODE_SHOW_BUS_DATA = DEBUG_MODE
    DEBUG_MODE_PRINT_REGISTER = DEBUG_MODE

    FREQ_REF = None
    N_OUTPUT_CLOCKS = None


    def __init__(self, freq = FREQ_DEFAULT, freq_correction = 0, phase = PHASE_DEFAULT, shape = SHAPE_DEFAULT,
                 registers_map = None, registers_values = None,
                 commands = None):
        self._frequency = freq
        self.freq_correction = freq_correction
        self.phase = phase
        self._shape = shape
        self._enabled = False
        self._action = ''

        self.map = registers_map
        if registers_values is not None:
            self.load_registers(registers_values)  # addressed registers values

        self.do(commands)


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


    def __del__(self):
        self.close()


    def do(self, commands):
        commands = commands or ()
        for (fun, args, kwargs) in commands:
            fun = getattr(self, fun)
            args = args or []
            kwargs = kwargs or {}
            fun(*args, **kwargs)


    @classmethod
    def do_on_devices(cls, devices, fun, *args, **kwargs):
        for d in devices:
            fun = getattr(d, fun)
            fun(*args, **kwargs)


    @property
    def is_virtual_device(self):
        raise NotImplementedError()


    @property
    def status(self):
        raise NotImplementedError()


    def load_registers(self, addressed_values):
        self._action = 'load_registers_values'
        self.map.load_values(addressed_values)


    @property
    def registers_values(self):
        return self.map.addressed_values


    @property
    def frequency(self):
        return self._frequency + self.freq_correction


    @frequency.setter
    def frequency(self, frequency):
        self._frequency = frequency


    @property
    def freq_resolution(self):
        raise NotImplementedError()


    @property
    def phase_resolution(self):
        raise NotImplementedError()


    def apply_signal(self, freq = None, freq_correction = None, phase = None, shape = None):
        raise NotImplementedError()


    def set_frequency(self, freq, idx = None, freq_correction = None):
        self._action = 'set_frequency {} idx {}'.format(freq, idx)
        raise NotImplementedError()


    def set_phase(self, phase, idx = None):
        self._action = 'set_phase {} idx {}'.format(phase, idx)
        raise NotImplementedError()


    def select_freq_source(self, idx):
        raise NotImplementedError()


    def select_phase_source(self, idx):
        raise NotImplementedError()


    @property
    def current_frequency(self):
        raise NotImplementedError()


    @property
    def current_phase(self):
        raise NotImplementedError()


    @property
    def shape(self):
        return self._shape


    @shape.setter
    def shape(self, shape):
        self._shape = shape


    @property
    def enabled(self):
        return self._enabled


    def enable(self, value = True):
        self._action = 'enable {}'.format(value)
        self._enabled = value
        self.enable_output(value)


    def toggle(self):
        self.enable(not self.enabled)


    def enable_output(self, value = True):
        self._action = 'enable_output: {}'.format(value)
        raise NotImplementedError()


    def enable_output_channel(self, idx, value = True):
        self._action = 'enable_output_channel: {} {}'.format(idx, value)
        raise NotImplementedError()


    def init(self):
        self._action = 'init'
        raise NotImplementedError()


    def start(self):
        self._action = 'start'
        self.enable(True)


    def pause(self):
        self._action = 'pause'
        self.enable(False)


    def resume(self):
        self._action = 'resume'
        self.enable(True)


    def stop(self):
        self._action = 'stop'
        self.pause()


    def close(self):
        self._action = 'close'
        self.stop()


    def update(self):
        self._action = 'update'
        self.write_all_registers(reset = False)


    def reset(self):
        self._action = 'reset'
        self.write_all_registers(reset = True)


    def print(self, as_hex = False):
        self._action = 'print'
        self.map.print(as_hex)


    def _show_bus_data(self, bytes_array, address = None, reading = False):
        if self.DEBUG_MODE_SHOW_BUS_DATA:
            print('\nAction: {}, {}: {}{}'.format(self._action,
                                                  'reading' if reading else 'writing',
                                                  hex(int.from_bytes(bytes_array, 'big')),
                                                  '' if address is None else ', Address: {}'.format(address)))


    def _print_register(self, register):
        if self.DEBUG_MODE_PRINT_REGISTER:
            register.print()


    # =================================================================

    def _write_register(self, register, reset = False):
        if reset:
            register.reset()
        self._show_bus_data(register.bytes, address = register.address)
        self._print_register(register)


    def _load_n_write_register(self, register, value):
        register.load_value(value)
        self._write_register(register)
        return register


    def _write_register_by_name(self, register_name, value):
        reg = self.map.registers[register_name]
        return self._load_n_write_register(reg, value)


    def _write_register_by_address(self, register_address, value):
        reg = self.map.registers_by_address[register_address]
        return self._load_n_write_register(reg, value)


    def _write_element_by_name(self, element_name, value):
        d = self.map.elements[element_name]
        reg, element = d['register'], d['element']
        element.value = value
        self._write_register(reg)
        return reg


    def write_all_registers(self, reset = False):
        for reg in self.map._registers:
            self._write_register(reg, reset = reset)


    def _read_register(self, register):
        raise NotImplementedError()


    def _read_n_load_register(self, register):
        register.load_value(self._read_register(register))
        return register


    def _read_register_by_name(self, register_name):
        reg = self.map.registers[register_name]
        return self._read_n_load_register(reg)


    def _read_register_by_address(self, register_address):
        reg = self.map.registers_by_address[register_address]
        return self._read_n_load_register(reg)


    def read_all_registers(self):
        for reg in self.map._registers:
            self._read_n_load_register(reg)
        return self.map.address_name_values


    def _read_element_by_name(self, element_name):
        reg = self.map.elements[element_name]['register']
        self._read_n_load_register(reg)
        return reg.elements[element_name]
