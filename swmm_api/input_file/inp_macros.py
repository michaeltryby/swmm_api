import pickle
from os import path, remove
from warnings import warn
from pandas import Series, DataFrame

from .inp_sections_generic import CurvesSection
from .inp_sections import CrossSectionCustom, Conduit, Storage, Outfall
from ..run import swmm5_run
from ..output_file import SwmmOutHandler, parquet
from .inp_reader import read_inp_file
from .inp_helpers import InpData, InpSection
from .inp_writer import write_inp_file, inp2string
# from .helpers.sections import REPORT, XSECTIONS, CURVES, STORAGE, PUMPS, SUBCATCHMENTS, RAINGAGES, SUBAREAS, \
#     INFILTRATION, COORDINATES, VERTICES
from .helpers import sections as S
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
    #     if S.REPORT in self:
    #         return self[S.REPORT]
    #     else:
    #         return None
    #
    # @property
    # def options(self):
    #     if S.OPTIONS in self:
    #         return self[S.OPTIONS]
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
    #     if S.TIMESERIES in self:
    #         return self[S.TIMESERIES]
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
        self.check_section(S.OPTIONS, Series())
        self[S.OPTIONS].loc['START_DATE'] = start.date()
        self[S.OPTIONS].loc['START_TIME'] = start.time()

        if incl_report:
            self.set_start_report(start)

    def set_start_report(self, start):
        self.check_section(S.OPTIONS, Series())
        self[S.OPTIONS].loc['REPORT_START_DATE'] = start.date()
        self[S.OPTIONS].loc['REPORT_START_TIME'] = start.time()

    def set_end(self, end):
        self.check_section(S.OPTIONS, Series())
        self[S.OPTIONS].loc['END_DATE'] = end.date()
        self[S.OPTIONS].loc['END_TIME'] = end.time()

    def set_threads(self, num):
        self.check_section(S.OPTIONS, Series())
        self[S.OPTIONS].loc['THREADS'] = num

    def ignore_rainfall(self, on=True):
        self.check_section(S.OPTIONS, Series())
        self[S.OPTIONS].loc['IGNORE_RAINFALL'] = on

    def ignore_snowmelt(self, on=True):
        self.check_section(S.OPTIONS, Series())
        self[S.OPTIONS].loc['IGNORE_SNOWMELT'] = on

    def ignore_groundwater(self, on=True):
        self.check_section(S.OPTIONS, Series())
        self[S.OPTIONS].loc['IGNORE_GROUNDWATER'] = on

    def ignore_quality(self, on=True):
        self.check_section(S.OPTIONS, Series())
        self[S.OPTIONS].loc['IGNORE_QUALITY'] = on

    def set_intervals(self, freq):
        self.check_section(S.OPTIONS, Series())
        new_step = offset2delta(freq)
        self[S.OPTIONS]['REPORT_STEP'] = new_step
        self[S.OPTIONS]['WET_STEP'] = new_step
        self[S.OPTIONS]['DRY_STEP'] = new_step

    def activate_report(self, input=False, continuity=True, flowstats=True, controls=False):
        self.check_section(S.REPORT, Series())
        self[S.REPORT].loc['INPUT'] = input
        self[S.REPORT].loc['CONTINUITY'] = continuity
        self[S.REPORT].loc['FLOWSTATS'] = flowstats
        self[S.REPORT].loc['CONTROLS'] = controls

    def reduce_curves(self):
        reduce_curves(self)

    def add_obj_to_report(self, new_obj, obj_kind):
        if isinstance(new_obj, str):
            new_obj = [new_obj]
        elif isinstance(new_obj, list):
            pass
        else:
            raise NotImplementedError('Type: {} not implemented!'.format(type(new_obj)))

        old_obj = self[S.REPORT][obj_kind]
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

        self[S.REPORT][obj_kind] = old_obj + new_obj

    def add_nodes_to_report(self, new_nodes):
        self.add_obj_to_report(new_nodes, 'NODES')

    def add_links_to_report(self, new_links):
        self.add_obj_to_report(new_links, 'LINKS')

    def add_timeseries_file(self, fn):
        self.check_section(S.TIMESERIES, dict())
        if 'Files' not in self[S.TIMESERIES]:
            self[S.TIMESERIES]['Files'] = DataFrame(columns=['Type', 'Fname'])

        self[S.TIMESERIES]['Files'] = self[S.TIMESERIES]['Files'].append(
            Series({'Fname': '"' + fn + '.dat"'}, name=path.basename(fn)))
        self[S.TIMESERIES]['Files']['Type'] = 'FILE'


def reduce_curves(inp):
    """

    :type inp: InpData
    """
    if S.CURVES not in inp:
        return inp

    # ---------------------
    def _reduce(all_curves, kind, curves):
        if kind not in all_curves:
            return all_curves
        old_curves = all_curves.pop(kind)

        new_curves = {}
        for c in curves:
            if c in old_curves:
                new_curves.update({c: old_curves[c]})

        all_curves.update({kind: new_curves})
        return all_curves

    # ---------------------
    inp[S.CURVES] = _reduce(inp[S.CURVES],
                            kind=CurvesSection.TYPES.SHAPE,
                            curves=set(
                                [xs.Curve for xs in inp[S.XSECTIONS].values() if isinstance(xs, CrossSectionCustom)]))

    if S.STORAGE in inp:
        inp[S.CURVES] = _reduce(inp[S.CURVES],
                                kind=CurvesSection.TYPES.STORAGE,
                                curves=set([st.Curve for st in inp[S.STORAGE].values() if st.Type == st.Types.TABULAR]))

    # ---------------------
    if S.PUMPS in inp:
        curves = set([pu.Pcurve for pu in inp[S.PUMPS].values() if pu.Pcurve != '*'])
        for kind in [CurvesSection.TYPES.PUMP1, CurvesSection.TYPES.PUMP2, CurvesSection.TYPES.PUMP3,
                     CurvesSection.TYPES.PUMP4]:
            inp[S.CURVES] = _reduce(inp[S.CURVES],
                                    kind=kind,
                                    curves=curves)
    return inp


