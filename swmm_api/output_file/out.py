__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

from swmmtoolbox.swmmtoolbox import SwmmExtract
from pandas import date_range, DataFrame, MultiIndex
from numpy import dtype, fromfile

from . import parquet


class SwmmOutHandler(SwmmExtract):
    """
    read the binary .out-file of EPA-SWMM
    """

    def __init__(self, filename):
        self.filename = filename
        SwmmExtract.__init__(self, filename)
        self.names_by_type = self._get_names_by_type()
        self.variables_by_type = self._get_variables_by_type()
        self._frame = None
        self._data = None
        self._index = date_range(self.startdate, periods=self.swmm_nperiods, freq=self.reportinterval)

    def _get_names_by_type(self):
        new_catalog = dict()
        for i, name in enumerate(self.itemlist):
            if self.names[i]:
                new_catalog[name] = self.names[i]
        return new_catalog

    def _get_variables_by_type(self):
        new_catalog = dict()
        for item_type in self.itemlist:
            if item_type == 'pollutant':
                continue
                # 'pollutant' really isn't it's own itemtype
                # but part of subcatchment, node, and link...

            new_catalog[item_type] = self.varcode[self.type_check(item_type)]
        return new_catalog

    def _get_columns(self):
        """
        get the dtypes and column names of the data

        Returns:
            numpy.dtype: structed numpy types (with names)
        """

        def col_name(kind, name, var_name):
            return '{kind}/{name}/{var_name}'.format(kind=kind, name=name, var_name=var_name)

        types = [('date', 'f8')]
        kind = 'subcatchment'
        for i in range(self.swmm_nsubcatch):
            name = self.names_by_type[kind][i]
            for v in range(self.swmm_nsubcatchvars):
                var_name = self.variables_by_type[kind][v]
                types.append((col_name(kind, name, var_name), 'f4'))

        kind = 'node'
        for i in range(self.swmm_nnodes):
            name = self.names_by_type[kind][i]
            for v in range(self.nnodevars):
                var_name = self.variables_by_type[kind][v]
                types.append((col_name(kind, name, var_name), 'f4'))

        kind = 'link'
        for i in range(self.swmm_nlinks):
            name = self.names_by_type[kind][i]
            for v in range(self.nlinkvars):
                var_name = self.variables_by_type[kind][v]
                types.append((col_name(kind, name, var_name), 'f4'))

        kind = 'system'
        for i in range(self.nsystemvars):
            var_name = self.variables_by_type[kind][i]
            types.append((col_name(kind, kind, var_name), 'f4'))

        return dtype(types)

    def to_numpy(self):
        """
        read the binary .out-file of EPA-SWMM and return a numpy array

        Returns:
            numpy.ndarray: all data
        """
        if self._data is None:
            self.fp.seek(self.startpos, 0)
            self._data = fromfile(self.fp, dtype=self._get_columns())
        return self._data

    def to_frame(self):
        """
        convert the data to a pandas Dataframe

        Returns:
            pandas.DataFrame: data
        """
        if self._frame is None:
            data = self.to_numpy()
            d = dict()
            for col in data.dtype.names:
                if col == 'date':
                    continue
                d[col] = data[col]
            self._frame = DataFrame(d)
            self._frame.index = self._index
            self._frame.columns = MultiIndex.from_tuples([col.split('/') for col in self._frame.columns])
        return self._frame

    def get_part(self, kind=None, name=None, var_name=None):
        """
        convert specific columns of the data to a pandas-DataFame

        Args:
            kind (str | list): ["subcatchment", "node", "link", "system"]
            name (str | list): name of the objekts
            var_name (str | list): variable names

        Returns:
            pandas.DataFrame: filtered data
        """
        data = self.to_numpy()

        def filter_name(n):
            if (isinstance(kind, str) and n.startswith(kind) or
                    isinstance(kind, list) and any(n.startswith(i) for i in kind) or
                    isinstance(name, str) and n.contains('/{}/'.format(name)) or
                    isinstance(name, list) and any(n.contains('/{}/'.format(i)) for i in name) or
                    isinstance(var_name, str) and n.endswith(var_name) or
                    isinstance(var_name, list) and any(n.endswith(i) for i in var_name)):
                return True
            else:
                return False

        columns = list(filter(filter_name, data.dtype.names))

        df = DataFrame(data[columns])

        df.index = self._index
        df.columns = self._columns(columns, drop_useless=True)
        return df

    @staticmethod
    def _columns(columns, drop_useless=False):
        """"""
        c = MultiIndex.from_tuples([col.split('/') for col in columns])
        if drop_useless:
            c = c.droplevel([i for i, l in enumerate(c.levshape) if l == 1])
        return c

    def to_parquet(self):
        """
        read the binary .out file from EPA-SWMM and write the data to a parquet file
        multi-column-names are separated by a slash ("/")
        read parquet files with parquet.read to get the original column-name-structure
        """
        parquet.write(self.to_frame(), self.filename.replace('.out', '.parquet'))


def out2frame(out_file):
    """
    read the binary .out file from EPA-SWMM and return a pandas Dataframe

    Args:
        out_file (str): path to out file

    Returns:
        pandas.DataFrame:
    """
    out = SwmmOutHandler(out_file)
    return out.to_frame()
