__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

from swmmtoolbox.swmmtoolbox import SwmmExtract
from pandas import date_range, DataFrame, MultiIndex
from numpy import dtype, fromfile
from os import remove

from . import parquet


class SwmmOutHandler:
    """
    read the binary .out-file of EPA-SWMM
    """

    def __init__(self, filename):
        self.filename = filename
        self._extract = SwmmExtract(filename)

        self.labels = {self._extract.itemlist[k]: v for k, v in self._extract.names.items()}
        self._variables = None
        self._frame = None
        self._data = None
        self.index = date_range(self._extract.startdate, periods=self._extract.swmm_nperiods,
                                freq=self._extract.reportinterval)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._extract.fp.close()

    def delete(self):
        self.close()
        remove(self.filename)

    @property
    def variables(self):
        if self._variables is None:
            self._variables = dict()
            for i, kind in enumerate(self._extract.itemlist):
                if i in self._extract.varcode:
                    self._variables[kind] = [self._extract.varcode[i][j] for j in range(len(self._extract.varcode[i]))]
                else:
                    self._variables[kind] = list()
        return self._variables

    def _get_columns(self):
        """
        get the dtypes and column names of the data

        Returns:
            numpy.dtype: structed numpy types (with names)
        """
        types = [('date', 'f8')]

        for kind in self._extract.itemlist:
            if kind == 'system':
                labels = [None]
            else:
                labels = self.labels[kind]
            for label in labels:
                for variable in self.variables[kind]:
                    types.append(('{}/{}/{}'.format(kind, label, variable), 'f4'))

        return dtype(types)

    def to_numpy(self):
        """
        read the binary .out-file of EPA-SWMM and return a numpy array

        Returns:
            numpy.ndarray: all data
        """
        if self._data is None:
            self._extract.fp.seek(self._extract.startpos, 0)
            self._data = fromfile(self._extract.fp, dtype=self._get_columns())
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
            self._frame.index = self.index
            self._frame.columns = MultiIndex.from_tuples([col.split('/') for col in self._frame.columns])
        return self._frame

    def get_part(self, kind=None, name=None, var_name=None):
        """
        convert specific columns of the data to a pandas-DataFame

        Args:
            kind (str | list): ["subcatchment", "node", "link", "system"]
            name (str | list): name of the objekts
            var_name (str | list): variable names
                node:
                    ['Depth_above_invert',
                     'Hydraulic_head',
                     'Volume_stored_ponded',
                     'Lateral_inflow',
                     'Total_inflow',
                     'Flow_lost_flooding']
                link:
                    ['Flow_rate',
                     'Flow_depth',
                     'Flow_velocity',
                     'Froude_number',
                     'Capacity']
                system:
                    ['Air_temperature',
                     'Rainfall',
                     'Snow_depth',
                     'Evaporation_infiltration',
                     'Runoff',
                     'Dry_weather_inflow',
                     'Groundwater_inflow',
                     'RDII_inflow',
                     'User_direct_inflow',
                     'Total_lateral_inflow',
                     'Flow_lost_to_flooding',
                     'Flow_leaving_outfalls',
                     'Volume_stored_water',
                     'Evaporation_rate',
                     'Potential_PET']

        Returns:
            pandas.DataFrame | pandas.Series: filtered data
        """
        data = self.to_numpy()
        if isinstance(kind, str):
            kind = [kind]

        if isinstance(name, str):
            name = [name]

        if isinstance(var_name, str):
            var_name = [var_name]

        def filter_name(n):
            b = True
            if isinstance(kind, list):
                b &= any(n.startswith(i) for i in kind)
            if isinstance(name, list):
                b &= any(['/{}/'.format(i) in n for i in name])
            if isinstance(var_name, list):
                b &= any(n.endswith(i) for i in var_name)
            return b

        columns = list(filter(filter_name, data.dtype.names))

        df = DataFrame(data[columns])

        df.index = self.index
        if df.columns.size == 1:
            return df.iloc[:,0]
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
