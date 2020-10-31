import pickle
from os import path, remove, mkdir
from warnings import warn
from pandas import Series, DataFrame, to_datetime
import numpy as np

from .inp_sections.identifiers import IDENTIFIERS
from .inp_sections.types import SECTION_TYPES
from .inp_sections import *
from .inp_sections import labels as sec
from ..run import swmm5_run
from ..output_file import SwmmOutHandler, parquet
from .inp_reader import read_inp_file
from .inp_helpers import InpData, InpSection
from .inp_writer import write_inp_file, inp2string, section_to_string
from .helpers.type_converter import offset2delta


def section_from_frame(df, section_class):
    # TODO: testing
    a = np.vstack((df.index.values, df.values.T)).T
    return InpSection.from_lines(a, section_class)
    # return cls.from_lines([line.split() for line in dataframe_to_inp_string(df).split('\n')], section_class)


def split_inp_to_files(inp_fn, **kwargs):
    parent = inp_fn.replace('.inp', '')
    mkdir(parent)
    inp = read_inp_file(inp_fn, **kwargs)
    for s in inp.keys():
        with open(path.join(parent, s + '.txt'), 'w') as f:
            f.write(section_to_string(inp[s], fast=False))


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
        self[sec.OPTIONS]['START_DATE'] = start.date()
        self[sec.OPTIONS]['START_TIME'] = start.time()

    def set_start_report(self, start):
        if isinstance(start, str):
            start = to_datetime(start)
        self[sec.OPTIONS]['REPORT_START_DATE'] = start.date()
        self[sec.OPTIONS]['REPORT_START_TIME'] = start.time()

    def set_end(self, end):
        if isinstance(end, str):
            end = to_datetime(end)
        self[sec.OPTIONS]['END_DATE'] = end.date()
        self[sec.OPTIONS]['END_TIME'] = end.time()

    def set_threads(self, num):
        self[sec.OPTIONS]['THREADS'] = num

    def ignore_rainfall(self, on=True):
        self[sec.OPTIONS]['IGNORE_RAINFALL'] = on

    def ignore_snowmelt(self, on=True):
        self[sec.OPTIONS]['IGNORE_SNOWMELT'] = on

    def ignore_groundwater(self, on=True):
        self[sec.OPTIONS]['IGNORE_GROUNDWATER'] = on

    def ignore_quality(self, on=True):
        self[sec.OPTIONS]['IGNORE_QUALITY'] = on

    def set_intervals(self, freq):
        new_step = offset2delta(freq)
        self[sec.OPTIONS]['REPORT_STEP'] = new_step
        self[sec.OPTIONS]['WET_STEP'] = new_step
        self[sec.OPTIONS]['DRY_STEP'] = new_step

    def activate_report(self, input=False, continuity=True, flowstats=True, controls=False):
        # r = self[S.REPORT]  # type: ReportSection
        # r.INPUT = input
        # r.CONTINUITY = continuity
        # r.FLOWSTATS = flowstats
        # r.CONTROLS = controls
        self[sec.REPORT]['INPUT'] = input
        self[sec.REPORT]['CONTINUITY'] = continuity
        self[sec.REPORT]['FLOWSTATS'] = flowstats
        self[sec.REPORT]['CONTROLS'] = controls

    def add_obj_to_report(self, obj_kind, new_obj):
        if isinstance(new_obj, str):
            new_obj = [new_obj]
        elif isinstance(new_obj, list):
            pass
        else:
            raise NotImplementedError('Type: {} not implemented!'.format(type(new_obj)))

        old_obj = self[sec.REPORT][obj_kind]
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

        self[sec.REPORT][obj_kind] = old_obj + new_obj

    def add_nodes_to_report(self, new_nodes):
        self.add_obj_to_report('NODES', new_nodes)

    def add_links_to_report(self, new_links):
        self.add_obj_to_report('LINKS', new_links)

    def add_timeseries_file(self, fn):  # TODO
        if 'Files' not in self[sec.TIMESERIES]:
            self[sec.TIMESERIES]['Files'] = DataFrame(columns=['Type', 'Fname'])

        self[sec.TIMESERIES]['Files'] = self[sec.TIMESERIES]['Files'].append(
            Series({'Fname': '"' + fn + '.dat"'}, name=path.basename(fn)))
        self[sec.TIMESERIES]['Files']['Type'] = 'FILE'

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



