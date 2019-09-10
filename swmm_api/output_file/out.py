import pandas as pd
from swmmtoolbox.swmmtoolbox import SwmmExtract
from sww.libs.timeseries.io import parquet
# from mp.helpers import class_timeit
import numpy as np

from sww.libs.timeseries.io.parquet import _index_to_multiindex


class SwmmOutHandler(SwmmExtract):

    def __init__(self, filename):
        self.filename = filename
        SwmmExtract.__init__(self, filename)
        self.names_by_type = self.get_names_by_type()
        self.variables_by_type = self.get_variables_by_type()
        self.frame = None

    def get_names_by_type(self):
        new_catalog = dict()
        for i, name in enumerate(self.itemlist):
            l = self.names[i]
            if l:
                new_catalog[name] = self.names[i]
        return new_catalog

    def get_variables_by_type(self):
        new_catalog = dict()
        for item_type in self.itemlist:
            if item_type == 'pollutant':
                continue
                # 'pollutant' really isn't it's own itemtype
                # but part of subcatchment, node, and link...

            new_catalog[item_type] = self.varcode[self.type_check(item_type)]
        return new_catalog

    def to_frame(self):
        if self.frame is None:
            self.fp.seek(self.startpos, 0)

            types = [('date', 'f8')]
            kind = 'subcatchment'
            for i in range(self.swmm_nsubcatch):
                name = self.names_by_type[kind][i]
                for v in range(self.swmm_nsubcatchvars):
                    var_name = self.variables_by_type[kind][v]
                    types.append((f'{kind}/{name}/{var_name}', 'f4'))

            kind = 'node'
            for i in range(self.swmm_nnodes):
                name = self.names_by_type[kind][i]
                for v in range(self.nnodevars):
                    var_name = self.variables_by_type[kind][v]
                    types.append((f'{kind}/{name}/{var_name}', 'f4'))

            kind = 'link'
            for i in range(self.swmm_nlinks):
                name = self.names_by_type[kind][i]
                for v in range(self.nlinkvars):
                    var_name = self.variables_by_type[kind][v]
                    types.append((f'{kind}/{name}/{var_name}', 'f4'))

            kind = 'system'
            for i in range(self.nsystemvars):
                var_name = self.variables_by_type[kind][i]
                types.append((f'{kind}/{var_name}/{var_name}', 'f4'))

            dt = np.dtype(types)
            data = np.fromfile(self.fp, dtype=dt)
            df = pd.DataFrame(data, columns=data.dtype.names)
            del df['date']
            df.columns = _index_to_multiindex(df.columns.astype(str))
            df.index = pd.date_range(self.startdate, periods=self.swmm_nperiods, freq=self.reportinterval)
            self.frame = df.copy()
        return self.frame

    def to_parquet(self):
        parquet.write(self.to_frame(), self.filename.replace('.out', '.parquet'))


def out2frame(out_file):
    out = SwmmOutHandler(out_file)
    return out.to_frame()


# def out2parquet(out_file):
#     out = SwmmOutHandler(out_file)
#     out.to_parquet()
