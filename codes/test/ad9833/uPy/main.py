try:
    from signal_generators import adapters
    from signal_generators import modulators
    from signal_generators import tools
    from signal_generators.ad98xx import ad9833
except:
    import adapters
    import modulators
    import tools
    import ad9833

    import machine
    import gc

gc.collect()

adapters.SPI.DEBUG_MODE = False

## Generators
_spi = adapters.SPI.get_uPy_spi(polarity = 1)
_ss1 = adapters.Pin.get_uPy_pin(15, output = True)
_ss2 = adapters.Pin.get_uPy_pin(4, output = True)

ad1 = ad9833.AD9833(_spi, _ss1)
ad2 = ad9833.AD9833(_spi, _ss2)

# # Not used.
# _ss3 = adapters.Pin.get_uPy_pin(16, output = True)
# ad3 = ad9833.AD9833(_spi, _ss3)

## Modulators
# bfsk = modulators.BFSK(_spi, _ss1)
# bpsk = modulators.BPSK(_spi, _ss1)
# dtmf = modulators.DTMF(_spi, _ss1, _ss2)
# fm = modulators.FM(_spi, _ss1)
# iq = modulators.IQ(_spi, _ss1, _ss2)
# ook = modulators.OOK(_spi, _ss1)
# pm = modulators.PM(_spi, _ss1)
# pwm = modulators.PWM(_spi, _ss1)
# qpsk = modulators.QPSK(_spi, _ss1)


ad1.reset()
ad2.reset()

tb = tools.ToolBox()

# tb.sweep(ad1, freq_start = 10, freq_end = int(1e6), n_freqs = 500,
#          sweep_type = 'logarithm', direction = 'up', n_cycles = 3,
#          slot_duration = 0.01, between_cycle_seconds = 1)

# duration_seconds, count, cycle_time = tb.toggle(ad1,
#                                                 fun = 'enable_output', params = ({'value': True}, {'value': False}),
#                                                 n_cycles = 10, slot_duration = 0.2, between_cycle_seconds = 0.2)
# print('duration_seconds, count, cycle_time', duration_seconds, count, cycle_time)

# tb.juggle((ad1, ad2),
#           freq_start = int(1e2), freq_end = int(1e4), n_freqs = 100, freqs_type = 'logarithm',
#           slot_duration = 0.2, between_cycle_seconds = 0.2,
#           n_juggles = 10)

## Testing data
# # symbols = np.random.randint(2, size=100)
# # duration = 0.1
# # sequence = [(symbol, duration) for symbol in symbols]
# # print('digital_sequence = {}'.format(sequence))
# digital_sequence = [(0, 0.1), (0, 0.1), (0, 0.1), (1, 0.1), (1, 0.1), (0, 0.1), (0, 0.1), (1, 0.1), (0, 0.1), (1, 0.1),
#                     (0, 0.1), (1, 0.1), (0, 0.1), (1, 0.1), (1, 0.1), (0, 0.1), (0, 0.1), (0, 0.1), (1, 0.1), (0, 0.1),
#                     (0, 0.1), (1, 0.1), (0, 0.1), (1, 0.1), (1, 0.1), (1, 0.1), (1, 0.1), (0, 0.1), (1, 0.1), (0, 0.1),
#                     (1, 0.1), (0, 0.1), (1, 0.1), (1, 0.1), (0, 0.1), (1, 0.1), (0, 0.1), (1, 0.1), (1, 0.1), (1, 0.1),
#                     (0, 0.1), (1, 0.1), (0, 0.1), (1, 0.1), (0, 0.1), (0, 0.1), (0, 0.1), (1, 0.1), (0, 0.1), (0, 0.1),
#                     (1, 0.1), (0, 0.1), (0, 0.1), (0, 0.1), (0, 0.1), (0, 0.1), (0, 0.1), (0, 0.1), (0, 0.1), (1, 0.1),
#                     (1, 0.1), (1, 0.1), (0, 0.1), (0, 0.1), (0, 0.1), (0, 0.1), (1, 0.1), (1, 0.1), (0, 0.1), (0, 0.1),
#                     (1, 0.1), (0, 0.1), (0, 0.1), (0, 0.1), (1, 0.1), (0, 0.1), (1, 0.1), (1, 0.1), (1, 0.1), (0, 0.1),
#                     (0, 0.1), (1, 0.1), (0, 0.1), (0, 0.1), (0, 0.1), (0, 0.1), (0, 0.1), (0, 0.1), (0, 0.1), (1, 0.1),
#                     (1, 0.1), (0, 0.1), (1, 0.1), (1, 0.1), (1, 0.1), (1, 0.1), (1, 0.1), (0, 0.1), (1, 0.1), (1, 0.1)]

