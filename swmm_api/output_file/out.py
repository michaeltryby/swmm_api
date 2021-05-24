__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

from os import remove

from itertools import product
from numpy import dtype, fromfile
from pandas import date_range, DataFrame, MultiIndex, Series
from .extract import SwmmOutExtract, OBJECTS, VARIABLES

from . import parquet

from tqdm import tqdm


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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.fp.close()

    def delete(self):
        self.close()
        remove(self.filename)

    def __del__(self):
        self.close()

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
        # if self.number_columns > 1000:
        #     return self.get_part_slim(kind, name, var_name)

        data = self.to_numpy()

        # maybe easier ?!?!
        # c = MultiIndex.from_tuples(self.columns_raw)

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
        df = self._to_pandas(data[columns], drop_useless=True)
        if len(columns) == 1:
            return df.iloc[:, 0]
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
            for i in tqdm(range(self.n_periods)):
                for label, args in parts.items():
                    if i == 0:
                        values[label] = list()
                    value = self.get_swmm_results(*args, i)
                    values[label].append(value)
            df = DataFrame.from_dict(values).set_index(self.index)
            df.columns = self._columns(df.columns, drop_useless=True)
            return df

        # -------------------------------------------------------------
        else:
            index_kind = OBJECTS.LIST_.index(kind)
            index_variable = self.variables[kind].index(var_name)

            values = []
            for i in tqdm(range(self.n_periods)):
                value = self.get_swmm_results(index_kind, name, index_variable, i)
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
        for k in OBJECTS.LIST_:
            if _checker(k, kind):
                continue

            kind_index = OBJECTS.LIST_.index(k)

            for l in self.labels[k]:
                if _checker(l, name):
                    continue

                for v in self.variables[k]:
                    if _checker(v, var_name):
                        continue

                    parts['{}/{}/{}'.format(k, l, v)] = (kind_index, l, self.variables[k].index(v))
        return parts

    @staticmethod
    def _columns(columns, drop_useless=False):
        if drop_useless and (columns.size == 1):
            return [columns[0]]
        c = MultiIndex.from_tuples([col.split('/') for col in columns])
        if drop_useless:
            c = c.droplevel([i for i, l in enumerate(c.levshape) if l == 1])
        return c

    def _to_pandas(self, data, drop_useless=False):
        # d = dict()
        # for col in data.dtype.names:
        #     if col == 'datetime':
        #         continue
        #     d[col] = data[col]
        df = DataFrame(data, index=self.index, dtype=float)
        df.columns = self._columns(df.columns, drop_useless=drop_useless)
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
