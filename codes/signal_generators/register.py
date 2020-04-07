import json
import math
from array import array



def _elements_by_attr(elements, attr):
    keyed_elements = {getattr(e, attr): e for e in elements}
    assert len(list(keyed_elements.keys())) == len(elements), '{} are not unique.'.format(attr)
    return keyed_elements



class RegistersMap:

    def __init__(self, name, description = None, registers = None):
        self.name = name
        self.description = description
        self.registers = registers


    @property
    def registers(self):
        return self._registers_dict


    @property
    def registers_by_address(self):
        return self._registers_by_address


    @property
    def elements(self):
        return self._elements


    @registers.setter
    def registers(self, registers):
        self._registers = registers or []
        self._registers_dict = _elements_by_attr(self._registers, 'name')
        self._registers_by_address = _elements_by_attr(self._registers, 'address')
        self._elements = {e.name: {'element': e, 'register': reg} for reg in self._registers for e in reg._elements}


    @property
    def values(self):
        return [reg.value for reg in self._registers]


    def load_from_registers(self, registers_value):
        assert len(registers_value) == len(self._registers), 'Sizes must match.'
        for reg, value in zip(self._registers, registers_value):
            reg.load_from_register(value)


    def reset(self):
        for register in self._registers:
            register.reset()


    def print(self, as_hex = False):
        for register in self._registers:
            register.print(as_hex = as_hex)


    def loads(self, json_string):
        rm_attrs = json.loads(json_string)

        reg_map = RegistersMap('')
        reg_map.name = rm_attrs['name']
        reg_map.description = rm_attrs['description']
        reg_map.registers = [Register.loads(json.dumps(reg_attrs)) for reg_attrs in rm_attrs['registers']]
        return reg_map


    def dumps(self):
        d = {'name'       : self.name,
             'description': self.description,
             'registers'  : [json.loads(r.dumps()) for r in self._registers]}

        return json.dumps(d, indent = 4)



class Register:

    def __init__(self, name, code_name = None, address = None, description = None, elements = None, default_value = 0):
        self.name = name
        self.code_name = code_name or name
        self.address = address
        self.description = description
        self.elements = elements
        self.default_value = default_value


    @property
    def elements(self):
        return self._elements_dict


    @elements.setter
    def elements(self, elements):
        self._elements = elements or []
        self._elements_dict = _elements_by_attr(self._elements, 'name')


    @property
    def n_bits(self):
        return sum([e.n_bits for e in self._elements])


    @property
    def n_bytes(self):
        return math.ceil(self.n_bits / 8)


    @property
    def value(self):
        return int(sum([e.shifted_value for e in self._elements]))


    @property
    def bytes(self):
        return array('B', self.value.to_bytes(self.n_bytes, 'big'))


    def load_from_register(self, register_value):
        for e in self._elements:
            e.load_from_register(register_value)


    def reset(self):
        self.load_from_register(self.default_value)


    def print(self, as_hex = False):
        len_name_field = max([len(e.name) for e in self._elements] + [0])
        print('\n{:<{}s}:  {}'.format('<< ' + self.name + ' >>', len_name_field + 7,
                                      (hex(self.value), bin(self.value))))
        for e in self._elements:
            print('{:<{}s}:  {}'.format('[ ' + e.name + ' ]', len_name_field + 5,
                                        (hex(e.value), bin(e.value)) if as_hex else e.value))
        return len_name_field


    @classmethod
    def loads(cls, json_string):
        reg_attrs = json.loads(json_string)

        reg = Register('')
        reg.name = reg_attrs['name']
        reg.code_name = reg_attrs['code_name']
        reg.address = reg_attrs['address']
        reg.description = reg_attrs['description']
        reg.default_value = reg_attrs['default_value']
        reg.elements = [Element(**element_attrs) for element_attrs in reg_attrs['elements']]
        return reg


    def dumps(self):
        d = {'name'         : self.name,
             'code_name'    : self.code_name,
             'address'      : self.address,
             'description'  : self.description,
             'default_value': self.default_value,
             'elements'     : [json.loads(e.dumps()) for e in self._elements]}

        return json.dumps(d, indent = 4)



class Element:

    def __init__(self, name, idx_lowest_bit, n_bits = 1, value = 0, read_only = False, code_name = None,
                 description = None):
        self.name = name
        self.idx_lowest_bit = idx_lowest_bit
        self.n_bits = n_bits
        self._value = value
        self.read_only = read_only
        self.code_name = code_name or name
        self.description = description


    @property
    def value(self):
        return self._value


    @value.setter
    def value(self, value):
        if not self.read_only:
            self._value = value


    @property
    def mask(self):
        return (2 ** self.n_bits - 1) << self.idx_lowest_bit


    @property
    def shifted_value(self):
        return (self.value << self.idx_lowest_bit) & self.mask


    def load_from_register(self, register_value):
        self.value = (register_value & self.mask) >> self.idx_lowest_bit


    @classmethod
    def loads(cls, json_string):
        attrs = json.loads(json_string)
        return Element(**attrs)


    def dumps(self):
        d = {'name'          : self.name,
             'idx_lowest_bit': self.idx_lowest_bit,
             'n_bits'        : self.n_bits,
             'value'         : self.value,
             'read_only'     : self.read_only,
             'code_name'     : self.code_name,
             'description'   : self.description}

        return json.dumps(d, indent = 4)
