from numpy import isnan
from pandas import DataFrame
from tqdm import tqdm
import re

from .type_converter import type2str

SWMM_VERSION = '5.1.015'


########################################################################################################################
class CustomDict:
    """imitate :class:`collections.UserDict` (:term:`dict-like <mapping>`) but operations only effect self._data"""

    def __init__(self, d=None, **kwargs):
        if d is None:
            self._data = kwargs
        else:
            if isinstance(d, dict):
                self._data = d
            else:
                self._data = dict(d)

    def __len__(self):
        return self._data.__len__()

    def __getitem__(self, key):
        return self._data.__getitem__(key)

    def __setitem__(self, key, item):
        self._data.__setitem__(key, item)
        # TODO: 3x slower
        # try except is even slower
        # for debugging

        # try:
        #     exec(f'self.{key} = item')
        # except (SyntaxError, AttributeError):
        #     pass

        # key_ = key
        # if isinstance(key_, tuple):
        #     key_ = '_'.join(key)
        # else:
        #     key = f'"{key}"'
        #
        # # if key_[0].isdigit():
        # #     pre = 'z__'
        # # else:
        # #     pre = ''
        #
        # key_ = key_.replace("-", "_").replace(".", "_")
        # exec(f'self.{"z__" * key_[0].isdigit()}{key_} = self[{key}]')

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
        return type(self)(self._data.copy())

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

    def __bool__(self):
        return bool(self._data)


########################################################################################################################
class InpData(CustomDict):
    """
    overall class for an input file

    child class of dict

    just used for the copy function and to identify ``.inp``-file data
    """
    def copy(self):
        """
        get a copy of the ``.inp``-file data

        Returns:
            InpData: a copy of the ``.inp``-file data
        """
        new = type(self)()
        for key in self:
            if isinstance(self[key], str):
                new[key] = self[key]
            else:
                new[key] = self[key].copy()
            exec(f'new.{key} = new["{key}"]')
        return new

    def __setitem__(self, key, item):
        self._data.__setitem__(key, item)
        exec(f'self.{key} = self["{key}"]')

    def __getitem__(self, key):
        """

        Returns:
            InpSection | InpSectionGeneric:
        """
        return self._data.__getitem__(key)
        # return super()._data.__getitem__(self, key)

    # def __getattr__(self, item):
    #     return self._data[item]
    #
    # def __setattr__(self, key, value):
    #     self[key] = value


########################################################################################################################
class InpSectionGeneric(dict):
    """
    abstract class for ``.inp``-file sections without objects

    :term:`dict-like <mapping>`"
    """

    @classmethod
    def from_inp_lines(cls, lines):
        """
        read ``.inp``-file lines and create an section object

        Args:
            lines (str | list[list[str]]): lines in the section of the ``.inp``-file

        Returns:
            InpSectionGeneric: object of the section
        """
        pass

    def to_inp_lines(self, fast=False):
        """
        write ``.inp``-file lines of the section object

        Args:
            fast (bool): speeding up conversion

                - :obj:`True`: if no special formation of the input file is needed
                - :obj:`False`: section is converted into a table to prettify string output (slower)

        Returns:
            str: ``.inp``-file lines of the section object
        """
        f = ''
        max_len = len(max(self.keys(), key=len)) + 2
        for sub in self:
            f += '{key}{value}'.format(key=sub.ljust(max_len),
                                       value=type2str(self[sub]) + '\n')
        return f

    def copy(self):
        """
        get a copy of the ``.inp``-file data

        Returns:
            InpData: a copy of the ``.inp``-file data
        """
        return type(self)(dict.copy(self))