# # symbols = np.random.uniform(-1, 1, size = 100).round(5)
# # duration = 0.1
# # sequence = [(symbol, duration) for symbol in symbols]
# # print('analog_sequence = {}'.format(sequence))
# analog_sequence = [(0.78327, 0.1), (0.30279, 0.1), (-0.88788, 0.1), (0.78136, 0.1), (0.18037, 0.1), (0.57774, 0.1),
#                    (0.27251, 0.1), (-0.31195, 0.1), (-0.3271, 0.1), (-0.44761, 0.1), (0.06899, 0.1), (0.99835, 0.1),
#                    (0.32058, 0.1), (-0.83949, 0.1), (-0.02932, 0.1), (0.39843, 0.1), (-0.05903, 0.1), (0.44105, 0.1),
#                    (-0.89004, 0.1), (-0.48743, 0.1), (0.82121, 0.1), (0.56143, 0.1), (0.23903, 0.1), (0.64168, 0.1),
#                    (-0.54888, 0.1), (0.15721, 0.1), (0.6321, 0.1), (-0.07464, 0.1), (0.26714, 0.1), (-0.28809, 0.1),
#                    (0.81656, 0.1), (0.2058, 0.1), (-0.20701, 0.1), (-0.26074, 0.1), (-0.14932, 0.1), (-0.29503, 0.1),
#                    (0.60224, 0.1), (0.94686, 0.1), (-0.82493, 0.1), (-0.59258, 0.1), (0.03863, 0.1), (-0.58419, 0.1),
#                    (-0.94228, 0.1), (-0.97345, 0.1), (0.90726, 0.1), (0.29426, 0.1), (-0.02133, 0.1), (-0.13033, 0.1),
#                    (-0.80385, 0.1), (0.07959, 0.1), (0.14669, 0.1), (0.53537, 0.1), (-0.636, 0.1), (-0.17577, 0.1),
#                    (-0.35541, 0.1), (0.06053, 0.1), (-0.23482, 0.1), (0.50227, 0.1), (-0.98655, 0.1), (-0.39213, 0.1),
#                    (0.89561, 0.1), (-0.60339, 0.1), (0.6801, 0.1), (0.74134, 0.1), (0.00984, 0.1), (-0.58895, 0.1),
#                    (0.85744, 0.1), (0.92864, 0.1), (0.97276, 0.1), (-0.84921, 0.1), (-0.06907, 0.1), (-0.94814, 0.1),
#                    (-0.87123, 0.1), (-0.42633, 0.1), (-0.52706, 0.1), (0.94893, 0.1), (0.7214, 0.1), (0.57636, 0.1),
#                    (-0.38682, 0.1), (-0.32602, 0.1), (-0.59388, 0.1), (0.62751, 0.1), (0.36523, 0.1), (-0.22088, 0.1),
#                    (0.70272, 0.1), (0.89303, 0.1), (-0.97301, 0.1), (-0.25038, 0.1), (0.68807, 0.1), (0.61047, 0.1),
#                    (-0.13399, 0.1), (-0.8315, 0.1), (-0.16341, 0.1), (-0.59039, 0.1), (0.92454, 0.1), (0.57682, 0.1),
#                    (-0.62021, 0.1), (-0.12206, 0.1), (-0.99582, 0.1), (0.45998, 0.1)]
#
# # symbols = random.choice(['1', '2', '3', 'A', '4', '5', '6', 'B', '7', '8', '9', 'C', '*', '0', '#', 'D'], size = 100)
# # duration = 0.1
# # sequence = [(symbol, duration) for symbol in symbols]
# # print('dtmf_sequence = {}'.format(sequence))
# dtmf_sequence = [('4', 0.1), ('D', 0.1), ('A', 0.1), ('#', 0.1), ('B', 0.1), ('9', 0.1), ('7', 0.1), ('0', 0.1),
#                  ('1', 0.1), ('0', 0.1), ('D', 0.1), ('3', 0.1), ('2', 0.1), ('4', 0.1), ('1', 0.1), ('8', 0.1),
#                  ('B', 0.1), ('2', 0.1), ('9', 0.1), ('0', 0.1), ('1', 0.1), ('1', 0.1), ('#', 0.1), ('9', 0.1),
#                  ('1', 0.1), ('A', 0.1), ('3', 0.1), ('#', 0.1), ('5', 0.1), ('A', 0.1), ('9', 0.1), ('C', 0.1),
#                  ('4', 0.1), ('7', 0.1), ('B', 0.1), ('6', 0.1), ('4', 0.1), ('A', 0.1), ('0', 0.1), ('7', 0.1),
#                  ('7', 0.1), ('2', 0.1), ('D', 0.1), ('5', 0.1), ('5', 0.1), ('B', 0.1), ('8', 0.1), ('#', 0.1),
#                  ('D', 0.1), ('6', 0.1), ('*', 0.1), ('2', 0.1), ('0', 0.1), ('D', 0.1), ('1', 0.1), ('C', 0.1),
#                  ('A', 0.1), ('2', 0.1), ('C', 0.1), ('5', 0.1), ('8', 0.1), ('D', 0.1), ('C', 0.1), ('#', 0.1),
#                  ('1', 0.1), ('4', 0.1), ('*', 0.1), ('9', 0.1), ('7', 0.1), ('8', 0.1), ('A', 0.1), ('8', 0.1),
#                  ('C', 0.1), ('9', 0.1), ('4', 0.1), ('6', 0.1), ('B', 0.1), ('D', 0.1), ('7', 0.1), ('6', 0.1),
#                  ('3', 0.1), ('A', 0.1), ('3', 0.1), ('5', 0.1), ('3', 0.1), ('9', 0.1), ('A', 0.1), ('B', 0.1),
#                  ('#', 0.1), ('#', 0.1), ('B', 0.1), ('5', 0.1), ('#', 0.1), ('#', 0.1), ('6', 0.1), ('6', 0.1),
#                  ('3', 0.1), ('C', 0.1), ('#', 0.1), ('A', 0.1)]
#
# # symbols = random.choice([0, 1, 2, 3], size = 100)
# # duration = 0.1
# # sequence = [(symbol, duration) for symbol in symbols]
# # print('quadrature_sequence = {}'.format(sequence))
# quadrature_sequence = [(1, 0.1), (1, 0.1), (3, 0.1), (3, 0.1), (2, 0.1), (3, 0.1), (0, 0.1), (3, 0.1), (2, 0.1),
#                        (0, 0.1), (3, 0.1), (0, 0.1), (1, 0.1), (3, 0.1), (0, 0.1), (1, 0.1), (2, 0.1), (0, 0.1),
#                        (1, 0.1), (0, 0.1), (1, 0.1), (1, 0.1), (1, 0.1), (2, 0.1), (3, 0.1), (2, 0.1), (2, 0.1),
#                        (1, 0.1), (2, 0.1), (1, 0.1), (1, 0.1), (3, 0.1), (2, 0.1), (3, 0.1), (3, 0.1), (1, 0.1),
#                        (3, 0.1), (3, 0.1), (2, 0.1), (2, 0.1), (2, 0.1), (2, 0.1), (3, 0.1), (0, 0.1), (3, 0.1),
#                        (2, 0.1), (2, 0.1), (1, 0.1), (3, 0.1), (0, 0.1), (2, 0.1), (1, 0.1), (2, 0.1), (1, 0.1),
#                        (3, 0.1), (0, 0.1), (3, 0.1), (2, 0.1), (3, 0.1), (3, 0.1), (3, 0.1), (2, 0.1), (3, 0.1),
#                        (0, 0.1), (2, 0.1), (1, 0.1), (0, 0.1), (2, 0.1), (2, 0.1), (2, 0.1), (2, 0.1), (3, 0.1),
#                        (3, 0.1), (2, 0.1), (1, 0.1), (0, 0.1), (2, 0.1), (3, 0.1), (2, 0.1), (3, 0.1), (0, 0.1),
#                        (3, 0.1), (0, 0.1), (1, 0.1), (2, 0.1), (0, 0.1), (3, 0.1), (3, 0.1), (2, 0.1), (0, 0.1),
#                        (3, 0.1), (1, 0.1), (3, 0.1), (0, 0.1), (0, 0.1), (3, 0.1), (1, 0.1), (2, 0.1), (0, 0.1),
#                        (0, 0.1)]

gc.collect()
