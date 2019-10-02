from pandas import DataFrame
from numpy import isnan, NaN

from .helpers.type_converter import type2str, infer_type


def convert_name(name, new_name='J'):
    if isinstance(name, str):
        if '_' in name:
            return name
        new_name += name
    elif isinstance(name, int):
        new_name += '{:02d}'.format(name)
    else:
        new_name += str(name)
    return new_name


class MyUserDict:

    def __init__(self, d=None, **kwargs):
        if d is None:
            self._data = kwargs
        else:
            self._data = dict(d)

    def __len__(self):
        return self._data.__len__()

    def __getitem__(self, key):
        return self._data.__getitem__(key)

    def __setitem__(self, key, item):
        self._data.__setitem__(key, item)

    def __delitem__(self, key):
        self._data.__delitem__(key)

    def __iter__(self):
        return self._data.__iter__()

    def __contains__(self, key):
        return self._data.__contains__(key)

    def __repr__(self):
        return self._data.__repr__()

    def __str__(self):
        return self._data.__str__()

    def get(self, key, default=None):
        if isinstance(key, list):
            return (self.get(k) for k in key)
        return self._data.get(key) if key in self else default

    def copy(self):
        return MyUserDict(self._data.copy())

    def values(self):
        return self._data.values()

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()

    def update(self, d=None, **kwargs):
        self._data.update(d, **kwargs)

    def pop(self, key):
        return self._data.pop(key)


class BaseSection:
    index = ''

    def get(self, key):
        if isinstance(key, list):
            return tuple([self.get(k) for k in key])
        return self.to_dict_().get(key)

    def to_dict_(self):
        return vars(self)

    def __repr__(self):
        return str(self)

    def __str__(self):
        args = list()
        for k, d in self.to_dict_().items():
            if isinstance(d, float) and isnan(d):
                args.append('{} = NaN'.format(k))
            elif isinstance(d, str):
                args.append('{} = "{}"'.format(k, d))
            else:
                args.append('{} = {}'.format(k, d))
        return '{}({})'.format(self.__class__.__name__, ', '.join(args))

    def inp_line(self):
        di = self.to_dict_().copy()
        s = ''
        if isinstance(self.index, list):
            s += ' '.join([str(di.pop(i)) for i in self.index])
        else:
            s += str(di.pop(self.index))

        s += ' ' + ' '.join([type2str(i) for i in di.values()])
        return s

    # @property
    # def string(self):
    #     return str(self)


class InpSection(MyUserDict):
    def __init__(self, index):
        if isinstance(index, str):
            self.index = index
        if isinstance(index, list):
            self.index = index
        elif isinstance(index, type):
            if issubclass(index, BaseSection):
                self.index = index.index
        MyUserDict.__init__(self)

    def append(self, item):
        """

        Args:
            item (BaseSection | list[BaseSection]):
        """
        if isinstance(item, list):
            for i in item:
                self.append(i)
        else:
            self[item.get(self.index)] = item

    @classmethod
    def from_lines(cls, lines, section_class):
        """

        Args:
            lines (list):
            section_class (BaseSection):

        Returns:
            InpSection:
        """
        if isinstance(section_class, type):
            inp_section = cls(section_class)
        else:
            inp_section = None

        # -----------------------
        # section with multiple line entries
        # ie.: Pattern
        if inp_section is not None and hasattr(section_class, 'convert_lines'):
            for section_class_line in section_class.convert_lines(lines):
                inp_section.append(section_class_line)
            return inp_section

        # -----------------------
        for line in lines:
            line = infer_type(line)
            if inp_section is None:
                # if multiple types are possible and ie.: Infiltration
                first_section_line = section_class(*line)
                inp_section = cls(type(first_section_line))
                inp_section.append(first_section_line)

            else:
                inp_section.append(section_class(*line))
        return inp_section

    def to_frame_(self):
        """

        Returns:
            pandas.DataFrame:
        """
        di = {}
        if bool(self):
            for n, i in enumerate(self.values()):
                d = i.to_dict_()
                di[n] = d
            return DataFrame.from_dict(di, 'index').set_index(self.index)
        else:
            return DataFrame()

    @property
    def frame(self):
        """

        Returns:
            pandas.DataFrame:
        """
        return self.to_frame_()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return dataframe_to_inp_string(self.to_frame_())

    def to_inp(self, fast=False):
        if fast:
            if bool(self):
                s = ''
                for i in self.values():
                    s += i.inp_line() + '\n'
                return s
            else:
                return ''

        else:
            return str(self)


def dataframe_to_inp_string(df):
    if df.empty:
        return '; NO data'

    c = df.copy()
    if c.columns.name is None:
        c.columns.name = ';'
    else:
        if not c.columns.name.startswith(';'):
            c.columns.name = ';' + c.columns.name

    if c.index.name is not None:
        if not c.index.name.startswith(';'):
            c.index.name = ';' + c.index.name

    if c.index._typ == 'multiindex':
        if c.index.names is not None:
            if not c.index.levels[0].name.startswith(';'):
                c.index.levels[0].name = ';' + c.index.levels[0].name

    return c.applymap(type2str).to_string(sparsify=False, line_width=9999)
