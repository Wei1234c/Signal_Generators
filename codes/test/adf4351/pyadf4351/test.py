from jhol import *


ref_freq, ref_doubler, r_counter, ref_div2, INT, MOD, \
FRAC, output_divider, band_select_clock_divider = calculate_regs(freq = 1500.0)

regs = make_regs(INT = INT, MOD = MOD, FRAC = FRAC,
                 output_divider = output_divider,
                 band_select_clock_divider = band_select_clock_divider)
print(regs)
