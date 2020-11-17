from collections import ChainMap
from os import path, mkdir, listdir

import numpy as np

from .inp_helpers import InpData, InpSection
from .inp_reader import read_inp_file, convert_section
from .inp_sections import *
from .inp_sections import labels as sec
from .inp_sections.identifiers import IDENTIFIERS
from .inp_sections.labels import VERTICES, COORDINATES
from .inp_sections.types import SECTION_TYPES
from .inp_writer import section_to_string
from .macro_snippets.curve_simplification import ramer_douglas, _vec2d_dist

"""
a collection of macros to manipulate an inp-file

use this file as an example for the usage of this package
"""


def section_from_frame(df, section_class):
    """
    create a inp-file section from an pandas DataFrame

    Args:
        df (pandas.DataFrame): data
        section_class (BaseSectionObject):

    Returns:
        InpSection: converted section
    """
    # TODO: macro_snippets
    values = np.vstack((df.index.values, df.values.T)).T
    return section_class.create_section(values)
    # return cls.from_lines([line.split() for line in dataframe_to_inp_string(df).split('\n')], section_class)


def split_inp_to_files(inp_fn, convert_sections=[], **kwargs):
    """
    spit an inp-file into the sections and write per section one file

    creates a subdirectory in the directory of the input file with the name of the input file (without ``.inp``)
    and creates for each section a ``.txt``-file

    Args:
        inp_fn (str): path to inp-file
        convert_sections (list): only convert these sections. Default: convert no section
        **kwargs: keyword arguments of the :func:`~swmm_api.input_file.inp_reader.read_inp_file`-function

    Keyword Args:
        ignore_sections (list[str]): don't convert ignored sections. Default: ignore none.
        custom_converter (dict): dictionary of {section: converter/section_type} Default: :const:`SECTION_TYPES`
        ignore_gui_sections (bool): don't convert gui/geo sections (ie. for commandline use)
    """
    parent = inp_fn.replace('.inp', '')
    mkdir(parent)
    inp = read_inp_file(inp_fn, convert_sections=convert_sections, **kwargs)
    for s in inp.keys():
        with open(path.join(parent, s + '.txt'), 'w') as f:
            f.write(section_to_string(inp[s], fast=False))


def read_split_inp_file(inp_fn):
    """
    use this function to read an split inp-file after splitting the file with the :func:`~split_inp_to_files`-function

    Args:
        inp_fn (str): path of the directory of the split inp-file

    Returns:
        InpData: inp-file data
    """
    inp = InpData()
    for header_file in listdir(inp_fn):
        header = header_file.replace('.txt', '')
        with open(path.join(inp_fn, header_file), 'r') as f:
            inp[header] = convert_section(header, f.read(), SECTION_TYPES)

    return inp


def combined_subcatchment_frame(inp):
    """
    combine all information of the subcatchment data-frames

    Args:
        inp (InpData): inp-file data

    Returns:
        pandas.DataFrame: combined subcatchment data
    """
    return inp[sec.SUBCATCHMENTS].frame.join(inp[sec.SUBAREAS].frame).join(inp[sec.INFILTRATION].frame)


def find_node(inp, node_label):
    """
    find node in inp-file data

    Args:
        inp (InpData): inp-file data
        node_label (str): node Name/label

    Returns:
        Junction or Storage or Outfall: searched node (if not found None)
    """
    nodes = nodes_dict(inp)
    if node_label in nodes:
        return nodes[node_label]


def nodes_dict(inp):
    nodes = ChainMap()
    for section in [sec.JUNCTIONS, sec.OUTFALLS, sec.DIVIDERS, sec.STORAGE]:
        if section in inp:
            nodes.maps.append(inp[section])
    return nodes


def links_dict(inp):
    links = ChainMap()
    for section in [sec.CONDUITS, sec.PUMPS, sec.ORIFICES, sec.WEIRS, sec.OUTLETS]:
        if section in inp:
            links.maps.append(inp[section])
    return links


def find_link(inp, label):
    """
    find link in inp-file data

    Args:
        inp (InpData): inp-file data
        label (str): link Name/label

    Returns:
        Conduit | Weir | Outlet | Orifice | Pump: searched link (if not found None)
    """
    links = links_dict(inp)
    if label in links:
        return links[label]


def calc_slope(inp, link):
    """
    calculate the slop of a link

    Args:
        inp (InpData): inp-file data
        link (Conduit | Weir | Outlet | Orifice | Pump): link

    Returns:
        float: slop of the link
    """
    return (find_node(inp, link.FromNode).Elevation - find_node(inp, link.ToNode).Elevation) / link.Length


