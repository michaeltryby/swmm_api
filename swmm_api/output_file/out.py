__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"


from itertools import product
from numpy import dtype, fromfile
from pandas import date_range, DataFrame, MultiIndex
from .extract import SwmmOutExtract, OBJECTS, VARIABLES

from . import parquet


class SwmmOut(SwmmOutExtract):
    """
    read the binary .out-file of EPA-SWMM

    based on the python package swmmtoolbox

    combined the reader of swmmtoolbox with the functionality of pandas
    """

    def __init__(self, filename):
        SwmmOutExtract.__init__(self, filename)

        self._frame = None
        self._data = None

        # the main datetime index for the results
        self.index = date_range(self.start_date + self.report_interval,
                                periods=self.n_periods, freq=self.report_interval)

    def __repr__(self):
        return f'SwmmOut(file="{self.filename}")'

    def _get_dtypes(self):
        """
        get the dtypes of the data

        Returns:
            str: numpy types
        """
        return 'f8' + ',f4' * self.number_columns

    @property
    def number_columns(self):
        """
        get number of columns of the full results table

        Returns:
            int: number of columns of the full results table
        """
        return sum([len(self.variables[kind]) * len(self.labels[kind]) for kind in OBJECTS.LIST_])

    @property
    def columns_raw(self):
        columns = list()
        for kind in OBJECTS.LIST_:
            columns += list(product([kind], self.labels[kind], self.variables[kind]))
        return columns

    def to_numpy(self):
        """
        read the full binary .out-file of EPA-SWMM and return a numpy array

        Returns:
            numpy.ndarray: all data
        """
        if self._data is None:
            types = [('datetime', 'f8')]
            types += list(map(lambda i: ('/'.join(i), 'f4'), self.columns_raw))
            self.fp.seek(self.pos_start_output, 0)
            self._data = fromfile(self.fp, dtype=dtype(types))
        return self._data

    def to_frame(self):
        """
        convert all the data to a pandas-DataFrame

        Warnings:
            for a big out-file with many objects, this function may take a long time

        Returns:
            pandas.DataFrame: data
        """
        if self._frame is None:
            self._frame = self._to_pandas(self.to_numpy())
            del self._frame['datetime']
        return self._frame

    def get_part(self, kind=None, label=None, variable=None, slim=False):
        """
        get specific columns of the data to a pandas-DataFame (or pandas-Series for a single column)

        use this function instead of "get_part" if there are a lot of objects in the out-file.

        Args:
            kind (str | list): ["subcatchment", "node", "link", "system"]
            label (str | list): name of the objekts
            variable (str | list): variable names
            slim (bool): set to `True` if there are a lot of objects and just few time-steps in the out-file.

                * node:
                    - ``Depth_above_invert``
                    - ``Hydraulic_head``
                    - ``Volume_stored_ponded``
                    - ``Lateral_inflow``
                    - ``Total_inflow``
                    - ``Flow_lost_flooding``
                * link:
                    - ``Flow_rate``
                    - ``Flow_depth``
                    - ``Flow_velocity``
                    - ``Froude_number``
                    - ``Capacity``
                * system:
                    - ``Air_temperature``
                    - ``Rainfall``
                    - ``Snow_depth``
                    - ``Evaporation_infiltration``
                    - ``Runoff``
                    - ``Dry_weather_inflow``
                    - ``Groundwater_inflow``
                    - ``RDII_inflow``
                    - ``User_direct_inflow``
                    - ``Total_lateral_inflow``
                    - ``Flow_lost_to_flooding``
                    - ``Flow_leaving_outfalls``
                    - ``Volume_stored_water``
                    - ``Evaporation_rate``
                    - ``Potential_PET``


        Returns:
            pandas.DataFrame | pandas.Series: filtered data
        """
        columns = self._filter_part_columns(kind, label, variable)
        if slim:
            values = self.get_selective_results(columns)
        else:
            values = self.to_numpy()[list(map('/'.join, columns))]

        return self._to_pandas(values, drop_useless=True)

    def _filter_part_columns(self, kind=None, label=None, variable=None):
        """
        filter which columns should be extracted

        Args:
            kind (str | list): ["subcatchment", "node", "link", "system"]
            label (str | list): name of the objekts
            variable (str | list): variable names

        Returns:
            list: filtered list of tuple(kind, label, variable)
        """
        def _filter(i, possibilities):
            if i is None:
                return possibilities
            elif isinstance(i, str):
                if i in possibilities:
                    return [i]
                else:
                    return []
            elif isinstance(i, list):
                return [j for j in i if j in possibilities]

        columns = list()
        for k in _filter(kind, OBJECTS.LIST_):
            columns += list(product([k], _filter(label, self.labels[k]), _filter(variable, self.variables[k])))
        return columns

    def _to_pandas(self, data, drop_useless=False):
        """
        convert interim results to pandas DataFrame or Series

        Args:
            data (dict, numpy.ndarray): timeseries data of swmm out file
            drop_useless (bool): if single column data should be returned as Series

        Returns:
            (pandas.DataFrame | pandas.Series): pandas Timerseries of data
        """
        if isinstance(data, dict):
            if not bool(data):
                return DataFrame()
            df = DataFrame.from_dict(data).set_index(self.index)
        else:
            if data.size == 0:
                return DataFrame()
            df = DataFrame(data, index=self.index, dtype=float)

        # -----------
        if df.columns.size == 1:
            return df.iloc[:, 0]
        # -----------
        df.columns = MultiIndex.from_tuples([col.split('/') for col in df.columns])
        if drop_useless:
            df.columns = df.columns.droplevel([i for i, l in enumerate(df.columns.levshape) if l == 1])

        return df

    def to_parquet(self):
        """
        read the binary .out file from EPA-SWMM and write the data to a parquet file

        multi-column-names are separated by a slash ("/")
        read parquet files with parquet.read to get the original column-name-structure
        """
        parquet.write(self.to_frame(), self.filename.replace('.out', '.parquet'))


def read_out_file(out_filename):
    """
    read the binary ``.out``-file of EPA-SWMM

    based on the python package swmmtoolbox

    combined the reader of swmmtoolbox with the functionality of pandas

    Returns:
        SwmmOut: class to extract data fromm the ``.out``-file
    """
    return SwmmOut(out_filename)


def out2frame(out_file):
    """
    read the binary .out file from EPA-SWMM and return a pandas Dataframe

    Attention! don't use this if many object are in the out file an you only need few objects.
    Use ``.get_part`` functionality of base class (return of ``read_out_file`` function)

    Args:
        out_file (str): path to out file

    Returns:
        pandas.DataFrame:
    """
    out = SwmmOut(out_file)
    return out.to_frame()