########################################################################################################################
class InpSection(CustomDict):
    """
    class for ``.inp``-file sections with objects (i.e. nodes, links, subcatchments, raingages, ...)
    """
    def __init__(self, section_object):
        """
        create an object for ``.inp``-file sections with objects (i.e. nodes, links, subcatchments, raingages, ...)

        Args:
            section_object (BaseSectionObject-like): object class which is stored in this section.
                This information is used to set the index of the section and
                to decide if the section can be exported (converted to a string) as a table.
        """
        CustomDict.__init__(self)
        self._section_object = section_object

    @property
    def objects(self):
        return self._data

    @property
    def _identifier(self):
        # to set the index of the section (key to select an object an index for the dataframe export)
        return self._section_object._identifier

    @property
    def _table_inp_export(self):
        # if the section can be exported (converted to a string) as a table.
        return self._section_object._table_inp_export

    def append(self, item):
        """
        add object(s) to section

        Args:
            item (BaseSectionObject | list[BaseSectionObject]): new objects
        """
        if isinstance(item, (list, tuple)):
            for i in item:
                self.append(i)
        else:
            self[item.get(self._identifier)] = item

    @classmethod
    def from_inp_lines(cls, lines, section_class):
        """
        convert the lines of a section to this class and each line to a object

        This function is used for the ``.inp``-file reading

        Args:
            lines (str | list[list[str]]): lines of a section in a ``.inp``-file
            section_class (BaseSectionObject): object class which is stored in this section.

        Returns:
            InpSection: section of the ``.inp``-file
        """

        def txt_to_lines(content):
            for line in re.findall(r'^[ \t]*([^;\n]+)[ \t]*;?[^\n]*$', content, flags=re.M):
                # ;; section comment
                # ; object comment / either inline(at the end of the line) or before the line
                # if ';' in line:
                #     line
                # line = line.split(';')[0]
                # line = line.strip()
                # if line == '':  # ignore empty and comment lines
                #     continue
                # else:
                yield line.split()

        if isinstance(lines, str):
            if len(lines) > 10000000:
                n_lines = lines.count('\n') + 1
                # to create a progressbar in the reading process
                # only needed with big (> 200 MB) files
                lines = txt_to_lines(lines)
                lines = tqdm(lines, desc=section_class.__name__, total=n_lines)
            else:
                lines = txt_to_lines(lines)

        return section_class.create_section(lines)

    def to_inp_lines(self, fast=False):
        """
        convert the section to a multi-line ``.inp``-file conform string

        This function is used for the ``.inp``-file writing

        Args:
            fast (bool): speeding up conversion

                - :obj:`True`: if no special formation of the input file is needed
                - :obj:`False`: section is converted into a table to prettify string output (slower)

        Returns:
             str: lines of the ``.inp``-file section
        """
        if not self:  # if empty
            return ';; No Data'

        if fast or not self._table_inp_export:
            return '\n'.join(o.to_inp_line() for o in self.values())
        else:
            return dataframe_to_inp_string(self.frame)

    @property
    def frame(self):
        """convert section to a pandas data-frame

        This property is used for debugging purposes and data analysis of the input data of the swmm model.

        Returns:
            pandas.DataFrame: section as table
        """
        if not self:  # if empty
            return DataFrame()

        return DataFrame([i.to_dict_() for i in self.values()]).set_index(self._identifier)

    def copy(self):
        """
        get a copy of the section

        Returns:
            InpSection: copy of the section
        """
        new = type(self)(self._section_object)
        # ΔTime: 18.678 s
        # new._data = deepcopy(self._data)
        # ΔTime: 2.943 s
        new._data = {k: self[k].copy() for k in self}
        return new

    def filter_keys(self, keys, by=None):
        """
        filter parts of the section with keys (identifier strings or attribute string)

        Args:
            keys (list | set): list of names to filter by (ether the identifier or the attribute of "by")
            by (str | list[str] |tuple[str]): attribute name of the section object to filter by

        Returns:
            InpSection: new filtered section
        """
        new = type(self)(self._section_object)
        if by is None:
            new._data = {k: self[k] for k in set(self.keys()).intersection(keys)}
        elif isinstance(by, (list, set, tuple)):
            new._data = {k: self[k] for k in self.keys() if all(map(lambda b: self[k][b] in keys, by))}
        else:
            new._data = {k: self[k] for k in self.keys() if self[k][by] == keys}
        return new


########################################################################################################################
class BaseSectionObject:
    """
    base class for all section objects to unify operations

    sections objects only have __init__ with object parameters

    acts :term:`like a dict <mapping>` (getter and setter)"""
    _identifier = ''
    """str: attribute of an object which will be used as identifiers"""
    _table_inp_export = True
    """bool: if an section is writeable as table. Default ist True"""

    _section_class = InpSection

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
        return self._to_debug_string()

    def _to_debug_string(self):
        """for debugging purposes

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

    def to_inp_line(self):
        """
        convert object to one line of the ``.inp``-file

        for ``.inp``-file writing

        Returns:
            str: SWMM .inp file compatible string
        """
        di = self.to_dict_()
        s = ''
        if isinstance(self._identifier, list):
            s += ' '.join([str(di.pop(i)) for i in self._identifier])
        else:
            s += str(di.pop(self._identifier))

        s += ' ' + ' '.join([type2str(i) for i in di.values()])
        return s

    @classmethod
    def from_inp_line(cls, *line):
        """
        convert line in the ``.inp``-file to the object

        Args:
            *line (list[str]): arguments in the line

        Returns:
            BaseSectionObject: object of the ``.inp``-file section
        """
        return cls(*line)

    def copy(self):
        """
        copy object

        Returns:
            BaseSectionObject: copy of the object
        """
        return type(self)(**vars(self).copy())

    @classmethod
    def create_section(cls, lines=None):
        """
        create an object for ``.inp``-file sections with objects

        i.e. nodes, links, subcatchments, raingages, ...
        """
        if lines is None:
            return cls._section_class(cls)
        else:
            sec = cls._section_class(cls)
            for obj in cls._convert_lines(lines):
                sec.append(obj)
            return sec

    @classmethod
    def _convert_lines(cls, lines):
        """
        convert the ``.inp``-file section

        creates an object for each line and yields them

        Args:
            lines (list[list[str]]): lines in the input file section

        Yields:
            BaseSectionObject: object of the ``.inp``-file section
        """
        # overwrite if each object has multiple lines
        for line in lines:
            yield cls.from_inp_line(*line)


########################################################################################################################
def dataframe_to_inp_string(df):
    """convert a data-frame into a multi-line string

    used to make a better readable .inp file and for debugging

    Args:
        df (pandas.DataFrame): section table

    Returns:
        str: .inp file conform string for one section
    """
    comment_sign = ';;'
    if df.empty:
        return ';; NO data'

    c = df.copy()
    if c.columns.name is None:
        c.columns.name = comment_sign
    else:
        if not c.columns.name.startswith(comment_sign):
            c.columns.name = comment_sign + c.columns.name

    if c.index.name is not None:
        if not c.index.name.startswith(comment_sign):
            c.index.name = comment_sign + c.index.name

    if c.index._typ == 'multiindex':
        if c.index.names is not None:
            if not c.index.levels[0].name.startswith(comment_sign):
                c.index.set_names(';' + c.index.names[0], level=0, inplace=True)
                # because pandas 1.0
                # c.index.levels[0].name = ';' + c.index.levels[0].name

    return c.applymap(type2str).to_string(sparsify=False,
                                          line_width=999999,
                                          max_rows=999999,
                                          max_cols=999999,
                                          max_colwidth=999999)