def delete_node(inp, node):
    """
    delete node in inp data

    Args:
        inp (InpData): inp data
        node (str | Junction | Storage | Outfall): node to delete

    Returns:
        InpData: inp data
    """
    # print('DELETE (node): ', node)
    if isinstance(node, str):
        n = find_node(inp, node)
    else:
        n = node
        node = n.Name

    for section in [sec.JUNCTIONS, sec.OUTFALLS, sec.DIVIDERS, sec.STORAGE, sec.COORDINATES]:
        if (section in inp) and (node in inp[section]):
            inp[section].pop(node)

    # delete connected links
    for link in inp[sec.CONDUITS].keys().copy():
        if (inp[sec.CONDUITS][link].ToNode == node) or (inp[sec.CONDUITS][link].FromNode == node):
            # print('DELETE (link): ', link)
            inp[sec.CONDUITS].pop(link)
            inp[sec.XSECTIONS].pop(link)
            inp[sec.VERTICES].pop(link)

    return inp


def combine_conduits(inp, c1, c2, keep_first=True):
    """
    combine the two conduits to one

    Args:
        inp (InpData): inp data
        c1 (str | Conduit): conduit 1 to combine
        c2 (str | Conduit): conduit 2 to combine
        keep_first (bool): keep first (of conduit 1) cross-section; else use second (of conduit 2)

    Returns:
        InpData: inp data
    """
    if isinstance(c1, str):
        c1 = inp[sec.CONDUITS][c1]
    if isinstance(c2, str):
        c2 = inp[sec.CONDUITS][c2]

    c_new = c2.copy()  # type: Conduit
    c_new.Length += c1.Length

    # vertices + Coord of middle node
    v_new = inp[sec.VERTICES][c1.Name].vertices + inp[sec.VERTICES][c2.Name].vertices

    # Loss
    if sec.LOSSES in inp and c_new.Name in inp[sec.LOSSES]:
        pass

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


def dissolve_node(inp, node):
    """
    delete node and combine conduits

    Args:
        inp (InpData): inp data
        node (str | Junction | Storage | Outfall): node to delete

    Returns:
        InpData: inp data
    """
    if isinstance(node, str):
        node = find_node(inp, node)
    # create new section with only
    c1 = inp[sec.CONDUITS].filter_keys([node.Name], 'ToNode')
    if c1:
        c2 = inp[sec.CONDUITS].filter_keys([node.Name], 'FromNode')
        inp = combine_conduits(inp, c1, c2)
    else:
        inp = delete_node(node.Name)
    return inp


def conduit_iter_over_inp(inp, start, end=None):
    """
    iterate of the inp-file data

    only correct when FromNode and ToNode are in the correct direction
    doesn't look backwards if split node

    Args:
        inp (InpData): inp-file data
        start (str): start node label
        end (str): end node label

    Yields:
        Conduit: input conduits
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
    """
    convert :class:`~swmm_api.input_file.inp_sections.node.Junction` to :class:`~swmm_api.input_file.inp_sections.node.Storage`
    and add it to the STORAGE section

    Args:
        inp (InpData): inp-file data
        label (str): label of the junction
        *args: argument of the :class:`~swmm_api.input_file.inp_sections.node.Storage`-class
        **kwargs: keyword arguments of the :class:`~swmm_api.input_file.inp_sections.node.Storage`-class
    """
    j = inp[sec.JUNCTIONS].pop(label)  # type: Junction
    if sec.STORAGE not in inp:
        inp[sec.STORAGE] = InpSection(Storage)
    inp[sec.STORAGE].append(Storage(Name=label, Elevation=j.Elevation, MaxDepth=j.MaxDepth,
                                    InitDepth=j.InitDepth, Apond=j.Aponded, *args, **kwargs))


def junction_to_outfall(inp, label, *args, **kwargs):
    """
    convert :class:`~swmm_api.input_file.inp_sections.node.Junction` to :class:`~swmm_api.input_file.inp_sections.node.Outfall`
    and add it to the OUTFALLS section

    Args:
        inp (InpData): inp-file data
        label (str): label of the junction
        *args: argument of the :class:`~swmm_api.input_file.inp_sections.node.Outfall`-class
        **kwargs: keyword arguments of the :class:`~swmm_api.input_file.inp_sections.node.Outfall`-class
    """
    j = inp[sec.JUNCTIONS].pop(label)  # type: Junction
    if sec.OUTFALLS not in inp:
        inp[sec.OUTFALLS] = Outfall.create_section()
    inp[sec.OUTFALLS].append(Outfall(Name=label, Elevation=j.Elevation, *args, **kwargs))


def rename_node(label, new_label):
    # TODO !!
    pass


def rename_link(label, new_label):
    # TODO !!
    pass


def remove_empty_sections(inp):
    """
    remove empty inp-file data sections

    Args:
        inp (InpData): inp-file data

    Returns:
        InpData: cleaned inp-file data
    """
    new_inp = InpData()
    for section in inp:
        if inp[section]:
            new_inp[section] = inp[section]
    return new_inp


def reduce_curves(inp):
    """
    get used CURVES from [STORAGE, OUTLETS, PUMPS and XSECTIONS] and keep only used curves in the section

    Args:
        inp (InpData): inp-file data

    Returns:
        InpData: inp-file data with filtered CURVES section
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


