class Device:

    def __init__(self, freq = 440, freq_correction = 0, phase = 0, shape = 'sine', commands = None):
        self._frequency = freq
        self.freq_correction = freq_correction
        self.phase = phase
        self._shape = shape
        self._enabled = False
        self.do(commands)


    def __enter__(self):
        pass


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


    @property
    def freq_resolution(self):
        raise NotImplementedError()


    @property
    def frequency(self):
        return self._frequency + self.freq_correction


    @frequency.setter
    def frequency(self, frequency):
        self._frequency = frequency


    def set_frequency(self, freq, freq_correction = None):
        raise NotImplementedError()


    def select_freq_source(self, idx):
        raise NotImplementedError()


    @property
    def current_frequency(self):
        raise NotImplementedError()


    def set_phase(self, phase):
        raise NotImplementedError()


    def select_phase_source(self, idx):
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


    def apply_signal(self, freq = None, freq_correction = None, phase = None, shape = None):
        raise NotImplementedError()


    @property
    def enabled(self):
        return self._enabled


    @enabled.setter
    def enabled(self, value):
        self._enabled = value


    def enable(self, value):
        raise NotImplementedError()


    def init(self):
        raise NotImplementedError()


    def reset(self):
        raise NotImplementedError()


    def start(self):
        raise NotImplementedError()


    def pause(self):
        raise NotImplementedError()


    def resume(self):
        raise NotImplementedError()


    def stop(self):
        raise NotImplementedError()


    def close(self):
        raise NotImplementedError()


    def update(self):
        raise NotImplementedError()


    def dump(self):
        raise NotImplementedError()