def reduce_raingages(inp):
    """

    :type inp: InpData
    """
    if S.SUBCATCHMENTS not in inp or S.RAINGAGES not in inp:
        return inp
    needed_raingages = list()
    for s in inp[S.SUBCATCHMENTS].values():
        needed_raingages.append(s.RainGage)

    needed_raingages = set(needed_raingages)

    current_rain_gages = list(inp[S.RAINGAGES].keys())
    for rg in current_rain_gages:
        if rg not in needed_raingages:
            inp[S.RAINGAGES].pop(rg)

    return inp


def combined_subcatchment_infos(inp):
    return inp[S.SUBCATCHMENTS].frame.join(inp[S.SUBAREAS].frame).join(inp[S.INFILTRATION].frame)

#
# def coordinates_frame(inp):
#     return DataFrame.from_records(inp[COORDINATES]).rename(columns={0: 'name',
#                                                                     1: 'x',
#                                                                     2: 'y'}).set_index('name', drop=True).astype(float)
#
#
# def vertices_frame(inp):
#     return DataFrame.from_records(inp[VERTICES]).rename(columns={0: 'name',
#                                                                  1: 'x',
#                                                                  2: 'y'}).set_index('name', drop=True).astype(float)


def find_node(inp, label):
    for kind in [S.JUNCTIONS, S.OUTFALLS, S.DIVIDERS, S.STORAGE]:
        if (kind in inp) and (label in inp[kind]):
            return inp[kind][label]


def find_link(inp, label):
    for kind in [S.CONDUITS, S.PUMPS, S.ORIFICES, S.WEIRS, S.OUTLETS]:
        if (kind in inp) and (label in inp[kind]):
            return inp[kind][label]


def calc_slope(inp, link):
    return (find_node(inp, link.FromNode).Elevation - find_node(inp, link.ToNode).Elevation) / link.Length


def delete_node(inp, node):
    # print('DELETE (node): ', node)
    if isinstance(node, str):
        n = find_node(inp, node)
    else:
        n = node
        node = n.Name

    for kind in [S.JUNCTIONS, S.OUTFALLS, S.DIVIDERS, S.STORAGE]:
        if (kind in inp) and (node in inp[kind]):
            inp[kind].pop(node)
    inp[S.COORDINATES].pop(node)

    # delete connected links
    for i_name, i in inp[S.CONDUITS].copy().items():
        if (i.ToNode == node) or (i.FromNode == node):
            # print('DELETE (link): ', i_name)
            inp[S.CONDUITS].pop(i_name)
            inp[S.XSECTIONS].pop(i_name)
            inp[S.VERTICES].pop(i_name)

    return inp


def combine_conduits(inp, c1, c2):
    if isinstance(c1, str):
        c1 = inp[S.CONDUITS][c1]
    if isinstance(c2, str):
        c2 = inp[S.CONDUITS][c2]

    c_new = c2.copy()
    c_new.Length += c1.Length

    v_new = inp[S.VERTICES][c1.Name] + inp[S.VERTICES][c2.Name]

    xs_new = inp[S.XSECTIONS][c2.Name]

    if c1.FromNode == c2.ToNode:
        c_new.ToNode = c1.ToNode
        inp = delete_node(inp, c2.ToNode)

    elif c1.ToNode == c2.FromNode:
        c_new.FromNode = c1.FromNode
        inp = delete_node(inp, c2.FromNode)
    else:
        raise EnvironmentError('Links not connected')

    inp[S.VERTICES][c_new.Name] = v_new
    inp[S.CONDUITS].append(c_new)
    inp[S.XSECTIONS].append(xs_new)
    return inp


def conduit_iter_over_inp(inp, start, end=None):
    """
    only correct when FromNode and ToNode are in the correct direction
    doesn't look backwards if split node

    Args:
        inp:
        start (str):

    Returns:
        Yields: input conduits
    """
    node = start
    while True:
        found = False
        for i, c in inp[S.CONDUITS].items():
            if c.FromNode == node:
                conduit = c

                node = conduit.ToNode
                yield conduit
                found = True
                break
        if not found or (node is not None and (node == end)):
            break


def junction_to_storage(inp, label, *args, **kwargs):
    j = inp[S.JUNCTIONS].pop(label)  # type: S.Junction
    if S.STORAGE not in inp:
        inp[S.STORAGE] = InpSection(Storage)
    inp[S.STORAGE].append(Storage(Name=label, Elevation=j.Elevation, MaxDepth=j.MaxDepth,
                                  InitDepth=j.InitDepth, Apond=j.Aponded, *args, **kwargs))


def junction_to_outfall(inp, label, *args, **kwargs):
    j = inp[S.JUNCTIONS].pop(label)  # type: S.Junction
    if S.OUTFALLS not in inp:
        inp[S.OUTFALLS] = InpSection(Outfall)
    inp[S.OUTFALLS].append(Outfall(Name=label, Elevation=j.Elevation, *args, **kwargs))