def simplify_curves(curve_section, dist=0.001):
    """
    simplify curves with the algorithm by Ramer and Douglas

    Args:
        curve_section (InpSection[Curve]): old section
        dist (float): maximum Ramer-Douglas distance

    Returns:
        InpSection[Curve]: new section
    """
    new = Curve.create_section()
    for label, curve in curve_section.items():
        new[label] = Curve(curve.Name, curve.Type, points=ramer_douglas(curve_section[label].points, dist=dist))
    return new


def reduce_raingages(inp):
    """
    get used RAINGAGES from SUBCATCHMENTS and keep only used raingages in the section

    Args:
        inp (InpData):  inp-file data

    Returns:
        InpData: inp-file data with filtered RAINGAGES section
    """
    if sec.SUBCATCHMENTS not in inp or sec.RAINGAGES not in inp:
        return inp
    needed_raingages = {inp[sec.SUBCATCHMENTS][s].RainGage for s in inp[sec.SUBCATCHMENTS]}
    inp[sec.RAINGAGES] = inp[sec.RAINGAGES].filter_keys(needed_raingages)
    return inp


def filter_nodes(inp, final_nodes):
    """
     filter nodes in the network

    Args:
        inp (InpData): inp-file data
        final_nodes (list | set):

    Returns:
        InpData: new inp-file data
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
        inp (InpData): inp-file data
        final_nodes (list | set):

    Returns:
        InpData: new inp-file data
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
            inp[section] = inp[section].filter_keys(final_links)

    # __________________________________________
    if sec.TAGS in inp:
        inp[sec.TAGS] = inp[sec.TAGS].filter_keys(final_links, which=TagsSection.TYPES.Link)

    # __________________________________________
    inp = remove_empty_sections(inp)

    return inp


def filter_subcatchments(inp, final_nodes):
    """
    filter subcatchments by nodes in the network

    Args:
        inp (InpData): inp-file data
        final_nodes (list | set):

    Returns:
        InpData: new inp-file data
    """
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


def group_edit(inp):
    # for objects of type (Subcatchments, Infiltration, Junctions, Storage Units, or Conduits)
    # with tag equal to
    # edit the property
    # by replacing it with
    pass


def add_coordinates_to_vertices(inp):
    links = links_dict(inp)

    for label, link in links.items():
        inner_vertices = list()
        if label in VERTICES:
            inner_vertices = inp[VERTICES][label].vertices

        yield label, [inp[COORDINATES][link.FromNode].point] + inner_vertices + [inp[COORDINATES][link.ToNode].point]


def update_vertices(inp):
    links = links_dict(inp)
    coords = inp[COORDINATES]
    for l in links.values():  # type: Conduit # or Weir or Orifice or Pump or Outlet
        v = list()
        if l.Name in VERTICES:
            v = inp[VERTICES][l.Name].vertices
        inp[VERTICES][l.Name].vertices = [coords[l.FromNode].point] + v + [coords[l.ToNode].point]
    return inp


def reduce_vertices(inp):
    links = links_dict(inp)

    for l in links.values():  # type: Conduit # or Weir or Orifice or Pump or Outlet
        if l.Name in VERTICES:
            v = inp[VERTICES][l.Name].vertices
            p = inp[COORDINATES][l.FromNode].point
            if _vec2d_dist(p, v[0]) < 0.25:
                v = v[1:]

            p = inp[COORDINATES][l.ToNode].point
            if _vec2d_dist(p, v[-1]) < 0.25:
                v = v[:-1]

            inp[VERTICES][l.Name].vertices = v
    return inp


def update_inp(inp, inp_new):
    for sec in inp_new:
        if sec not in inp:
            inp[sec] = inp_new[sec]
        else:
            inp[sec].update(inp_new[sec])
    return inp
