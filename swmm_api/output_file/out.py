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
    Read the SWMM Output file (xxx.out).

    Notes:
        Combined the reader of `swmmtoolbox`_ with the functionality of pandas.

    Attributes:
        index (pandas.DatetimeIndex): Index of the timeseries of the data.
        flow_unit (str): Flow unit. One of ['CMS', 'LPS', 'MLD', 'CFS', 'GPM', 'MGD']
        labels (dict[str, list]): dictionary of the object labels as list (value) for each object type
            (keys are: ``'link'``, ``'node'``, ``'subcatchment'``)
        model_properties (dict[str, [dict[str, list]]]): property values for the subcatchments, nodes and links.
            The Properties for the objects are.

                    - ``subcatchment``
                      - [area]
                    - ``node``
                      - [type, invert, max. depth]
                    - ``link``
                      - type,
                      - offsets
                        - ht. above start node invert (ft),
                        - ht. above end node invert (ft),
                      - max. depth,
                      - length

        pollutant_units (dict[str, str]): Units per pollutant.
        report_interval (datetime.timedelta): Intervall of the index.
        start_date (datetime.datetime): Start date of the data.
        swmm_version (str): SWMM Version
        variables (dict[str, list]): variables per object-type inclusive the pollutants.

    .. _swmmtoolbox: https://github.com/timcera/swmmtoolbox
    """
    def __init__(self, filename):
        """
        SWMM Output file (xxx.out).

        Args:
            filename(str): path to .rpt file
        """
        SwmmOutExtract.__init__(self, filename)

        self._frame = None
        self._data = None

        # the main datetime index for the results
        self.index = date_range(self.start_date + self.report_interval,
                                periods=self.n_periods, freq=self.report_interval)

    def __repr__(self):
        return f'SwmmOutput(file="{self.filename}")'

    def _get_dtypes(self):
        """
        Get the dtypes of the data.

        Returns:
            str: numpy types
        """
        return 'f8' + ',f4' * self.number_columns

    @property
    def number_columns(self):
        """
        Get number of columns of the full results table.

        Returns:
            int: Number of columns of the full results table.
        """
        return sum(
            len(self.variables[kind]) * len(self.labels[kind])
            for kind in OBJECTS.LIST_
        )

    @property
    def _columns_raw(self):
        """
        get the column-names of the data

        Returns:
            list[list[str]]: multi-level column-names
        """
        columns = []
        for kind in OBJECTS.LIST_:
            columns += list(product([kind], self.labels[kind], self.variables[kind]))
        return columns

    def to_numpy(self):
        """
        Convert all data to a numpy-array.

        Returns:
            numpy.ndarray: all data
        """
        if self._data is None:
            types = [('datetime', 'f8')]
            types += list(map(lambda i: ('/'.join(i), 'f4'), self._columns_raw))
            self.fp.seek(self._pos_start_output, 0)
            self._data = fromfile(self.fp, dtype=dtype(types))
        return self._data

    def to_frame(self):
        """
        Convert all the data to a pandas-DataFrame.

        .. Important::
            This function may take a long time if the out-file has with many objects (=columns).
            If you just want the data of a few columns use :meth:`SwmmOutput.get_part` instead.

        Returns:
            pandas.DataFrame: data
        """
        if self._frame is None:
            self._frame = self._to_pandas(self.to_numpy())
            del self._frame['datetime']
        return self._frame

    def get_part(self, kind=None, label=None, variable=None, slim=False):
        """
        Get specific columns of the data.

        .. Important::
            Set the parameter ``slim`` to ``True`` to speedup the code if you just want a few columns and
            there are a lot of objects (many columns) and just few time-steps (fewer rows) in the out-file.

        Args:
            kind (str | list): [``'subcatchment'``, ``'node'`, ``'link'``, ``'system'``] (predefined in :obj:`swmm_api.output_file.definitions.OBJECTS`)
            label (str | list): name of the objekts
            variable (str | list): variable names (predefined in :obj:`swmm_api.output_file.definitions.VARIABLES`)

                * subcatchment:
                    - ``rainfall`` or :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.RAINFALL`
                    - ``snow_depth`` or :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.SNOW_DEPTH`
                    - ``evaporation`` or :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.EVAPORATION`
                    - ``infiltration`` or :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.INFILTRATION`
                    - ``runoff`` or :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.RUNOFF`
                    - ``groundwater_outflow`` or :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.GW_OUTFLOW`
                    - ``groundwater_elevation`` or :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.GW_ELEVATION`
                    - ``soil_moisture`` or :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.SOIL_MOISTURE`
                * node:
                    - ``depth`` or :attr:`~swmm_api.output_file.definitions.NODE_VARIABLES.DEPTH`
                    - ``head`` or :attr:`~swmm_api.output_file.definitions.NODE_VARIABLES.HEAD`
                    - ``volume`` or :attr:`~swmm_api.output_file.definitions.NODE_VARIABLES.VOLUME`
                    - ``lateral_inflow`` or :attr:`~swmm_api.output_file.definitions.NODE_VARIABLES.LATERAL_INFLOW`
                    - ``total_inflow`` or :attr:`~swmm_api.output_file.definitions.NODE_VARIABLES.TOTAL_INFLOW`
                    - ``flooding`` or :attr:`~swmm_api.output_file.definitions.NODE_VARIABLES.FLOODING`
                * link:
                    - ``flow`` or :attr:`~swmm_api.output_file.definitions.LINK_VARIABLES.FLOW`
                    - ``depth`` or :attr:`~swmm_api.output_file.definitions.LINK_VARIABLES.DEPTH`
                    - ``velocity`` or :attr:`~swmm_api.output_file.definitions.LINK_VARIABLES.VELOCITY`
                    - ``volume`` or :attr:`~swmm_api.output_file.definitions.LINK_VARIABLES.VOLUME`
                    - ``capacity`` or :attr:`~swmm_api.output_file.definitions.LINK_VARIABLES.CAPACITY`
                * system:
                    - ``air_temperature`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.AIR_TEMPERATURE`
                    - ``rainfall`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.RAINFALL`
                    - ``snow_depth`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.SNOW_DEPTH`
                    - ``infiltration`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.INFILTRATION`
                    - ``runoff`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.RUNOFF`
                    - ``dry_weather_inflow`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.DW_INFLOW`
                    - ``groundwater_inflow`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.GW_INFLOW`
                    - ``RDII_inflow`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.RDII_INFLOW`
                    - ``direct_inflow`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.DIRECT_INFLOW`
                    - ``lateral_inflow`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.LATERAL_INFLOW`
                    - ``flooding`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.FLOODING`
                    - ``outflow`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.OUTFLOW`
                    - ``volume`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.VOLUME`
                    - ``evaporation`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.EVAPORATION`
                    - ``PET`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.PET`

            slim (bool): set to ``True`` to speedup the code if there are a lot of objects and just few time-steps in the out-file.

        Returns:
            pandas.DataFrame | pandas.Series: Filtered data.
                (return Series if only one column is selected otherwise return a DataFrame)
        """
        columns = self._filter_part_columns(kind, label, variable)
        if slim:
            values = self._get_selective_results(columns)
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

        columns = []
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
        Write the data in a parquet file.

        multi-column-names are separated by a slash ("/")

        Uses the function :func:`swmm_api.output_file.parquet.write`, which is based on :meth:`pandas.DataFrame.to_parquet` to write the file.

        Read parquet files with :func:`swmm_api.output_file.parquet.read` to get the original column-name-structure.
        """
        parquet.write(self.to_frame(), self.filename.replace('.out', '.parquet'))


def read_out_file(filename):
    """
    Read the SWMM Output file (xxx.out).

    Args:
        filename (str): filename of the output file

    Returns:
        SwmmOutput: output file object

    See Also:
        :meth:`SwmmOutput.__init__` : Equal functionality.
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
        Don't use this function if many object are in the out file, and you only need few of them.
        In this case use the method :meth:`SwmmOutput.get_part` instead.
    """
    out = SwmmOutput(filename)
    return out.to_frame()
