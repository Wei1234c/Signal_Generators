import math
from array import array



class Register:

    def __init__(self, name, code_name = None, address = None, description = None, elements = None, default_value = 0):
        self.name = name
        self.code_name = code_name or name
        self.address = address
        self.description = description
        self.elements = elements
        self._default_value = default_value


    @property
    def elements(self):
        return self._elements_dict


    @elements.setter
    def elements(self, elements):
        self._elements = elements or []
        self._elements_dict = self._elements_by_attr('name')


    def _elements_by_attr(self, attr):
        keyed_elements = {getattr(e, attr): e for e in self._elements}
        assert len(list(keyed_elements.keys())) == len(self._elements), '{} are not unique.'.format(attr)
        return keyed_elements


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
        self.load_from_register(self._default_value)


    def dump(self, as_hex = False):
        len_name_field = max([len(e.name) for e in self._elements] + [0])
        print('\n{:<{}s}:  {}'.format('<< ' + self.name + ' >>', len_name_field + 7,
                                      (hex(self.value), bin(self.value))))
        for e in self._elements:
            print('{:<{}s}:  {}'.format('[ ' + e.name + ' ]', len_name_field + 5,
                                        (hex(e.value), bin(e.value)) if as_hex else e.value))
        return len_name_field


    def load_from_dict(self, elements_dict_list):
        self.elements = [Element(**element_dict) for element_dict in elements_dict_list]


    @property
    def elements_dict_list(self):
        return [{'name'          : e.name,
                 'idx_lowest_bit': e.idx_lowest_bit,
                 'n_bits'        : e.n_bits,
                 'value'         : e.value,
                 'read_only'     : e.read_only,
                 'code_name'     : e.code_name,
                 'description'   : e.description} for e in self._elements]



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
