__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"


from itertools import product
from numpy import dtype, fromfile
from pandas import date_range, DataFrame, MultiIndex
from .extract import SwmmOutExtract
from .definitions import OBJECTS, VARIABLES

from . import parquet


class SwmmOutput(SwmmOutExtract):
    """
    SWMM Output file (xxx.out).

    combined the reader of `swmmtoolbox`_ with the functionality of pandas

    .. _swmmtoolbox: https://github.com/timcera/swmmtoolbox
    """
    def __init__(self, filename):
        """
        SWMM Output file (xxx.out).

        Args:
            filename(str): path to .rpt file

        Notes:
            based on the python package swmmtoolbox
        """
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
    def _columns_raw(self):
        """
        get the column-names of the data

        Returns:
            list[list[str]]: multi-level column-names
        """
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
            types += list(map(lambda i: ('/'.join(i), 'f4'), self._columns_raw))
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
            kind (str | list): ["subcatchment", "node", "link", "system"] (predefined in :obj:`swmm_api.output_file.definitions.OBJECTS`)
            label (str | list): name of the objekts
            variable (str | list): variable names (predefined in :obj:`swmm_api.output_file.definitions.VARIABLES`)

                * subcatchment:
                    - ``rainfall`` i.e.: :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.RAINFALL`
                    - ``snow_depth`` i.e.: :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.SNOW_DEPTH`
                    - ``evaporation`` i.e.: :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.EVAPORATION`
                    - ``infiltration`` i.e.: :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.INFILTRATION`
                    - ``runoff`` i.e.: :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.RUNOFF`
                    - ``groundwater_outflow`` i.e.: :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.GW_OUTFLOW`
                    - ``groundwater_elevation`` i.e.: :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.GW_ELEVATION`
                    - ``soil_moisture`` i.e.: :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.SOIL_MOISTURE`
                * node:
                    - ``depth`` i.e.: :attr:`~swmm_api.output_file.definitions.NODE_VARIABLES.DEPTH`
                    - ``head`` i.e.: :attr:`~swmm_api.output_file.definitions.NODE_VARIABLES.HEAD`
                    - ``volume`` i.e.: :attr:`~swmm_api.output_file.definitions.NODE_VARIABLES.VOLUME`
                    - ``lateral_inflow`` i.e.: :attr:`~swmm_api.output_file.definitions.NODE_VARIABLES.LATERAL_INFLOW`
                    - ``total_inflow`` i.e.: :attr:`~swmm_api.output_file.definitions.NODE_VARIABLES.TOTAL_INFLOW`
                    - ``flooding`` i.e.: :attr:`~swmm_api.output_file.definitions.NODE_VARIABLES.FLOODING`
                * link:
                    - ``flow`` i.e.: :attr:`~swmm_api.output_file.definitions.LINK_VARIABLES.FLOW`
                    - ``depth`` i.e.: :attr:`~swmm_api.output_file.definitions.LINK_VARIABLES.DEPTH`
                    - ``velocity`` i.e.: :attr:`~swmm_api.output_file.definitions.LINK_VARIABLES.VELOCITY`
                    - ``volume`` i.e.: :attr:`~swmm_api.output_file.definitions.LINK_VARIABLES.VOLUME`
                    - ``capacity`` i.e.: :attr:`~swmm_api.output_file.definitions.LINK_VARIABLES.CAPACITY`
                * system:
                    - ``air_temperature`` i.e.: :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.AIR_TEMPERATURE`
                    - ``rainfall`` i.e.: :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.RAINFALL`
                    - ``snow_depth`` i.e.: :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.SNOW_DEPTH`
                    - ``infiltration`` i.e.: :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.INFILTRATION`
                    - ``runoff`` i.e.: :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.RUNOFF`
                    - ``dry_weather_inflow`` i.e.: :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.DW_INFLOW`
                    - ``groundwater_inflow`` i.e.: :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.GW_INFLOW`
                    - ``RDII_inflow`` i.e.: :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.RDII_INFLOW`
                    - ``direct_inflow`` i.e.: :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.DIRECT_INFLOW`
                    - ``lateral_inflow`` i.e.: :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.LATERAL_INFLOW`
                    - ``flooding`` i.e.: :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.FLOODING`
                    - ``outflow`` i.e.: :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.OUTFLOW`
                    - ``volume`` i.e.: :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.VOLUME`
                    - ``evaporation`` i.e.: :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.EVAPORATION`
                    - ``PET`` i.e.: :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.PET`

            slim (bool): set to `True` if there are a lot of objects and just few time-steps in the out-file.


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


def read_out_file(filename):
    """
    Read the SWMM Output file (xxx.rpt).

    Args:
        filename (str): filename of the output file

    Returns:
        SwmmOutput: output file object
    """
    return SwmmOutput(filename)


def out2frame(filename):
    """
    Get the content of the SWMM Output file as a DataFrame

    Args:
        filename (str): filename of the output file

    Returns:
        pandas.DataFrame: Content of the SWMM Output file

    .. Important::
        don't use this function if many object are in the out file and you only need few of them.
        In this case use the method :meth:`SwmmOutput.get_part` instead.
    """
    out = SwmmOutput(filename)
    return out.to_frame()
