__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

import pandas as pd
from swmmtoolbox.swmmtoolbox import SwmmExtract
import numpy as np

#from mp.helpers.check_time import class_timeit, Timer

from . import parquet


class SwmmOutHandler(SwmmExtract):
    """
    read the binary .out file from EPA-SWMM and return a pandas Dataframe
    """
    def __init__(self, filename):
        self.filename = filename
        SwmmExtract.__init__(self, filename)
        self.names_by_type = self._get_names_by_type()
        self.variables_by_type = self._get_variables_by_type()
        self.frame = None
        self.data = None

    def _get_names_by_type(self):
        new_catalog = dict()
        for i, name in enumerate(self.itemlist):
            l = self.names[i]
            if l:
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

    #@class_timeit
    def to_numpy(self):
        """
        read the binary .out file from EPA-SWMM and return a pandas Dataframe

        Returns:
            pandas.DataFrame: data
        """
        if self.data is None:
            self.fp.seek(self.startpos, 0)

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
                types.append((col_name(kind, var_name, var_name), 'f4'))

            dt = np.dtype(types)
            self.data = np.fromfile(self.fp, dtype=dt)
        return self.data

    #@class_timeit
    def to_frame(self):
        if self.frame is None:
            with Timer('DataFrame'):
                data = self.to_numpy()
                self.frame = pd.DataFrame(data=data, columns=data.dtype.names, dtype=data.dtype)
            del self.frame['date']
            with Timer('_index_to_multiindex'):
                self.frame.columns = parquet._index_to_multiindex(self.frame.columns.astype(str))
            with Timer('date_range'):
                self.frame.index = pd.date_range(self.startdate, periods=self.swmm_nperiods, freq=self.reportinterval)
        return self.frame

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

# def out2parquet(out_file):
#     out = SwmmOutHandler(out_file)
#     out.to_parquet()
