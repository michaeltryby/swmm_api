from os import path, mkdir, listdir

import numpy as np

from .inp_helpers import InpData, InpSection
from .inp_reader import read_inp_file, _convert_sections
from .inp_sections import *
from .inp_sections import labels as sec
from .inp_sections.identifiers import IDENTIFIERS
from .inp_writer import section_to_string

"""
a collection of macros to manipulate an inp-file

use this file as an example for the usage of this package
"""


def section_from_frame(df, section_class):
    # TODO: macro_snippets
    a = np.vstack((df.index.values, df.values.T)).T
    return InpSection.from_inp_lines(a, section_class)
    # return cls.from_lines([line.split() for line in dataframe_to_inp_string(df).split('\n')], section_class)


def split_inp_to_files(inp_fn, **kwargs):
    parent = inp_fn.replace('.inp', '')
    mkdir(parent)
    inp = read_inp_file(inp_fn, **kwargs)
    for s in inp.keys():
        with open(path.join(parent, s + '.txt'), 'w') as f:
            f.write(section_to_string(inp[s], fast=False))


def read_split_inp_file(inp_fn):
    inp = dict()
    for header_file in listdir(inp_fn):
        header = header_file.replace('.txt', '')
        with open(path.join(inp_fn, header_file), 'r') as f:
            inp[header] = f.read()

    inp = InpData(inp)
    inp = _convert_sections(inp)
    return inp


def combined_subcatchment_infos(inp):
    return inp[sec.SUBCATCHMENTS].frame.join(inp[sec.SUBAREAS].frame).join(inp[sec.INFILTRATION].frame)


def find_node(inp, node_label):
    for section in [sec.JUNCTIONS, sec.OUTFALLS, sec.DIVIDERS, sec.STORAGE]:
        if (section in inp) and (node_label in inp[section]):
            return inp[section][node_label]


def find_link(inp, label):
    for section in [sec.CONDUITS, sec.PUMPS, sec.ORIFICES, sec.WEIRS, sec.OUTLETS]:
        if (section in inp) and (label in inp[section]):
            return inp[section][label]


def calc_slope(inp, link):
    return (find_node(inp, link.FromNode).Elevation - find_node(inp, link.ToNode).Elevation) / link.Length


def delete_node(inp, node):
    # print('DELETE (node): ', node)
    if isinstance(node, str):
        n = find_node(inp, node)
    else:
        n = node
        node = n.Name

    for section in [sec.JUNCTIONS, sec.OUTFALLS, sec.DIVIDERS, sec.STORAGE]:
        if (section in inp) and (node in inp[section]):
            inp[section].pop(node)
    inp[sec.COORDINATES].pop(node)

    # delete connected links
    for link in inp[sec.CONDUITS].keys().copy():
        if (inp[sec.CONDUITS][link].ToNode == node) or (inp[sec.CONDUITS][link].FromNode == node):
            # print('DELETE (link): ', link)
            inp[sec.CONDUITS].pop(link)
            inp[sec.XSECTIONS].pop(link)
            inp[sec.VERTICES].pop(link)

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
    j = inp[sec.JUNCTIONS].pop(label)  # type: Junction
    if sec.STORAGE not in inp:
        inp[sec.STORAGE] = InpSection(Storage)
    inp[sec.STORAGE].append(Storage(Name=label, Elevation=j.Elevation, MaxDepth=j.MaxDepth,
                                    InitDepth=j.InitDepth, Apond=j.Aponded, *args, **kwargs))


def junction_to_outfall(inp, label, *args, **kwargs):
    j = inp[sec.JUNCTIONS].pop(label)  # type: Junction
    if sec.OUTFALLS not in inp:
        inp[sec.OUTFALLS] = InpSection(Outfall)
    inp[sec.OUTFALLS].append(Outfall(Name=label, Elevation=j.Elevation, *args, **kwargs))


def remove_empty_sections(inp):
    new_inp = InpData()
    for section in inp:
        if inp[section]:
            new_inp[section] = inp[section]
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
        if section in inp:
            used_curves |= {inp[section][name].Curve for name in inp[section] if
                            isinstance(inp[section][name].Curve, str)}
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
    """

    Args:
        inp ():
        final_nodes ():

    Returns:

    """
    for section in [sec.JUNCTIONS,
                    sec.OUTFALLS,
                    sec.STORAGE,
                    sec.COORDINATES]:  # ignoring dividers
        if section in inp:
            inp[section] = inp[section].filter_keys(final_nodes)

    # __________________________________________
    for section in [sec.INFLOWS, sec.DWF]:
        if section in inp:
            inp[section] = inp[section].filter_keys(final_nodes, by=IDENTIFIERS.Node)

    # __________________________________________
    if sec.TAGS in inp:
        inp[sec.TAGS] = inp[sec.TAGS].filter_keys(final_nodes, which=TagsSection.TYPES.Node)

    # __________________________________________
    inp = remove_empty_sections(inp)
    return inp


def filter_links(inp, final_nodes):
    """
    filter links by nodes in the network

    Args:
        inp (InpData):
        final_nodes (list | set):

    Returns:
        InpData: new input data
    """
    # __________________________________________
    final_links = set()
    for section in [sec.CONDUITS,
                    sec.PUMPS,
                    sec.ORIFICES,
                    sec.WEIRS,
                    sec.OUTLETS]:
        if section in inp:
            inp[section] = inp[section].filter_keys(final_nodes, by=['FromNode', 'ToNode'])
            final_links |= set(inp[section].keys())

    # __________________________________________
    for section in [sec.XSECTIONS, sec.LOSSES, sec.VERTICES]:
        if section in inp:
            inp[section] = inp[section].filter_keys(final_links, by=IDENTIFIERS.Link)

    # __________________________________________
    if sec.TAGS in inp:
        inp[sec.TAGS] = inp[sec.TAGS].filter_keys(final_links, which=TagsSection.TYPES.Link)

    # __________________________________________
    inp = remove_empty_sections(inp)

    return inp


def filter_subcatchments(inp, final_nodes):
    if sec.SUBCATCHMENTS in inp:
        sub_orig = inp[sec.SUBCATCHMENTS].copy()
        # all with an outlet to final_nodes
        inp[sec.SUBCATCHMENTS] = inp[sec.SUBCATCHMENTS].filter_keys(final_nodes, by='Outlet')
        # all with an outlet to an subcatchment
        inp[sec.SUBCATCHMENTS].update(sub_orig.filter_keys(inp[sec.SUBCATCHMENTS].keys(), by='Outlet'))

        # __________________________________________
        for section in [sec.SUBAREAS, sec.INFILTRATION, sec.POLYGONS]:
            if section in inp:
                inp[section] = inp[section].filter_keys(inp[sec.SUBCATCHMENTS])

        # __________________________________________
        if sec.TAGS in inp:
            inp[sec.TAGS] = inp[sec.TAGS].filter_keys(inp[sec.SUBCATCHMENTS], which=TagsSection.TYPES.Subcatch)

    else:
        for section in [sec.SUBAREAS, sec.INFILTRATION, sec.POLYGONS]:
            if section in inp:
                del inp[section]

        if sec.TAGS in inp and TagsSection.TYPES.Subcatch in inp[sec.TAGS]:
            del inp[sec.TAGS][TagsSection.TYPES.Subcatch]

    # __________________________________________
    inp = remove_empty_sections(inp)
    return inp
