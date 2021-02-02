__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

from os import remove

from numpy import dtype, fromfile
from pandas import date_range, DataFrame, MultiIndex, Series
from swmmtoolbox.swmmtoolbox import SwmmExtract

from . import parquet


class VARIABLES:
    class KIND:
        SUBCATCHMENT = "subcatchment"
        NODE = "node"
        LINK = "link"
        SYSTEM = "system"

    class NODE:
        DEPTH_ABOVE_INVERT = 'Depth_above_invert'
        HYDRAULIC_HEAD = 'Hydraulic_head'
        VOLUME_STORED_PONDED = 'Volume_stored_ponded'
        LATERAL_INFLOW = 'Lateral_inflow'
        TOTAL_INFLOW = 'Total_inflow'
        FLOW_LOST_FLOODING = 'Flow_lost_flooding'

    class LINK:
        FLOW_RATE = 'Flow_rate'
        FLOW_DEPTH = 'Flow_depth'
        FLOW_VELOCITY = 'Flow_velocity'
        FROUDE_NUMBER = 'Froude_number'
        CAPACITY = 'Capacity'

    class SYSTEM:
        AIR_TEMPERATURE = 'Air_temperature'
        RAINFALL = 'Rainfall'
        SNOW_DEPTH = 'Snow_depth'
        EVAPORATION_INFILTRATION = 'Evaporation_infiltration'
        RUNOFF = 'Runoff'
        DRY_WEATHER_INFLOW = 'Dry_weather_inflow'
        GROUNDWATER_INFLOW = 'Groundwater_inflow'
        RDII_INFLOW = 'RDII_inflow'
        USER_DIRECT_INFLOW = 'User_direct_inflow'
        TOTAL_LATERAL_INFLOW = 'Total_lateral_inflow'
        FLOW_LOST_TO_FLOODING = 'Flow_lost_to_flooding'
        FLOW_LEAVING_OUTFALLS = 'Flow_leaving_outfalls'
        VOLUME_STORED_WATER = 'Volume_stored_water'
        EVAPORATION_RATE = 'Evaporation_rate'
        POTENTIAL_PET = 'Potential_PET'


class SwmmOutHandler:
    """
    read the binary .out-file of EPA-SWMM

    based on the python package swmmtoolbox

    combined the reader of swmmtoolbox with the functionality of pandas
    """

    def __init__(self, filename):
        self.filename = filename
        self._extract = SwmmExtract(filename)

        self._labels = None
        self._variables = None
        self._frame = None
        self._data = None
        self._index = None
        self._number_columns = None

    def __repr__(self):
        return f'SwmmOutHandler(file="{self.filename}")'

    # def __str__(self):
    #     return f'SwmmOutHandler({self.filename})'

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
    def labels(self):
        """
        get the dictionary of the object labels for each object type (link, node, subcatchment)

        Returns:
            dict: object-type: object-labels
        """
        if self._labels is None:
            self._labels = {self._extract.itemlist[k]: v for k, v in self._extract.names.items()}
        return self._labels

    @property
    def variables(self):
        """
        get the dictionary of the object variables for each object type (link, node, subcatchment)

        Returns:
            dict: object-type: object-variables
        """
        if self._variables is None:
            self._variables = dict()
            for i, kind in enumerate(self._extract.itemlist):
                if i in self._extract.varcode:
                    self._variables[kind] = [self._extract.varcode[i][j] for j in range(len(self._extract.varcode[i]))]
                else:
                    self._variables[kind] = list()
        return self._variables

    @property
    def index(self):
        """
        get the main datetime index for the results

        Returns:
            pandas.DatetimeIndex: main datetime index of the results
        """
        if self._index is None:
            self._index = date_range(self._extract.startdate, periods=self._extract.swmm_nperiods,
                                     freq=self._extract.reportinterval)
        return self._index

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

    @property
    def number_columns(self):
        """
        get number of columns of the full results table

        Returns:
            int: number of columns of the full results table
        """
        if self._number_columns is None:
            n = 0
            for kind in self._extract.itemlist:
                if kind == 'system':
                    labels = [None]
                else:
                    labels = self.labels[kind]

                n += len(self.variables[kind]) * len(labels)
            self._number_columns = n
        return self._number_columns

    def to_numpy(self):
        """
        read the full binary .out-file of EPA-SWMM and return a numpy array

        Returns:
            numpy.ndarray: all data
        """
        if self._data is None:
            self._extract.fp.seek(self._extract.startpos, 0)
            self._data = fromfile(self._extract.fp, dtype=self._get_columns())
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
        if self.number_columns > 1000:
            return self.get_part_slim(kind, name, var_name)

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
            return df.iloc[:, 0]
        df.columns = self._columns(columns, drop_useless=True)
        return df

    def get_part_slim(self, kind=None, name=None, var_name=None):
        """
        use this function instead of "get_part" if there are a lot of objects in the out-file.

        get specific columns of the data to a pandas-DataFame (or pandas-Series for a single column)

        Args:
            kind (str | list): ["subcatchment", "node", "link", "system"]
            name (str | list): name of the objekts
            var_name (str | list): variable names

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
        if not all([kind, name, var_name]):
            parts = self._get_part_args(kind, name, var_name)
            values = dict()
            for i in range(self._extract.swmm_nperiods):
                for label, args in parts.items():
                    if i == 0:
                        values[label] = list()
                    _, value = self._extract.get_swmm_results(*args, i)
                    values[label].append(value)
            df = DataFrame.from_dict(values).set_index(self.index)
            df.columns = self._columns(df.columns, drop_useless=True)
            return df

        # -------------------------------------------------------------
        else:
            index_kind = self._extract.itemlist.index(kind)
            index_variable = self.variables[kind].index(var_name)

            values = []
            for i in range(self._extract.swmm_nperiods):
                _, value = self._extract.get_swmm_results(index_kind, name, index_variable, i)
                values.append(value)

            return Series(values, index=self.index, name='{}/{}/{}'.format(kind, name, var_name))

    def _get_part_args(self, kind=None, name=None, var_name=None):
        """

        Args:
            kind (str | list): ["subcatchment", "node", "link", "system"]
            name (str | list): name of the objekts
            var_name (str | list): variable names

        Returns:
            dict: str(final column name) -> tuple(type-index, object-label, variable-index)
        """

        def _checker(i, user):
            if user is None:
                return False
            elif isinstance(user, list) and (i in user):
                return False
            elif isinstance(user, str) and (i == user):
                return False
            else:
                return True

        parts = dict()
        for k in self._extract.itemlist:
            if k == 'system':
                labels = [None]
            else:
                labels = self.labels[k]

            if _checker(k, kind):
                continue

            kind_index = self._extract.itemlist.index(k)

            for l in labels:
                if _checker(l, name):
                    continue

                for v in self.variables[k]:
                    if _checker(v, var_name):
                        continue

                    parts['{}/{}/{}'.format(k, l, v)] = (kind_index, l, self.variables[k].index(v))
        return parts

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


def read_out_file(out_filename):
    """
    read the binary ``.out``-file of EPA-SWMM

    based on the python package swmmtoolbox

    combined the reader of swmmtoolbox with the functionality of pandas

    Returns:
        SwmmOutHandler: class to extract data fromm the ``.out``-file
    """
    return SwmmOutHandler(out_filename)


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
    out = SwmmOutHandler(out_file)
    return out.to_frame()