def combined_subcatchment_infos(inp):
    return inp[sec.SUBCATCHMENTS].frame.join(inp[sec.SUBAREAS].frame).join(inp[sec.INFILTRATION].frame)


def find_node(inp, label):
    for kind in [sec.JUNCTIONS, sec.OUTFALLS, sec.DIVIDERS, sec.STORAGE]:
        if (kind in inp) and (label in inp[kind]):
            return inp[kind][label]


def find_link(inp, label):
    for kind in [sec.CONDUITS, sec.PUMPS, sec.ORIFICES, sec.WEIRS, sec.OUTLETS]:
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

    for kind in [sec.JUNCTIONS, sec.OUTFALLS, sec.DIVIDERS, sec.STORAGE]:
        if (kind in inp) and (node in inp[kind]):
            inp[kind].pop(node)
    inp[sec.COORDINATES].pop(node)

    # delete connected links
    for i_name, i in inp[sec.CONDUITS].copy().items():
        if (i.ToNode == node) or (i.FromNode == node):
            # print('DELETE (link): ', i_name)
            inp[sec.CONDUITS].pop(i_name)
            inp[sec.XSECTIONS].pop(i_name)
            inp[sec.VERTICES].pop(i_name)

    return inp


def combine_conduits(inp, c1, c2):
    if isinstance(c1, str):
        c1 = inp[sec.CONDUITS][c1]
    if isinstance(c2, str):
        c2 = inp[sec.CONDUITS][c2]

    c_new = c2.copy()
    c_new.Length += c1.Length

    v_new = inp[sec.VERTICES][c1.Name] + inp[sec.VERTICES][c2.Name]

    xs_new = inp[sec.XSECTIONS][c2.Name]

    if c1.FromNode == c2.ToNode:
        c_new.ToNode = c1.ToNode
        inp = delete_node(inp, c2.ToNode)

    elif c1.ToNode == c2.FromNode:
        c_new.FromNode = c1.FromNode
        inp = delete_node(inp, c2.FromNode)
    else:
        raise EnvironmentError('Links not connected')

    inp[sec.VERTICES][c_new.Name] = v_new
    inp[sec.CONDUITS].append(c_new)
    inp[sec.XSECTIONS].append(xs_new)
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
        for i, c in inp[sec.CONDUITS].items():
            if c.FromNode == node:
                conduit = c

                node = conduit.ToNode
                yield conduit
                found = True
                break
        if not found or (node is not None and (node == end)):
            break


def junction_to_storage(inp, label, *args, **kwargs):
    j = inp[sec.JUNCTIONS].pop(label)  # type: S.Junction
    if sec.STORAGE not in inp:
        inp[sec.STORAGE] = InpSection(Storage)
    inp[sec.STORAGE].append(Storage(Name=label, Elevation=j.Elevation, MaxDepth=j.MaxDepth,
                                    InitDepth=j.InitDepth, Apond=j.Aponded, *args, **kwargs))


def junction_to_outfall(inp, label, *args, **kwargs):
    j = inp[sec.JUNCTIONS].pop(label)  # type: S.Junction
    if sec.OUTFALLS not in inp:
        inp[sec.OUTFALLS] = InpSection(Outfall)
    inp[sec.OUTFALLS].append(Outfall(Name=label, Elevation=j.Elevation, *args, **kwargs))


def remove_empty_sections(inp):
    new_inp = inp.copy()
    for section in new_inp:
        if not new_inp[section]:
            del new_inp[section]
    return new_inp


def reduce_curves(inp):
    """
    get used CURVES from [STORAGE, OUTLETS, PUMPS and XSECTIONS] and keep only used curves in the section

    Args:
        inp (InpData): input file data

    Returns:
        InpData: input file data with filtered CURVES section
    """
    if sec.CURVES not in inp:
        return inp
    used_curves = set()
    for section in [sec.STORAGE, sec.OUTLETS, sec.PUMPS, sec.XSECTIONS]:
        used_curves |= {inp[section][name].Curve for name in inp[section]}
    inp[sec.CURVES] = inp[sec.CURVES].filter_keys(used_curves)
    return inp


