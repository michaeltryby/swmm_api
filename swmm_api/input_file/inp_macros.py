import pickle
from os import path, remove
from warnings import warn
from pandas import Series, DataFrame

from swmm_api.input_file.inp_sections_generic import CurvesSection
from .inp_sections import CrossSectionCustom
from ..run import swmm5_run
from ..output_file import SwmmOutHandler, parquet
from .inp_reader import read_inp_file
from .inp_helpers import InpData
from .inp_writer import write_inp_file, inp2string
from .helpers.sections import REPORT, XSECTIONS, CURVES
from .helpers.type_converter import offset2delta


class InpMacros(InpData):
    def __init__(self):
        InpData.__init__(self, {})
        self.filename = None
        self.basename = None
        self.dirname = None

    def set_name(self, name):
        self.filename = name
        self.basename = '.'.join(path.basename(name).split('.')[:-1])
        self.dirname = path.dirname(name)

    @property
    def report_filename(self):
        return path.join(self.dirname, self.basename + '.rpt')

    @property
    def out_filename(self):
        return path.join(self.dirname, self.basename + '.out')

    @property
    def parquet_filename(self):
        return path.join(self.dirname, self.basename + '.parquet')

    def __repr__(self):
        return str(self)

    def __str__(self):
        return inp2string(self)

    def read_file(self, ignore_sections=None, convert_sections=None, custom_converter=None,
                  ignore_gui_sections=True):
        data = read_inp_file(self.filename, ignore_sections=ignore_sections, convert_sections=convert_sections,
                             custom_converter=custom_converter, ignore_gui_sections=ignore_gui_sections)
        InpData.__init__(self, data)

    @classmethod
    def from_file(cls, filename, ignore_sections=None, convert_sections=None, custom_converter=None,
                  ignore_gui_sections=True):
        inp = cls()
        inp.set_name(filename)
        inp.read_file(ignore_sections=ignore_sections, convert_sections=convert_sections,
                      custom_converter=custom_converter, ignore_gui_sections=ignore_gui_sections)
        return inp

    # @class_timeit
    def write(self, fast=True):
        write_inp_file(self, self.filename, fast=fast)

    @classmethod
    def from_pickle(cls, fn):
        new = cls()
        pkl_file = open(fn, 'rb')
        new._data = pickle.load(pkl_file)
        pkl_file.close()
        return new

    def to_pickle(self, fn):
        output = open(fn, 'wb')
        pickle.dump(self._data, output)
        output.close()

    # ------------------------------------------------------------------------------------------------------------------
    # @class_timeit
    def execute_swmm(self, rpt_dir=None, out_dir=None, init_print=False):
        swmm5_run(self.filename, rpt_dir=rpt_dir, out_dir=out_dir, init_print=init_print)

    def delete_report_file(self):
        remove(self.report_filename)

    def delete_inp_file(self):
        remove(self.filename)

    # @class_timeit
    def run(self, rpt_dir=None, out_dir=None, init_print=False):
        self.execute_swmm(rpt_dir=rpt_dir, out_dir=out_dir, init_print=init_print)
        self.convert_out()

    # ------------------------------------------------------------------------------------------------------------------
    # @class_timeit
    def get_out(self):
        return SwmmOutHandler(self.out_filename)

    # @class_timeit
    def get_out_frame(self):
        out = self.get_out()
        df = out.to_frame()
        # TODO check if file can be deleted
        out.fp.close()
        del out
        return df

    # @class_timeit
    def convert_out(self):
        out = self.get_out()
        out.to_parquet()
        if out.filename:
            try:
                remove(out.filename)
            except PermissionError as e:
                warn(str(e))

    def delete_out_file(self):
        remove(self.out_filename)

    # @class_timeit
    def get_result_frame(self):
        if not path.isfile(self.parquet_filename):
            self.convert_out()
        return parquet.read(self.parquet_filename)

    ####################################################################################################################
    # @property
    # def report(self):
    #     if 'REPORT' in self:
    #         return self['REPORT']
    #     else:
    #         return None
    #
    # @property
    # def options(self):
    #     if 'OPTIONS' in self:
    #         return self['OPTIONS']
    #     else:
    #         return None
    #
    # @property
    # def curves(self):
    #     if 'CURVES' in self:
    #         return self['CURVES']
    #     else:
    #         return None
    #
    # @property
    # def timeseries(self):
    #     if 'TIMESERIES' in self:
    #         return self['TIMESERIES']
    #     else:
    #         return None
    #
    # @property
    # def inflows(self):
    #     if 'INFLOWS' in self:
    #         return self['INFLOWS']
    #     else:
    #         return None

    ####################################################################################################################
    def reset_section(self, cat, cls):
        if cat in self:
            del self[cat]
        self[cat] = cls

    def check_section(self, cat, cls):
        if cat not in self:
            self[cat] = cls

    def set_start(self, start, incl_report=True):
        self.check_section('OPTIONS', Series())
        self['OPTIONS'].loc['START_DATE'] = start.date()
        self['OPTIONS'].loc['START_TIME'] = start.time()

        if incl_report:
            self.set_start_report(start)

    def set_start_report(self, start):
        self.check_section('OPTIONS', Series())
        self['OPTIONS'].loc['REPORT_START_DATE'] = start.date()
        self['OPTIONS'].loc['REPORT_START_TIME'] = start.time()

    def set_end(self, end):
        self.check_section('OPTIONS', Series())
        self['OPTIONS'].loc['END_DATE'] = end.date()
        self['OPTIONS'].loc['END_TIME'] = end.time()

    def set_threads(self, num):
        self.check_section('OPTIONS', Series())
        self['OPTIONS'].loc['THREADS'] = num

    def ignore_rainfall(self, on=True):
        self.check_section('OPTIONS', Series())
        self['OPTIONS'].loc['IGNORE_RAINFALL'] = on

    def ignore_snowmelt(self, on=True):
        self.check_section('OPTIONS', Series())
        self['OPTIONS'].loc['IGNORE_SNOWMELT'] = on

    def ignore_groundwater(self, on=True):
        self.check_section('OPTIONS', Series())
        self['OPTIONS'].loc['IGNORE_GROUNDWATER'] = on

    def ignore_quality(self, on=True):
        self.check_section('OPTIONS', Series())
        self['OPTIONS'].loc['IGNORE_QUALITY'] = on

    def set_intervals(self, freq):
        self.check_section('OPTIONS', Series())
        new_step = offset2delta(freq)
        self['OPTIONS']['REPORT_STEP'] = new_step
        self['OPTIONS']['WET_STEP'] = new_step
        self['OPTIONS']['DRY_STEP'] = new_step

    def activate_report(self, input=False, continuity=True, flowstats=True, controls=False):
        self.check_section('REPORT', Series())
        self['REPORT'].loc['INPUT'] = input
        self['REPORT'].loc['CONTINUITY'] = continuity
        self['REPORT'].loc['FLOWSTATS'] = flowstats
        self['REPORT'].loc['CONTROLS'] = controls

    def reduce_curves(self):
        reduce_curves(self)

    def add_obj_to_report(self, new_obj, obj_kind):
        if isinstance(new_obj, str):
            new_obj = [new_obj]
        elif isinstance(new_obj, list):
            pass
        else:
            raise NotImplementedError('Type: {} not implemented!'.format(type(new_obj)))

        old_obj = self[REPORT][obj_kind]
        if isinstance(old_obj, str):
            old_obj = [old_obj]
        elif isinstance(old_obj, (int, float)):
            old_obj = [str(old_obj)]
        elif isinstance(old_obj, list):
            pass
        elif old_obj is None:
            old_obj = []
        else:
            raise NotImplementedError('Type: {} not implemented!'.format(type(old_obj)))

        self[REPORT][obj_kind] = old_obj + new_obj

    def add_nodes_to_report(self, new_nodes):
        self.add_obj_to_report(new_nodes, 'NODES')

    def add_links_to_report(self, new_links):
        self.add_obj_to_report(new_links, 'LINKS')

    def add_timeseries_file(self, fn):
        self.check_section('TIMESERIES', dict())
        if 'Files' not in self['TIMESERIES']:
            self['TIMESERIES']['Files'] = DataFrame(columns=['Type', 'Fname'])

        self['TIMESERIES']['Files'] = self['TIMESERIES']['Files'].append(
            Series({'Fname': '"' + fn + '.dat"'}, name=path.basename(fn)))
        self['TIMESERIES']['Files']['Type'] = 'FILE'


def reduce_curves(inp):
    """

    :type inp: InpData
    """
    curves = set([xs.Curve for xs in inp[XSECTIONS].values() if isinstance(xs, CrossSectionCustom)])
    # curves |= set(self[OUTFALLS]['Data'].dropna().unique().tolist())
    # self[CURVES][CurvesSection.TYPES.SHAPE].update(self[CURVES][CurvesSection.TYPES.SHAPE])

    old_shapes = inp[CURVES].pop(CurvesSection.TYPES.SHAPE)

    new_curves = {}
    for c in curves:
        if c in old_shapes:
            new_curves.update({c: old_shapes[c]})

    inp[CURVES].update({CurvesSection.TYPES.SHAPE: new_curves})
    return inp
