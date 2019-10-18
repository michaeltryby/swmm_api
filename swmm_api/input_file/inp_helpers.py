from pandas import DataFrame
from numpy import isnan, NaN

from .helpers.type_converter import type2str, infer_type


########################################################################################################################
class UserDict_:
    """imitate UserDict / user class like dict but operations only effect self._data"""

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
        return UserDict_(self._data.copy())

    def values(self):
        return self._data.values()

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()

    def update(self, d=None, **kwargs):
        self._data.update(d, **kwargs)

    @property
    def empty(self):
        return not bool(self._data)

    def pop(self, key):
        return self._data.pop(key)


########################################################################################################################
class BaseSectionObject:
    """base class for all section objects to unify operations
    sections objects only have __init__ with object parameters"""
    index = ''

    def get(self, key):
        if isinstance(key, list):
            return tuple([self.get(k) for k in key])
        return self.to_dict_().get(key)

    def set(self, key, value):
        assert key in self.to_dict_()
        vars(self)[key] = value

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, item):
        self.set(key, item)

    def to_dict_(self):
        """
        get all object parameters as dictionary

        Returns:
            dict:
        """
        return vars(self).copy()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.to_debug_string()

    def to_debug_string(self):
        """
        for debugging purposes
        string is almost equal to python syntax
        so you could copy it and past it into your code

        Returns:
            str: debug string of the object
        """
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
        """
        convert object to one line of the .inp file
        for .inp file writing

        Returns:
            str: SWMM .inp file compatible string
        """
        di = self.to_dict_()
        s = ''
        if isinstance(self.index, list):
            s += ' '.join([str(di.pop(i)) for i in self.index])
        else:
            s += str(di.pop(self.index))

        s += ' ' + ' '.join([type2str(i) for i in di.values()])
        return s

    @classmethod
    def from_line(cls, *line):
        return cls(*line)


########################################################################################################################
class InpSectionGeneric:
    @classmethod
    def from_lines(cls, lines):
        pass

    def __repr__(self):
        pass

    def __str__(self):
        pass

    def to_inp(self, fast=False):
        pass


########################################################################################################################
class InpSection(UserDict_):
    """each section of the .inp file is converted to such a section"""

    def __init__(self, index):
        if isinstance(index, str):
            self.index = index
        if isinstance(index, list):
            self.index = index
        elif isinstance(index, type):
            if issubclass(index, BaseSectionObject):
                self.index = index.index
        UserDict_.__init__(self)

    def append(self, item):
        """
        add object(s)/item(s) to section

        Args:
            item (BaseSectionObject | list[BaseSectionObject]):
        """
        if isinstance(item, (list, tuple)):
            for i in item:
                self.append(i)
        else:
            self[item.get(self.index)] = item

    @classmethod
    def from_lines(cls, lines, section_class):
        """
        for .inp file reading
        convert all lines of a section to this class and each line to a object

        Args:
            lines (list[str]): lines of a section in a .inp file
            section_class (BaseSectionObject):

        Returns:
            InpSection: of one section
        """
        inp_section = cls(section_class)

        if hasattr(section_class, 'convert_lines'):
            for section_class_line in section_class.convert_lines(lines):
                inp_section.append(section_class_line)
            return inp_section

        # -----------------------
        for line in lines:
            line = infer_type(line)
            inp_section.append(section_class.from_line(*line))

        return inp_section

    @property
    def frame(self):
        """
        convert section to a data-frame
        for debugging purpose

        Returns:
            pandas.DataFrame:
        """
        di = {}
        if not self.empty:
            for n, i in enumerate(self.values()):
                di[n] = i.to_dict_()
            return DataFrame.from_dict(di, 'index').set_index(self.index)
        else:
            return DataFrame()

    # def __repr__(self):
    #     return dataframe_to_inp_string(self.frame)
    #
    # def __str__(self):
    #     return dataframe_to_inp_string(self.frame)

    def to_inp(self, fast=False):
        """
        section to a multi-line string
        for .inp file writing

        Args:
            fast (bool): dont use any formatting else format as table

        Returns:
            str: .inp file string
        """
        if fast:
            if not self.empty:
                s = ''
                for i in self.values():
                    s += i.inp_line() + '\n'
                return s
            else:
                return ''

        else:
            return dataframe_to_inp_string(self.frame)


class InpData(UserDict_):
    def copy(self):
        return InpData(self._data.copy())


def dataframe_to_inp_string(df):
    """
    convert a data-frame into a multi-line string
    used to make a better readable .inp file and for debugging

    Args:
        df (pandas.DataFrame): section table

    Returns:
        str: .inp file conform string for one section
    """
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