def reduce_raingages(inp):
    """
    get used RAINGAGES from SUBCATCHMENTS and keep only used raingages in the section

    Args:
        inp (InpData): input file data

    Returns:
        InpData: input file data with filtered RAINGAGES section
    """
    if sec.SUBCATCHMENTS not in inp or sec.RAINGAGES not in inp:
        return inp
    needed_raingages = {inp[sec.SUBCATCHMENTS][s].RainGage for s in inp[sec.SUBCATCHMENTS]}
    inp[sec.RAINGAGES] = inp[sec.RAINGAGES].filter_keys(needed_raingages)
    return inp


def filter_nodes(inp, final_nodes):
    inp_new = inp.copy()
    for section in [sec.JUNCTIONS,
                    sec.OUTFALLS,
                    sec.STORAGE,
                    sec.COORDINATES]:  # ignoring dividers
        if section in inp_new:
            inp_new[section] = inp_new[section].filter_keys(final_nodes)

    # __________________________________________
    for section in [sec.INFLOWS, sec.DWF]:
        if section in inp_new:
            inp_new[section] = inp_new[section].filter_keys(final_nodes, by=IDENTIFIERS.Node)

    # __________________________________________
    if sec.TAGS in inp_new:
        inp_new[sec.TAGS] = inp_new[sec.TAGS].filter_keys(final_nodes, which=TagsSection.TYPES.Node)

    # __________________________________________
    inp_new = remove_empty_sections(inp_new)
    return inp_new


def filter_links(inp_original, final_nodes):
    inp = inp_original.copy()
    # __________________________________________
    final_links = list()
    for section in [sec.CONDUITS,
                    sec.PUMPS,
                    sec.ORIFICES,
                    sec.WEIRS,
                    sec.OUTLETS]:
        if section not in inp:
            continue
        new_section = InpSection(inp[section].index)
        for name, thing in inp[section].items():
            if thing.ToNode in final_nodes:
                new_section.append(thing)
                final_links.append(name)

        if new_section.empty:
            del inp[section]
        else:
            inp[section] = new_section

    # __________________________________________
    for section in [sec.XSECTIONS, sec.LOSSES]:
        if section not in inp:
            continue
        new_section = InpSection(inp[section].index)
        for name, thing in inp[section].items():
            if thing.Link in final_links:
                new_section.append(thing)

        if new_section.empty:
            del inp[section]
        else:
            inp[section] = new_section

    # __________________________________________
    # section_filter[TAGS],  # node und link
    if sec.TAGS in inp:
        old_tags = inp[sec.TAGS][TagsSection.TYPES.Link].copy()
        for name in old_tags:
            if name not in final_links:
                inp[sec.TAGS][TagsSection.TYPES.Link].pop(name)

    # __________________________________________
    if sec.VERTICES in inp:
        new_verticies = list()
        for line in inp[sec.VERTICES]:
            name = line[0]
            if name in final_links:
                new_verticies.append(line)
        inp[sec.VERTICES] = new_verticies

    return inp


def filter_subcatchments(inp_original, final_nodes):
    inp = inp_original.copy()

    # __________________________________________
    for section in [sec.SUBCATCHMENTS]:
        if section not in inp:
            continue
        new_section = InpSection(inp[section].index)
        for name, thing in inp[section].items():
            if thing.Outlet in final_nodes:
                new_section.append(thing)

        if new_section.empty:
            del inp[section]
        else:
            inp[section] = new_section

    # __________________________________________
    for section in [sec.SUBAREAS, sec.INFILTRATION]:
        if section not in inp:
            continue
        new_section = InpSection(inp[section].index)
        for name, thing in inp[section].items():
            if thing.subcatchment in inp[sec.SUBCATCHMENTS]:
                new_section.append(thing)

        if new_section.empty:
            del inp[section]
        else:
            inp[section] = new_section

    # __________________________________________
    # section_filter[TAGS],  # node und link
    if sec.TAGS in inp:
        old_tags = inp[sec.TAGS][TagsSection.TYPES.Subcatch].copy()
        for name in old_tags:
            if name not in inp[sec.SUBCATCHMENTS]:
                inp[sec.TAGS][TagsSection.TYPES.Link].pop(name)

    # __________________________________________
    if sec.POLYGONS in inp:
        new_poly = list()
        for line in inp[sec.POLYGONS]:
            name = line[0]
            if name in inp[sec.SUBCATCHMENTS]:
                new_poly.append(line)
        inp[sec.POLYGONS] = new_poly

    return inp
