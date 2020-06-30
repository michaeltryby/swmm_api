import pickle
from os import path, remove
from warnings import warn
from pandas import Series, DataFrame, to_datetime

from .inp_section_types import SECTION_TYPES
from .inp_sections_generic import CurvesSection, ReportSection
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
        self._out = None

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

    def read_file(self, **kwargs):
        data = read_inp_file(self.filename, **kwargs)
        InpData.__init__(self, data)

    @classmethod
    def from_file(cls, filename, **kwargs):
        inp = cls()
        inp.set_name(filename)
        inp.read_file(**kwargs)
        return inp

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
    def execute_swmm(self, rpt_dir=None, out_dir=None, init_print=False):
        swmm5_run(self.filename, rpt_dir=rpt_dir, out_dir=out_dir, init_print=init_print)

    def delete_report_file(self):
        remove(self.report_filename)

    def delete_inp_file(self):
        remove(self.filename)

    def run(self, rpt_dir=None, out_dir=None, init_print=False):
        self.execute_swmm(rpt_dir=rpt_dir, out_dir=out_dir, init_print=init_print)
        self.convert_out()

    def __getitem__(self, section):
        self.check_section(section)
        return InpData.__getitem__(self, section)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def output_data(self):
        if self._out is None:
            self._out = SwmmOutHandler(self.out_filename)
        return self._out

    def get_out_frame(self):
        return self.output_data.to_frame()

    def convert_out(self):
        self.output_data.to_parquet()
        self.delete_out_file()

    def delete_out_file(self):
        # TODO check if file can be deleted
        self._out.close()
        try:
            remove(self.out_filename)
        except PermissionError as e:
            warn(str(e))

    def get_result_frame(self):
        if not path.isfile(self.parquet_filename):
            data = self.output_data.to_frame()
            self.convert_out()
            return data
        else:
            return parquet.read(self.parquet_filename)

    ####################################################################################################################
    def reset_section(self, section):
        if section in self:
            del self[section]
        self[section] = SECTION_TYPES[section]

    def check_section(self, section):
        if section not in self:
            self[section] = SECTION_TYPES[section]

    def set_start(self, start):
        if isinstance(start, str):
            start = to_datetime(start)
        self[S.OPTIONS]['START_DATE'] = start.date()
        self[S.OPTIONS]['START_TIME'] = start.time()

    def set_start_report(self, start):
        if isinstance(start, str):
            start = to_datetime(start)
        self[S.OPTIONS]['REPORT_START_DATE'] = start.date()
        self[S.OPTIONS]['REPORT_START_TIME'] = start.time()

    def set_end(self, end):
        if isinstance(end, str):
            end = to_datetime(end)
        self[S.OPTIONS]['END_DATE'] = end.date()
        self[S.OPTIONS]['END_TIME'] = end.time()

    def set_threads(self, num):
        self[S.OPTIONS]['THREADS'] = num

    def ignore_rainfall(self, on=True):
        self[S.OPTIONS]['IGNORE_RAINFALL'] = on

    def ignore_snowmelt(self, on=True):
        self[S.OPTIONS]['IGNORE_SNOWMELT'] = on

    def ignore_groundwater(self, on=True):
        self[S.OPTIONS]['IGNORE_GROUNDWATER'] = on

    def ignore_quality(self, on=True):
        self[S.OPTIONS]['IGNORE_QUALITY'] = on

    def set_intervals(self, freq):
        new_step = offset2delta(freq)
        self[S.OPTIONS]['REPORT_STEP'] = new_step
        self[S.OPTIONS]['WET_STEP'] = new_step
        self[S.OPTIONS]['DRY_STEP'] = new_step

    def activate_report(self, input=False, continuity=True, flowstats=True, controls=False):
        # r = self[S.REPORT]  # type: ReportSection
        # r.INPUT = input
        # r.CONTINUITY = continuity
        # r.FLOWSTATS = flowstats
        # r.CONTROLS = controls
        self[S.REPORT]['INPUT'] = input
        self[S.REPORT]['CONTINUITY'] = continuity
        self[S.REPORT]['FLOWSTATS'] = flowstats
        self[S.REPORT]['CONTROLS'] = controls

    def add_obj_to_report(self, obj_kind, new_obj):
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
        self.add_obj_to_report('NODES', new_nodes)

    def add_links_to_report(self, new_links):
        self.add_obj_to_report('LINKS', new_links)

    def add_timeseries_file(self, fn):  # TODO
        if 'Files' not in self[S.TIMESERIES]:
            self[S.TIMESERIES]['Files'] = DataFrame(columns=['Type', 'Fname'])

        self[S.TIMESERIES]['Files'] = self[S.TIMESERIES]['Files'].append(
            Series({'Fname': '"' + fn + '.dat"'}, name=path.basename(fn)))
        self[S.TIMESERIES]['Files']['Type'] = 'FILE'

    def reduce_curves(self):
        reduce_curves(self)

    def reduce_raingages(self):
        reduce_raingages(self)

    def combined_subcatchment_infos(self):
        return combined_subcatchment_infos(self)

    def find_node(self, label):
        return find_node(self, label)

    def find_link(self, label):
        return find_link(self, label)

    def calc_slope(self, link_label):
        return calc_slope(self, link_label)

    def delete_node(self, node_label):
        delete_node(self, node_label)

    def combine_conduits(self, c1, c2):
        combine_conduits(self, c1, c2)

    def conduit_iter_over_inp(self, start, end=None):
        conduit_iter_over_inp(self, start, end=end)

    def junction_to_outfall(self, label, *args, **kwargs):
        junction_to_outfall(self, label, *args, **kwargs)

    def junction_to_storage(self, label, *args, **kwargs):
        junction_to_storage(self, label, *args, **kwargs)


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
