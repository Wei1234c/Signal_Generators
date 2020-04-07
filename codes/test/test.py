from signal_generators.si535x.si535x import _get_registers_map
from signal_generators.si535x.si535x import *


regs_map = _get_registers_map()
reg = regs_map._registers[0]
e = reg._elements[0]

# regs_map.print()

er = regs_map.elements['CLK3_DIS_STATE']
print(er['element'].dumps())
print(er['register'].dumps())
# print(regs_map.dumps())
# print(len(regs_map._registers))

# ds = regs_map.dumps()
# print(ds)
# rm = regs_map.loads(ds)
# print(rm.dumps())
#
#
#
# # register
# ds = reg.dumps()
# print(ds)
# rr = reg.loads(ds)
# print(rr.dumps())
#
#
# # Element
# ds = e.dumps()
# print(ds )
# er = Element.loads(ds)
# print(er.dumps() )
