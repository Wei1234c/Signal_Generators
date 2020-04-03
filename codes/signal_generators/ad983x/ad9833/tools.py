import math
import random
import time


try:
    from ...ad983x.ad9833 import ad9833
except:
    import ad9833



class ToolBox:
    SWEEP_TYPES = ('logarithm', 'linear')
    SWEEP_DIRECTIONS = ('up', 'down', 'round_trip')


    @classmethod
    def sweep(cls, generator, freq_start = 10, freq_end = int(1e6), n_freqs = 500,
              sweep_type = SWEEP_TYPES[0], direction = SWEEP_DIRECTIONS[0], n_cycles = None,
              slot_duration = 0.01, between_cycle_seconds = 1):

        if sweep_type == 'linear':
            start = freq_start
            step = (freq_end - freq_start) / n_freqs
            freqs = [(start + i * step) for i in range(n_freqs)]
        else:
            start = math.log10(freq_start)
            step = math.log10(freq_end / freq_start) / n_freqs
            freqs = [10 ** (start + i * step) for i in range(n_freqs)]

        if direction == 'down':
            freqs = freqs[::-1]

        (cycles_remains, need_to_count_down) = (1, False) if n_cycles is None else (n_cycles, True)

        if direction == 'round_trip':
            cycles_remains *= 2

        generator.reset()

        try:
            while cycles_remains:

                if need_to_count_down:
                    cycles_remains -= 1

                generator.enable_output(True)

                for freq in freqs:
                    print('Frequency: {:>10.2f}'.format(freq))
                    generator.set_frequency(freq = freq)
                    time.sleep(slot_duration)

                generator.enable_output(False)

                if direction == 'round_trip':
                    freqs = freqs[::-1]

                time.sleep(between_cycle_seconds)

        except KeyboardInterrupt:
            print('User interrupts.')

        generator.enable_output(False)

        return freqs


    @classmethod
    def toggle(cls, generator, fun = 'enable_output', params = ({'value': True}, {'value': False}), n_cycles = None,
               slot_duration = 0.2, between_cycle_seconds = 0.2):

        fun = getattr(generator, fun)
        (cycles_remains, need_to_count_down) = (1, False) if n_cycles is None else (n_cycles, True)
        generator.reset()
        count = 0

        time_start = time.time()

        try:
            while cycles_remains:

                if need_to_count_down:
                    cycles_remains -= 1

                count += 1

                for kwargs in params:
                    fun(**kwargs)
                    time.sleep(slot_duration)

                time.sleep(between_cycle_seconds)

        except KeyboardInterrupt:
            print('User interrupts.')

        time_end = time.time()

        duration_seconds = time_end - time_start
        cycle_time = duration_seconds / count

        generator.reset()

        return duration_seconds, count, cycle_time


    @classmethod
    def juggle(cls, generators, freq_start = int(1e2), freq_end = int(1e4), n_freqs = 100,
               freqs_type = SWEEP_TYPES[0], slot_duration = 0.2, between_cycle_seconds = 0.2, n_juggles = None):

        freqs = cls.sweep(generators[0],
                          freq_start = freq_start, freq_end = freq_end, n_freqs = n_freqs,
                          sweep_type = freqs_type, n_cycles = 0)
        phases = range(0, 360)
        shapes = list(ad9833.SHAPES_CONFIG.keys())

        (cycles_remains, need_to_count_down) = (1, False) if n_juggles is None else (n_juggles, True)


        def enable_output(value):
            for g in generators:
                g.enable_output(value)


        for g in generators:
            g.reset()

        enable_output(True)

        try:
            while cycles_remains:

                if need_to_count_down:
                    cycles_remains -= 1

                for g in generators:
                    freq = random.choice(freqs)
                    phase = random.choice(phases)
                    shape = random.choice(shapes)
                    g.apply_signal(freq = freq, phase = phase, shape = shape)
                    print('freq: {:>10.2f}\tphase: {:>6.2f}\tshape: {}'.format(freq, phase, shape))

                    time.sleep(slot_duration)

                time.sleep(between_cycle_seconds)

        except KeyboardInterrupt:
            print('User interrupts.')

        enable_output(False)
