from collections import ChainMap
from math import ceil
import os
import numpy as np
import pandas as pd
from networkx import DiGraph, all_simple_paths, subgraph, node_connected_component, Graph
from statistics import mean
from typing import List
from itertools import product

from ._type_converter import is_equal
from .helpers import InpSection, convert_section, section_to_string, BaseSectionObject, _sort_by
from . import SwmmInput, section_labels as sec
from .sections import *
from .sections._identifiers import IDENTIFIERS
from .section_labels import VERTICES, COORDINATES, XSECTIONS
from .section_types import SECTION_TYPES
from .macro_snippets.curve_simplification import ramer_douglas, _vec2d_dist
from .sections.link import _Link
from .sections.node import _Node

"""
a collection of macros to manipulate an inp-file

use this file as an example for the usage of this package
"""


def section_from_frame(df, section_class):
    """
    create a inp-file section from an pandas DataFrame

    will only work for specific sections ie. JUNCTIONS where every row is the same and no special __init__ is needed!

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


########################################################################################################################
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
    os.mkdir(parent)
    inp = SwmmInput.read_file(inp_fn, convert_sections=convert_sections, **kwargs)
    for s in inp.keys():
        with open(os.path.join(parent, s + '.txt'), 'w') as f:
            f.write(section_to_string(inp[s], fast=False))


def read_split_inp_file(inp_fn):
    """
    use this function to read an split inp-file after splitting the file with the :func:`~split_inp_to_files`-function

    Args:
        inp_fn (str): path of the directory of the split inp-file

    Returns:
        SwmmInput: inp-file data
    """
    inp = SwmmInput()
    for header_file in os.listdir(inp_fn):
        header = header_file.replace('.txt', '')
        with open(os.path.join(inp_fn, header_file), 'r') as f:
            inp[header] = convert_section(header, f.read(), SECTION_TYPES)

    return inp


########################################################################################################################
def combined_subcatchment_frame(inp: SwmmInput):
    """
    combine all information of the subcatchment data-frames

    Args:
        inp (SwmmInput): inp-file data

    Returns:
        pandas.DataFrame: combined subcatchment data
    """
    df = inp[sec.SUBCATCHMENTS].frame.join(inp[sec.SUBAREAS].frame).join(inp[sec.INFILTRATION].frame)
    df = df.join(get_subcatchment_tags(inp))
    return df


########################################################################################################################
def _get_tags_frame(inp, part=None):
    if sec.TAGS in inp:
        df_tags = inp[sec.TAGS].frame
        if part in df_tags.index.levels[0]:
            return inp[sec.TAGS].frame.xs(part, axis=0, level=0)
    return pd.Series(name='tags', dtype=str)


def get_node_tags(inp):
    """
    get node tags as pandas.Series

    Args:
        inp (SwmmInput): inp data

    Returns:
        pandas.Series: node tags
    """
    return _get_tags_frame(inp, Tag.TYPES.Node)


def get_link_tags(inp):
    """
    get node link as pandas.Series

    Args:
        inp (SwmmInput): inp data

    Returns:
        pandas.Series: link tags
    """
    return _get_tags_frame(inp, Tag.TYPES.Link)


def get_subcatchment_tags(inp):
    """
    get subcatchment tags as pandas.Series

    Args:
        inp (SwmmInput): inp data

    Returns:
        pandas.Series: subcatchment tags
    """
    return _get_tags_frame(inp, Tag.TYPES.Subcatch)


########################################################################################################################
def filter_tags(inp_tags: SwmmInput, inp_objects: SwmmInput=None):
    """
    get tags of one inp data for objects of another inp data and create new section

    Args:
        inp_tags (SwmmInput): inp data where all tags are
        inp_objects (SwmmInput): inp data of the needed objects

    Returns:
        InpSection[str, Tag] | dict[str, Tag]:
    """
    if inp_objects is None:
        inp_objects = inp_tags

    nodes = nodes_dict(inp_objects)
    keys = list(product([Tag.TYPES.Node], list(nodes.keys())))

    links = links_dict(inp_objects)
    keys += list(product([Tag.TYPES.Link], list(links.keys())))

    if sec.SUBCATCHMENTS in inp_objects:
        keys += list(product([Tag.TYPES.Subcatch], list(inp_objects.SUBCATCHMENTS.keys())))

    return inp_tags.TAGS.slice_section(keys)


########################################################################################################################
def nodes_dict(inp: SwmmInput):
    """
    get a dict of all nodes

    the objects are referenced, so you can use it to modify too.

    Args:
        inp (SwmmInput): inp-file data

    Returns:
        dict[str, _Node]: dict of {labels: objects}
    """
    nodes: ChainMap[str, _Node] = ChainMap()
    for section in [sec.JUNCTIONS, sec.OUTFALLS, sec.DIVIDERS, sec.STORAGE]:
        if section in inp:
            nodes.maps.append(inp[section])
    return nodes


def find_node(inp: SwmmInput, node_label):
    """
    find node in inp-file data

    Args:
        inp (SwmmInput): inp-file data
        node_label (str): node Name/label

    Returns:
        Junction or Storage or Outfall: searched node (if not found None)
    """
    nodes = nodes_dict(inp)
    if node_label in nodes:
        return nodes[node_label]


def links_dict(inp: SwmmInput):  # or Weir or Orifice or Pump or Outlet
    """
    get a dict of all links

    the objects are referenced, so you can use it to modify too.

    Args:
        inp (SwmmInput): inp-file data

    Returns:
        dict[str, _Link]: dict of {labels: objects}
    """
    links: ChainMap[str, _Link] = ChainMap()
    for section in [sec.CONDUITS, sec.PUMPS, sec.ORIFICES, sec.WEIRS, sec.OUTLETS]:
        if section in inp:
            links.maps.append(inp[section])
    return links


def find_link(inp: SwmmInput, label):
    """
    find link in inp-file data

    Args:
        inp (SwmmInput): inp-file data
        label (str): link Name/label

    Returns:
        Conduit | Weir | Outlet | Orifice | Pump: searched link (if not found None)
    """
    links = links_dict(inp)
    if label in links:
        return links[label]


########################################################################################################################
def calc_slope(inp: SwmmInput, conduit):
    """
    calculate the slop of a conduit

    Args:
        inp (SwmmInput): inp-file data
        conduit (Conduit): link

    Returns:
        float: slop of the link
    """
    nodes = nodes_dict(inp)
    return (nodes[conduit.FromNode].Elevation + conduit.InOffset - (
            nodes[conduit.ToNode].Elevation + conduit.OutOffset)) / conduit.Length


def conduit_slopes(inp: SwmmInput):
    """
    get the slope of all conduits

    Args:
        inp (SwmmInput):

    Returns:
        pandas.Series: slopes
    """
    slopes = dict()
    for conduit in inp.CONDUITS.values():
        slopes[conduit.Name] = calc_slope(inp, conduit)
    return pd.Series(slopes)


def _rel_diff(a, b):
    m = mean([a + b])
    if m == 0:
        return abs(a - b)
    return abs(a - b) / m


def _rel_slope_diff(inp: SwmmInput, l0, l1):
    nodes = nodes_dict(inp)
    slope_res = (nodes[l0.FromNode].Elevation + l0.InOffset
                 - (nodes[l1.ToNode].Elevation + l1.OutOffset)
                 ) / (l0.Length + l1.Length)
    return _rel_diff(calc_slope(inp, l0), slope_res)


"""PCSWMM Simplify network tool 
Criteria

The criteria is a list of attributes and a given tolerance for each. Attribute criteria can be toggled on or off 
by checking the box next to the attribute. The attribute criteria are as follows:

    Cross-section shapes must match exactly
    Diameter values match within a specified percent tolerance
    Roughness values match within a specified percent tolerance
    Slope values match within a specified tolerance
    Transects must match exactly
    Shape curves must match exactly

Join preference

Select a preference for joining two conduits. The preference is used when two conduits are available for 
connecting on the upstream and downstream nodes. Choose the priority for the connection to be any one of the 
following:

    shorter conduit
    longer conduit
    closest slope
    upstream conduit
    downstream conduit
"""


def conduits_are_equal(inp: SwmmInput, link0, link1, diff_roughness=0.1, diff_slope=0.1, diff_height=0.1):
    """
    check if the links (with all there components) are equal

    Args:
        inp (SwmmInput):
        link0 (Conduit | Weir | Outlet | Orifice | Pump | _Link): first link
        link1 (Conduit | Weir | Outlet | Orifice | Pump | _Link): second link
        diff_roughness (float): difference from which it is considered different.
        diff_slope (float): difference from which it is considered different.
        diff_height (float): difference from which it is considered different.

    Returns:
        bool: if the links are equal
    """
    all_checks_out = True

    # Roughness values match within a specified percent tolerance
    if diff_roughness is not None:
        all_checks_out &= _rel_diff(link0.Roughness, link1.Roughness) < diff_roughness

    xs0 = inp[sec.XSECTIONS][link0.Name]  # type: CrossSection
    xs1 = inp[sec.XSECTIONS][link1.Name]  # type: CrossSection

    # Diameter values match within a specified percent tolerance (1 %)
    if diff_height is not None:
        all_checks_out &= _rel_diff(xs0.Geom1, xs1.Geom1) < diff_height

    # Cross-section shapes must match exactly
    all_checks_out &= xs0.Shape == xs1.Shape

    # Shape curves must match exactly
    if xs0.Shape == CrossSection.SHAPES.CUSTOM:
        all_checks_out &= xs0.Curve == xs1.Curve

    # Transects must match exactly
    elif xs0.Shape == CrossSection.SHAPES.IRREGULAR:
        all_checks_out &= xs0.Tsect == xs1.Tsect

    # Slope values match within a specified tolerance
    if diff_slope is not None:
        rel_slope_diff = _rel_diff(calc_slope(inp, link0), calc_slope(inp, link1))

        # if rel_slope_diff < 0:
        #     nodes = nodes_dict(inp)
        #     print(nodes[link0.FromNode].Elevation, link0.InOffset, nodes[link0.ToNode].Elevation, link0.OutOffset)
        #     print(nodes[link1.FromNode].Elevation, link1.InOffset, nodes[link1.ToNode].Elevation, link1.OutOffset)
        #     print('rel_slope_diff < 0', link0, link1)
        all_checks_out &= rel_slope_diff < diff_slope

    return all_checks_out


def delete_node(inp: SwmmInput, node_label, graph: DiGraph = None, alt_node=None):
    """
    delete node in inp data

    Notes:
        works inplace

    Args:
        inp (SwmmInput): inp data
        node_label (str): label of node to delete
        graph (DiGraph): networkx graph of model
        alt_node (str): node label | optional: move flows to this node

    Returns:
        SwmmInput: inp data
    """
    for section in [sec.JUNCTIONS, sec.OUTFALLS, sec.DIVIDERS, sec.STORAGE, sec.COORDINATES]:
        if (section in inp) and (node_label in inp[section]):
            inp[section].pop(node_label)

    # AND delete connected links
    if graph is not None:
        if node_label in graph:
            links = next_links_labels(graph, node_label) + previous_links_labels(graph, node_label)  # type: List[str]
            graph.remove_node(node_label)
        else:
            links = list()
    else:
        links = list()
        for section in [sec.CONDUITS, sec.PUMPS, sec.ORIFICES, sec.WEIRS, sec.OUTLETS]:
            if section in inp:
                links += list(inp[section].filter_keys([node_label], by='FromNode')) + \
                         list(inp[section].filter_keys([node_label], by='ToNode'))  # type: List[Conduit]
        links = [l.Name for l in links]  # type: List[str]

    for link in links:
        delete_link(inp, link)

    if alt_node is not None:
        move_flows(inp, node_label, alt_node)

    return inp


def move_flows(inp, from_node, to_node, only_constituent=None):
    """
    move flow (INFLOWS or DWF) from one node to another

    Args:
        inp (SwmmInput): inp data
        from_node (str): first node label
        to_node (str): second node label
        only_constituent (list): only consider this constituent (default: FLOW)

    Notes:
        works inplace
    """
    for section in (sec.INFLOWS, sec.DWF):
        if section not in inp:
            continue
        if only_constituent is None:
            only_constituent = [DryWeatherFlow.TYPES.FLOW]
        for t in only_constituent:
            index_old = (from_node, t)
            if index_old in inp[section]:
                index_new = (to_node, t)

                if section == sec.DWF:
                    old = inp[section].pop(index_old)
                    if index_new in inp[section]:
                        new = inp[section][index_new]
                        new.Base += old.Base

                        # if not all([old[p] == new[p] for p in ['pattern1', 'pattern2', 'pattern3', 'pattern4']]):
                        #     print(f'WARNING: move_flows  from "{from_node}" to "{to_node}". DWF patterns don\'t
                        #     match!')

                    else:
                        inp[section][index_new] = old
                        inp[section][index_new].Node = to_node

                elif index_new in inp[section]:
                    print(f'WARNING: move_flows  from "{from_node}" to "{to_node}". Already Exists!')

                else:
                    inp[section][index_new] = inp[section].pop(index_old)
                    inp[section][index_new].Node = to_node
            else:
                print(f'Nothing to move from "{from_node}" [{section}]')


def delete_link(inp: SwmmInput, link):
    for s in [sec.CONDUITS, sec.PUMPS, sec.ORIFICES, sec.WEIRS, sec.OUTLETS, sec.XSECTIONS, sec.LOSSES, sec.VERTICES]:
        if (s in inp) and (link in inp[s]):
            inp[s].pop(link)


def delete_subcatchment(inp: SwmmInput, subcatchment):
    for s in [sec.SUBCATCHMENTS, sec.SUBAREAS, sec.INFILTRATION, sec.POLYGONS, sec.LOADINGS, sec.COVERAGES]:
        if (s in inp) and (subcatchment in inp[s]):
            inp[s].pop(subcatchment)


def split_conduit(inp, conduit, intervals=None, length=None, from_inlet=True):
    # mode = [cut_point (GUI), intervals (n), length (l)]
    nodes = nodes_dict(inp)
    if isinstance(conduit, str):
        conduit = inp[sec.CONDUITS][conduit]  # type: Conduit

    dx = 0
    n_new_nodes = 0
    if intervals:
        dx = conduit.Length / intervals
        n_new_nodes = intervals - 1
    elif length:
        dx = length
        n_new_nodes = ceil(conduit.Length / length - 1)

    from_node = nodes[conduit.FromNode]
    to_node = nodes[conduit.ToNode]

    from_node_coord = inp[sec.COORDINATES][from_node.Name]
    to_node_coord = inp[sec.COORDINATES][to_node.Name]

    loss = None
    if (sec.LOSSES in inp) and (conduit.Name in inp[sec.LOSSES]):
        loss = inp[sec.LOSSES][conduit.Name]  # type: Loss

    new_nodes = list()
    new_links = list()

    x = dx
    last_node = from_node
    for new_node_i in range(n_new_nodes + 1):
        if x >= conduit.Length:
            node = to_node
        else:
            node = Junction(Name=f'{from_node.Name}_{to_node.Name}_{chr(new_node_i + 97)}',
                            Elevation=np.interp(x, [0, conduit.Length], [from_node.Elevation, to_node.Elevation]),
                            MaxDepth=np.interp(x, [0, conduit.Length], [from_node.MaxDepth, to_node.MaxDepth]),
                            InitDepth=np.interp(x, [0, conduit.Length], [from_node.InitDepth, to_node.InitDepth]),
                            SurDepth=np.interp(x, [0, conduit.Length], [from_node.SurDepth, to_node.SurDepth]),
                            Aponded=float(np.mean([from_node.Aponded, to_node.Aponded])),
                            )
            new_nodes.append(node)
            inp[sec.JUNCTIONS].add_obj(node)

            # TODO: COORDINATES based on vertices
            inp[sec.COORDINATES].add_obj(Coordinate(node.Name,
                                                    x=np.interp(x, [0, conduit.Length],
                                                                [from_node_coord.x, to_node_coord.x]),
                                                    y=np.interp(x, [0, conduit.Length],
                                                                [from_node_coord.y, to_node_coord.y])))

        link = Conduit(Name=f'{conduit.Name}_{chr(new_node_i + 97)}',
                       FromNode=last_node.Name,
                       ToNode=node.Name,
                       Length=dx,
                       Roughness=conduit.Roughness,
                       InOffset=0 if new_node_i != 0 else conduit.InOffset,
                       OutOffset=0 if new_node_i != (n_new_nodes - 1) else conduit.OutOffset,
                       InitFlow=conduit.InitFlow,
                       MaxFlow=conduit.MaxFlow)
        new_links.append(link)
        inp[sec.CONDUITS].add_obj(link)

        xs = inp[sec.XSECTIONS][conduit.Name].copy()
        xs.Link = link.Name
        inp[sec.XSECTIONS].add_obj(xs)

        if loss:
            inlet = loss.Inlet if loss.Inlet and (new_node_i == 0) else 0
            outlet = loss.Outlet if loss.Outlet and (new_node_i == n_new_nodes - 1) else 0
            average = loss.Average / (n_new_nodes + 1)
            flap_gate = loss.FlapGate

            if any([inlet, outlet, average, flap_gate]):
                inp[sec.LOSSES].add_obj(Loss(link.Name, inlet, outlet, average, flap_gate))

        # TODO: VERTICES

        if node is to_node:
            break
        last_node = node
        x += dx

    # if conduit.Name in inp[sec.VERTICES]:
    #     pass
    # else:
    #     # interpolate coordinates
    #     pass

    delete_link(inp, conduit.Name)


def combine_vertices(inp: SwmmInput, label1, label2):
    if sec.COORDINATES not in inp:
        # if there are not coordinates this function is nonsense
        return

    if sec.VERTICES not in inp:
        # we will at least ad the coordinates of the common node
        inp[sec.VERTICES] = Vertices.create_section()

    new_vertices = list()

    if label1 in inp[sec.VERTICES]:
        new_vertices += list(inp[sec.VERTICES][label1].vertices)

    common_node = links_dict(inp)[label1].ToNode
    if common_node in inp[sec.COORDINATES]:
        new_vertices += [inp[sec.COORDINATES][common_node].point]

    if label2 in inp[sec.VERTICES]:
        new_vertices += list(inp[sec.VERTICES][label2].vertices)

    if label1 in inp[sec.VERTICES]:
        inp[sec.VERTICES][label1].vertices = new_vertices
    else:
        inp[sec.VERTICES].add_obj(Vertices(label1, vertices=new_vertices))


def combine_conduits(inp, c1, c2, graph: DiGraph = None):
    """
    combine the two conduits to one keep attributes of the first (c1)

    works inplace

    Args:
        inp (SwmmInput): inp data
        c1 (str | Conduit): conduit 1 to combine
        c2 (str | Conduit): conduit 2 to combine
        graph (networkx.DiGraph): optional, runs faster with graph (inp representation)

    Returns:
        SwmmInput: inp data
    """
    if isinstance(c1, str):
        c1 = inp[sec.CONDUITS][c1]
    if isinstance(c2, str):
        c2 = inp[sec.CONDUITS][c2]
    # -------------------------
    if graph:
        graph.remove_edge(c1.FromNode, c1.ToNode)
    # -------------------------
    if c1.FromNode == c2.ToNode:
        c_first = c2.copy()  # type: Conduit
        c_second = c1.copy()  # type: Conduit
    elif c1.ToNode == c2.FromNode:
        c_first = c1.copy()  # type: Conduit
        c_second = c2.copy()  # type: Conduit
    else:
        raise EnvironmentError('Links not connected')

    # -------------------------
    # vertices + Coord of middle node
    combine_vertices(inp, c_first.Name, c_second.Name)

    # -------------------------
    c_new = c1  # type: Conduit
    # -------------------------
    common_node = c_first.ToNode
    c_new.FromNode = c_first.FromNode
    c_new.ToNode = c_second.ToNode
    # -------------------------
    if graph:
        graph.add_edge(c_new.FromNode, c_new.ToNode, label=c_new.Name)

    if isinstance(c_new, Conduit):
        c_new.Length = round(c1.Length + c2.Length, 1)

        # offsets
        c_new.InOffset = c_first.InOffset
        c_new.OutOffset = c_second.OutOffset

    # Loss
    if (sec.LOSSES in inp) and (c_new.Name in inp[sec.LOSSES]):
        print(f'combine_conduits {c1.Name} and {c2.Name}. BUT WHAT TO DO WITH LOSSES?')
        # add losses
        pass

    delete_node(inp, common_node, graph=graph, alt_node=c_new.FromNode)
    return c_new


def combine_conduits_keep_slope(inp, c1, c2, graph: DiGraph = None):
    nodes = nodes_dict(inp)
    new_out_offset = (- calc_slope(inp, c1) * c2.Length
                      + c1.OutOffset
                      + nodes[c1.ToNode].Elevation
                      - nodes[c2.ToNode].Elevation)
    c1 = combine_conduits(inp, c1, c2, graph=graph)
    c1.OutOffset = round(new_out_offset, 2)
    return c1


def dissolve_conduit(inp, c: Conduit, graph: DiGraph = None):
    """
    combine the two conduits to one

    Args:
        inp (SwmmInput): inp data
        c1 (str | Conduit): conduit 1 to combine
        c2 (str | Conduit): conduit 2 to combine
        keep_first (bool): keep first (of conduit 1) cross-section; else use second (of conduit 2)

    Returns:
        SwmmInput: inp data
    """
    common_node = c.FromNode
    for c_old in list(previous_links(inp, common_node, g=graph)):
        if graph:
            graph.remove_edge(c_old.FromNode, c_old.ToNode)

        c_new = c_old  # type: Conduit

        # vertices + Coord of middle node
        combine_vertices(inp, c_new.Name, c.Name)

        c_new.ToNode = c.ToNode
        # -------------------------
        if graph:
            graph.add_edge(c_new.FromNode, c_new.ToNode, label=c_new.Name)

        # Loss
        if sec.LOSSES in inp and c_new.Name in inp[sec.LOSSES]:
            print(f'dissolve_conduit {c.Name} in {c_new.Name}. BUT WHAT TO DO WITH LOSSES?')

        if isinstance(c_new, Conduit):
            c_new.Length = round(c.Length + c_new.Length, 1)
            # offsets
            c_new.OutOffset = c.OutOffset

    delete_node(inp, common_node, graph=graph, alt_node=c.ToNode)


# def dissolve_node(inp, node):
#     """
#     delete node and combine conduits
#
#     Args:
#         inp (InpData): inp data
#         node (str | Junction | Storage | Outfall): node to delete
#
#     Returns:
#         InpData: inp data
#     """
#     if isinstance(node, str):
#         node = find_node(inp, node)
#     # create new section with only
#     c1 = inp[sec.CONDUITS].slice_section([node.Name], 'ToNode')
#     if c1:
#         c2 = inp[sec.CONDUITS].slice_section([node.Name], 'FromNode')
#         inp = combine_conduits(inp, c1, c2)
#     else:
#         inp = delete_node(node.Name)
#     return inp


def conduit_iter_over_inp(inp, start, end):
    """
    iterate of the inp-file data

    only correct when FromNode and ToNode are in the correct direction
    doesn't look backwards if split node

    Args:
        inp (SwmmInput): inp-file data
        start (str): start node label
        end (str): end node label

    Yields:
        Conduit: input conduits
    """
    g = inp_to_graph(inp)

    if start and end:
        shortest_path_nodes = get_path(g, start, end)
        for n in shortest_path_nodes:
            for i in g.out_edges(n):
                if i[1] in shortest_path_nodes:
                    yield g.get_edge_data(*i)['label']
    # else:
    #     node = start
    #     while node:
    #         for l in next_links(g, node):
    #             yield l
    #
    #         # Todo: abzweigungen ...
    #         node = list(next_nodes(g, node))[0]

    # while True:
    #     found = False
    #     for i, c in inp[sec.CONDUITS].items():
    #         if c.FromNode == node:
    #             conduit = c
    #
    #             node = conduit.ToNode
    #             yield conduit
    #             found = True
    #             break
    #     if not found or (node is not None and (node == end)):
    #         break


def junction_to_storage(inp, label, *args, **kwargs):
    """
    convert :class:`~swmm_api.input_file.inp_sections.node.Junction` to
    :class:`~swmm_api.input_file.inp_sections.node.Storage`

    and add it to the STORAGE section

    Args:
        inp (SwmmInput): inp-file data
        label (str): label of the junction
        *args: argument of the :class:`~swmm_api.input_file.inp_sections.node.Storage`-class
        **kwargs: keyword arguments of the :class:`~swmm_api.input_file.inp_sections.node.Storage`-class
    """
    j = inp[sec.JUNCTIONS].pop(label)  # type: Junction
    if sec.STORAGE not in inp:
        inp[sec.STORAGE] = Storage.create_section()
    inp[sec.STORAGE].add_obj(Storage(Name=label, Elevation=j.Elevation, MaxDepth=j.MaxDepth,
                                     InitDepth=j.InitDepth, Apond=j.Aponded, *args, **kwargs))


def junction_to_outfall(inp, label, *args, **kwargs):
    """
    convert :class:`~swmm_api.input_file.inp_sections.node.Junction` to
    :class:`~swmm_api.input_file.inp_sections.node.Outfall`

    and add it to the OUTFALLS section

    Args:
        inp (SwmmInput): inp-file data
        label (str): label of the junction
        *args: argument of the :class:`~swmm_api.input_file.inp_sections.node.Outfall`-class
        **kwargs: keyword arguments of the :class:`~swmm_api.input_file.inp_sections.node.Outfall`-class
    """
    j = inp[sec.JUNCTIONS].pop(label)  # type: Junction
    if sec.OUTFALLS not in inp:
        inp[sec.OUTFALLS] = Outfall.create_section()
    inp[sec.OUTFALLS].add_obj(Outfall(Name=label, Elevation=j.Elevation, *args, **kwargs))


def conduit_to_orifice(inp, label, Type, Offset, Qcoeff, FlapGate=False, Orate=0):
    """
    convert :class:`~swmm_api.input_file.inp_sections.link.Conduit` to
    :class:`~swmm_api.input_file.inp_sections.link.Orifice`

    and add it to the ORIFICES section

    Args:
        inp (SwmmInput): inp-file data
        label (str): label of the conduit
        Type (str): orientation of orifice: either SIDE or BOTTOM.
        Offset (float): amount that a Side Orifice’s bottom or the position of a Bottom Orifice is offset above
            the invert of inlet node (ft or m, expressed as either a depth or as an elevation,
            depending on the LINK_OFFSETS option setting).
        Qcoeff (float): discharge coefficient (unitless).
        FlapGate (bool): YES if flap gate present to prevent reverse flow, NO if not (default is NO).
        Orate (int): time in decimal hours to open a fully closed orifice (or close a fully open one).
                        Use 0 if the orifice can open/close instantaneously.
    """
    c = inp[sec.CONDUITS].pop(label)  # type: Conduit
    if sec.ORIFICES not in inp:
        inp[sec.ORIFICES] = Orifice.create_section()
    inp[sec.ORIFICES].add_obj(Orifice(Name=label, FromNode=c.FromNode, ToNode=c.ToNode,
                                      Type=Type, Offset=Offset, Qcoeff=Qcoeff, FlapGate=FlapGate, Orate=Orate))


def subcachtment_nodes_dict(inp: SwmmInput):
    """
    get dict where key=node and value=list of subcatchment connected to the node (set as outlet)

    Args:
        inp (SwmmInput): inp data

    Returns:
        dict: dict[node] = list(subcatchments)
    """
    if sec.SUBCATCHMENTS in inp:
        di = {n: [] for n in nodes_dict(inp)}
        for s in inp.SUBCATCHMENTS.items():
            di[s.Outlet].append(s)
        return di


def rename_node(inp: SwmmInput, old_label: str, new_label: str, g=None):
    """
    change node label

    Notes:
        works inplace
        CONTROLS Not Implemented!

    Args:
        inp (SwmmInput): inp data
        old_label (str): previous node label
        new_label (str): new node label
        g (
    """
    # ToDo: Not Implemented: CONTROLS

    # Nodes and basic node components
    for section in [sec.JUNCTIONS, sec.OUTFALLS, sec.DIVIDERS, sec.STORAGE,
                    sec.COORDINATES, sec.RDII]:
        if (section in inp) and (old_label in inp[section]):
            inp[section][new_label] = inp[section].pop(old_label)
            if hasattr(inp[section][new_label], 'Name'):
                inp[section][new_label].Name = new_label
            else:
                inp[section][new_label].Node = new_label

    # tags
    if (sec.TAGS in inp) and ((Tag.TYPES.Node, old_label) in inp.TAGS):
        tag = inp[sec.TAGS].pop((Tag.TYPES.Node, old_label))
        tag.Name = new_label
        inp.TAGS.add_obj(tag)

    # subcatchment outlets
    if sec.SUBCATCHMENTS in inp:
        for obj in subcachtment_nodes_dict(inp)[old_label]:
            obj.Outlet = new_label
        # -------
        # for obj in inp.SUBCATCHMENTS.filter_keys([old_label], 'Outlet'):  # type: SubCatchment
        #     obj.Outlet = new_label
        # -------

    # link: from-node and to-node
    previous_links, next_links = links_connected(inp, old_label, g=g)
    for link in previous_links:
        link.ToNode = new_label

    for link in next_links:
        link.ToNode = new_label

    # -------
    # for section in [sec.CONDUITS, sec.PUMPS, sec.ORIFICES, sec.WEIRS, sec.OUTLETS]:
    #     if section in inp:
    #         for obj in inp[section].filter_keys([old_label], 'FromNode'):  # type: _Link
    #             obj.FromNode = new_label
    #
    #         for obj in inp[section].filter_keys([old_label], 'ToNode'):  # type: _Link
    #             obj.ToNode = new_label
    # -------

    # (dwf-)inflows
    constituents = [DryWeatherFlow.TYPES.FLOW]
    if sec.POLLUTANTS in inp:
        constituents += list(inp.POLLUTANTS.keys())

    for section in [sec.INFLOWS, sec.DWF, sec.TREATMENT]:
        if section in inp:
            for constituent in constituents:
                old_id = (old_label, constituent)
                if old_id in inp[section]:
                    inp[section][old_id].Node = new_label
                    inp[section][(new_label, constituent)] = inp[section].pop(old_id)

            # -------
            # for obj in inp[section].filter_keys([old_label], 'Node'):  # type: Inflow
            #     obj.Node = new_label
            #     inp[section][(new_label, obj[obj._identifier[1]])] = inp[section].pop((old_label, obj[obj._identifier[1]]))
            # -------


def rename_link(inp: SwmmInput, old_label: str, new_label: str):
    """
    change link label

    Notes:
        works inplace
        CONTROLS Not Implemented!

    Args:
        inp (SwmmInput): inp data
        old_label (str): previous link label
        new_label (str): new link label
    """
    # ToDo: Not Implemented: CONTROLS
    for section in [sec.CONDUITS, sec.PUMPS, sec.ORIFICES, sec.WEIRS, sec.OUTLETS,
                    sec.XSECTIONS, sec.LOSSES, sec.VERTICES]:
        if (section in inp) and (old_label in inp[section]):
            inp[section][new_label] = inp[section].pop(old_label)
            if hasattr(inp[section][new_label], 'Name'):
                inp[section][new_label].Name = new_label
            else:
                inp[section][new_label].Link = new_label

    if (sec.TAGS in inp) and ((Tag.TYPES.Link, old_label) in inp.TAGS):
        inp[sec.TAGS][(Tag.TYPES.Link, new_label)] = inp[sec.TAGS].pop((Tag.TYPES.Link, old_label))


def rename_timeseries(inp, old_label, new_label):
    """
    change timeseries label

    Notes:
        works inplace

    Args:
        inp (SwmmInput): inp data
        old_label (str): previous timeseries label
        new_label (str): new timeseries label
    """
    if old_label in inp[sec.TIMESERIES]:
        obj = inp[sec.TIMESERIES].pop(old_label)
        obj.Name = new_label
        inp[sec.TIMESERIES].add_obj(obj)

    key = EvaporationSection.KEYS.TIMESERIES  # TemperatureSection.KEYS.TIMESERIES, ...

    if sec.RAINGAGES in inp:
        f = inp[sec.RAINGAGES].frame
        filtered_table = f[(f['Source'] == key) & (f['Timeseries'] == old_label)]
        if not filtered_table.empty:
            for i in filtered_table.index:
                inp[sec.RAINGAGES][i].Timeseries = new_label

    if sec.EVAPORATION in inp:
        if key in inp[sec.EVAPORATION]:
            if inp[sec.EVAPORATION][key] == old_label:
                inp[sec.EVAPORATION][key] = new_label

    if sec.TEMPERATURE in inp:
        if key in inp[sec.TEMPERATURE]:
            if inp[sec.TEMPERATURE][key] == old_label:
                inp[sec.TEMPERATURE][key] = new_label

    if sec.OUTFALLS in inp:
        f = inp[sec.OUTFALLS].frame
        filtered_table = f[(f['Type'] == key) & (f['Data'] == old_label)]
        if not filtered_table.empty:
            for i in filtered_table.index:
                inp[sec.OUTFALLS][i].Data = new_label

    if sec.INFLOWS in inp:
        f = inp[sec.INFLOWS].frame
        filtered_table = f[f['TimeSeries'] == old_label]
        if not filtered_table.empty:
            for i in filtered_table.index:
                inp[sec.INFLOWS][i].TimeSeries = new_label


def remove_empty_sections(inp):
    """
    remove empty inp-file data sections

    Args:
        inp (SwmmInput): inp-file data

    Returns:
        SwmmInput: cleaned inp-file data
    """
    new_inp = SwmmInput()
    for section in inp:
        if inp[section]:
            new_inp[section] = inp[section]
    return new_inp


def reduce_curves(inp):
    """
    get used CURVES from [STORAGE, OUTLETS, PUMPS and XSECTIONS] and keep only used curves in the section

    Args:
        inp (SwmmInput): inp-file data

    Returns:
        SwmmInput: inp-file data with filtered CURVES section
    """
    if sec.CURVES not in inp:
        return inp
    used_curves = set()
    for section in [sec.STORAGE, sec.OUTLETS, sec.PUMPS, sec.XSECTIONS]:
        if section in inp:
            for name in inp[section]:
                if isinstance(inp[section][name].Curve, str):
                    used_curves.add(inp[section][name].Curve)

    inp[sec.CURVES] = inp[sec.CURVES].slice_section(used_curves)
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
    # new = Curve.create_section()
    # for label, curve in curve_section.items():
    #     new[label] = Curve(curve.Name, curve.Type, points=ramer_douglas(curve_section[label].points, dist=dist))
    # return new
    for curve in curve_section.values():  # type: Curve
        curve.points = ramer_douglas(curve.points, dist=dist)
    return curve_section


def reduce_raingages(inp):
    """
    get used RAINGAGES from SUBCATCHMENTS and keep only used raingages in the section

    Args:
        inp (SwmmInput):  inp-file data

    Returns:
        SwmmInput: inp-file data with filtered RAINGAGES section
    """
    if sec.SUBCATCHMENTS not in inp or sec.RAINGAGES not in inp:
        return inp
    needed_raingages = {inp[sec.SUBCATCHMENTS][s].RainGage for s in inp[sec.SUBCATCHMENTS]}
    inp[sec.RAINGAGES] = inp[sec.RAINGAGES].slice_section(needed_raingages)
    return inp


def filter_nodes(inp, final_nodes):
    """
     filter nodes in the network

    Args:
        inp (SwmmInput): inp-file data
        final_nodes (list | set):

    Returns:
        SwmmInput: new inp-file data
    """
    for section in [sec.JUNCTIONS,
                    sec.OUTFALLS,
                    sec.STORAGE,
                    sec.COORDINATES]:  # ignoring dividers
        if section in inp:
            inp[section] = inp[section].slice_section(final_nodes)

    # __________________________________________
    for section in [sec.INFLOWS, sec.DWF]:
        if section in inp:
            inp[section] = inp[section].slice_section(final_nodes, by=IDENTIFIERS.Node)

    # __________________________________________
    if sec.TAGS in inp:
        new = inp[sec.TAGS].create_new_empty()
        new.add_multiple(inp[sec.TAGS].filter_keys([Tag.TYPES.Subcatch, Tag.TYPES.Link], by='kind'))
        new.add_multiple(inp[sec.TAGS].filter_keys(((Tag.TYPES.Node, k) for k in final_nodes)))
        inp[sec.TAGS] = new

    # __________________________________________
    inp = remove_empty_sections(inp)
    return inp


def filter_links_within_nodes(inp, final_nodes):
    """
    filter links by nodes in the network

    Args:
        inp (SwmmInput): inp-file data
        final_nodes (list | set):

    Returns:
        SwmmInput: new inp-file data
    """
    final_links = set()
    for section in [sec.CONDUITS,
                    sec.PUMPS,
                    sec.ORIFICES,
                    sec.WEIRS,
                    sec.OUTLETS]:
        if section in inp:
            inp[section] = inp[section].slice_section(final_nodes, by=['FromNode', 'ToNode'])
            final_links |= set(inp[section].keys())

    # __________________________________________
    inp = _filter_link_components(inp, final_links)
    # __________________________________________
    inp = remove_empty_sections(inp)
    return inp


def filter_links(inp, final_links):
    """
    filter links by nodes in the network

    Args:
        inp (SwmmInput): inp-file data
        final_nodes (list | set):

    Returns:
        SwmmInput: new inp-file data
    """
    for section in [sec.CONDUITS,
                    sec.PUMPS,
                    sec.ORIFICES,
                    sec.WEIRS,
                    sec.OUTLETS]:
        if section in inp:
            inp[section] = inp[section].slice_section(final_links)

    # __________________________________________
    inp = _filter_link_components(inp, final_links)
    # __________________________________________
    inp = remove_empty_sections(inp)
    return inp


def _filter_link_components(inp, final_links):
    for section in [sec.XSECTIONS, sec.LOSSES, sec.VERTICES]:
        if section in inp:
            inp[section] = inp[section].slice_section(final_links)

    # __________________________________________
    if sec.TAGS in inp:
        new = inp[sec.TAGS].create_new_empty()
        new.add_multiple(inp[sec.TAGS].filter_keys([Tag.TYPES.Subcatch, Tag.TYPES.Node], by='kind'))
        new.add_multiple(inp[sec.TAGS].filter_keys(((Tag.TYPES.Link, k) for k in final_links)))
        inp[sec.TAGS] = new
        # inp[sec.TAGS] = inp[sec.TAGS].slice_section(((Tag.TYPES.Link, k) for k in final_links))

    # __________________________________________
    inp = remove_empty_sections(inp)
    return inp


def filter_subcatchments(inp, final_nodes):
    """
    filter subcatchments by nodes in the network

    Args:
        inp (SwmmInput): inp-file data
        final_nodes (list | set):

    Returns:
        SwmmInput: new inp-file data
    """
    if sec.SUBCATCHMENTS in inp:
        sub_orig = inp[sec.SUBCATCHMENTS].copy()
        # all with an outlet to final_nodes
        inp[sec.SUBCATCHMENTS] = inp[sec.SUBCATCHMENTS].slice_section(final_nodes, by='Outlet')
        # all with an outlet to an subcatchment
        inp[sec.SUBCATCHMENTS].update(sub_orig.slice_section(inp[sec.SUBCATCHMENTS].keys(), by='Outlet'))

        # __________________________________________
        for section in [sec.SUBAREAS, sec.INFILTRATION, sec.POLYGONS]:
            if section in inp:
                inp[section] = inp[section].slice_section(inp[sec.SUBCATCHMENTS])

        # __________________________________________
        if sec.TAGS in inp:
            new = inp[sec.TAGS].create_new_empty()
            new.add_multiple(inp[sec.TAGS].filter_keys([Tag.TYPES.Link, Tag.TYPES.Node], by='kind'))
            new.add_multiple(inp[sec.TAGS].filter_keys(((Tag.TYPES.Subcatch, k) for k in inp[sec.SUBCATCHMENTS])))
            inp[sec.TAGS] = new
            # inp[sec.TAGS] = inp[sec.TAGS].slice_section(((Tag.TYPES.Subcatch, k) for k in inp[sec.SUBCATCHMENTS]))

    else:
        for section in [sec.SUBAREAS, sec.INFILTRATION, sec.POLYGONS]:
            if section in inp:
                del inp[section]

        if sec.TAGS in inp:
            inp[sec.TAGS] = inp[sec.TAGS].slice_section([Tag.TYPES.Node, Tag.TYPES.Link], by='kind')

    # __________________________________________
    inp = remove_empty_sections(inp)
    return inp


def group_edit(inp):
    # ToDo
    # for objects of type (Subcatchments, Infiltration, Junctions, Storage Units, or Conduits)
    # with tag equal to
    # edit the property
    # by replacing it with
    pass


def update_vertices(inp):
    """
    add node coordinates to link vertices (start and end point)

    important for GIS export or GIS operations

    Notes:
        works inplace

    Args:
        inp (SwmmInput): inp data

    Returns:
        SwmmInput: changes inp data
    """
    links = links_dict(inp)
    coords = inp[COORDINATES]
    for l in links.values():  # type: Conduit # or Weir or Orifice or Pump or Outlet
        if l.Name not in inp[VERTICES]:
            object_type = inp[VERTICES]._section_object
            inp[VERTICES].add_obj(object_type(l.Name, vertices=list()))

        v = inp[VERTICES][l.Name].vertices
        inp[VERTICES][l.Name].vertices = [coords[l.FromNode].point] + v + [coords[l.ToNode].point]
    return inp


def reduce_vertices(inp, node_range=0.25):
    """
    remove first and last vertices to keep only inner vertices (SWMM standard)

    important if data originally from GIS and export to SWMM

    Notes:
        works inplace

    Args:
        inp (SwmmInput):
        node_range (float): minimal distance in m from the first and last vertices to the end nodes

    Returns:
        SwmmInput:
    """
    links = links_dict(inp)

    for l in links.values():  # type: Conduit
        if l.Name in inp[VERTICES]:
            v = inp[VERTICES][l.Name].vertices
            p = inp[COORDINATES][l.FromNode].point
            if _vec2d_dist(p, v[0]) < node_range:
                v = v[1:]

            if v:
                p = inp[COORDINATES][l.ToNode].point
                if _vec2d_dist(p, v[-1]) < node_range:
                    v = v[:-1]

            if v:
                inp[VERTICES][l.Name].vertices = v
            else:
                del inp[VERTICES][l.Name]
    return inp


def check_for_nodes(inp):
    links = links_dict(inp)
    nodes = nodes_dict(inp)
    for link in links.values():
        if link.FromNode not in nodes:
            print(link, link.FromNode)
        if link.ToNode not in nodes:
            print(link, link.ToNode)


def short_status(inp):
    for section in inp:
        print(f'{section}: {len(inp[section])}')


########################################################################################################################
def inp_to_graph(inp: SwmmInput) -> DiGraph:
    """
    create a network of the model with the networkx package

    Args:
        inp (SwmmInput): inp-file data

    Returns:
        networkx.DiGraph: networkx graph of the model
    """
    # g = nx.Graph()
    g = DiGraph()
    for node in nodes_dict(inp).keys():
        g.add_node(node)
    for link in links_dict(inp).values():
        # if link.FromNode not in g:
        #     g.add_node(link.FromNode)
        # if link.ToNode not in g:
        #     g.add_node(link.ToNode)
        g.add_edge(link.FromNode, link.ToNode, label=link.Name)
    return g


def get_path(g, start, end):
    # dijkstra_path(g, start, end)
    return list(all_simple_paths(g, start, end))[0]


def get_path_subgraph(base, start, end):
    if isinstance(base, SwmmInput):
        g = inp_to_graph(base)
    else:
        g = base
    sub_list = get_path(g, start=start, end=end)
    sub_graph = subgraph(g, sub_list)
    return sub_list, sub_graph


def next_links(inp, node, g=None):
    if g is None:
        g = inp_to_graph(inp)
    links = links_dict(inp)
    for i in g.out_edges(node):
        yield links[g.get_edge_data(*i)['label']]


def next_links_labels(g, node):
    labels = []
    for i in g.out_edges(node):
        labels.append(g.get_edge_data(*i)['label'])
    return labels


def next_nodes(g, node):
    return list(g.successors(node))


def previous_links(inp, node, g=None):
    if g is None:
        g = inp_to_graph(inp)
    links = links_dict(inp)
    for i in g.in_edges(node):
        yield links[g.get_edge_data(*i)['label']]


def previous_links_labels(g, node):
    labels = []
    for i in g.in_edges(node):
        labels.append(g.get_edge_data(*i)['label'])
    return labels


def previous_nodes(g, node):
    return list(g.predecessors(node))


def links_connected(inp, node, g=None):
    if g is None:
        g = inp_to_graph(inp)
    links = links_dict(inp)
    next_ = []
    for i in g.out_edges(node):
        next_.append(links[g.get_edge_data(*i)['label']])
    previous_ = []
    for i in g.in_edges(node):
        previous_.append(links[g.get_edge_data(*i)['label']])
    return previous_, next_


def number_in_out(g, node):
    return len(list(g.predecessors(node))), len(list(g.successors(node)))


def downstream_nodes(graph: DiGraph, node: str) -> list:
    """
    get all nodes downstream of the node given

    only the direction of links defined in the INP file counts (not the elevation)

    Args:
        graph (networkx.DiGraph): network of the inp data
        node (str): node label

    Returns:
        list[str]: list of nodes downstream of the given node
    """
    return _downstream_nodes(graph,  node)


def _downstream_nodes(graph: DiGraph, node: str, node_list=None) -> list:
    if node_list is None:
        node_list = list()
    node_list.append(node)
    next_nodes = list(graph.successors(node))
    if next_nodes:
        for n in next_nodes:
            if n in node_list:
                continue
            node_list = _downstream_nodes(graph, n, node_list)
    return node_list


def upstream_nodes(graph: DiGraph, node: str) -> list:
    """
    get all nodes upstream of the node given

    only the direction of links defined in the INP file counts (not the elevation)

    Args:
        graph (networkx.DiGraph): network of the inp data
        node (str): node label

    Returns:
        list[str]: list of nodes upstream of the given node
    """
    return _upstream_nodes(graph,  node)


def _upstream_nodes(graph: DiGraph, node: str, node_list=None) -> list:
    if node_list is None:
        node_list = list()
    node_list.append(node)
    next_nodes = list(graph.predecessors(node))
    if next_nodes:
        for n in next_nodes:
            if n in node_list:
                continue
            node_list = _upstream_nodes(graph, n, node_list)
    return node_list


########################################################################################################################
def create_sub_inp(inp, nodes):
    """
    split model network and only keep nodes.

    Notes:
        CONTROLS not supported

    Args:
        inp (SwmmInput): inp-file data
        nodes (list[str]): list of node labels to keep in inp data

    Returns:
        SwmmInput: filtered inp-file data
    """
    inp = filter_nodes(inp, nodes)
    inp = filter_links_within_nodes(inp, nodes)
    inp = filter_subcatchments(inp, nodes)

    # __________________________________________
    # TODO
    # if CONTROLS in inp:
    #     del inp[CONTROLS]

    # __________________________________________
    inp = reduce_curves(inp)
    inp = reduce_raingages(inp)
    inp = remove_empty_sections(inp)
    return inp


def split_network(inp, keep_node, split_at_node=None, keep_split_node=True, graph=None, init_print=True):
    """
    split model network at the ``split_at_node``-node and keep the part with the ``keep_node``-node.

    If you don't want to keep the ``split_at_node``-node toggle ``keep_split_node`` to False

    Set ``graph`` if a network-graph already exists (is faster).

    Notes:
        CONTROLS not supported

    Args:
        inp (SwmmInput): inp-file data
        keep_node (str): label of a node in the part you want to keep
        split_at_node (str): if you want to split the network, define the label of the node where you want to split it.
        keep_split_node (bool): if you want to keep the ``split_at_node`` node.
        graph (networkx.DiGraph): networkx graph of the model

    Returns:
        SwmmInput: filtered inp-file data
    """
    if graph is None:
        graph = inp_to_graph(inp)

    if split_at_node is not None:
        graph.remove_node(split_at_node)

    if isinstance(graph, DiGraph):
        graph = graph.to_undirected()
    sub = subgraph(graph, node_connected_component(graph, keep_node))

    if init_print:
        print(f'Reduced Network from {len(graph.nodes)} nodes to {len(sub.nodes)} nodes.')

    # _______________
    final_nodes = list(sub.nodes)
    if split_at_node is not None and keep_split_node:
        final_nodes.append(split_at_node)
    final_nodes = set(final_nodes)

    # _______________
    return create_sub_inp(inp, final_nodes)


def get_network_forks(inp):
    # pd.DataFrame.from_dict(forks, orient='index')
    g = inp_to_graph(inp)
    nodes = nodes_dict(inp)
    forks = dict()
    for n in nodes:
        forks[n] = number_in_out(g, n)
    return forks


def increase_max_node_depth(inp, node_label):
    # swmm raises maximum node depth to surrounding xsection height
    previous_, next_ = links_connected(inp, node_label)
    node = nodes_dict(inp)[node_label]
    max_height = node.MaxDepth
    for link in previous_ + next_:
        max_height = max((max_height, inp[XSECTIONS][link.Name].Geom1))
    print(f'MaxDepth increased for node "{node_label}" from {node.MaxDepth} to {max_height}')
    node.MaxDepth = max_height


def set_times(inp, start, end, head=None, tail=None):
    """
    set start and end time of the inp-file

    Args:
        inp (SwmmInput): inp data
        start (datetime.datetime): start time of the simulation and the reporting
        end (datetime.datetime): end time of the simulation
        head (datetime.timedelta): brings start time forward
        tail (datetime.timedelta): brings end time backward

    Returns:
        SwmmInput: changed inp data
    """
    if head is None:
        sim_start = start
    else:
        sim_start = start - head

    if tail is None:
        end = end
    else:
        end = end + tail

    report_start = start
    inp[sec.OPTIONS]['START_DATE'] = sim_start.date()
    inp[sec.OPTIONS]['START_TIME'] = sim_start.time()
    inp[sec.OPTIONS]['REPORT_START_DATE'] = report_start.date()
    inp[sec.OPTIONS]['REPORT_START_TIME'] = report_start.time()
    inp[sec.OPTIONS]['END_DATE'] = end.date()
    inp[sec.OPTIONS]['END_TIME'] = end.time()
    return inp


############################################################
def compare_sections(s1, s2, precision=3):
    """
    compare two inp file sections and get the differences as string output

    Args:
        s1 (InpSection): filename for the first inp file
        s2 (InpSection): filename for the second inp file
        precision (int): number of relevant decimal places

    Returns:
        str: differences of the sections
    """
    i1 = set(s1.keys())
    i2 = set(s2.keys())
    s_warnings = str()
    not_in_1 = list()
    not_in_2 = list()
    n_equal = 0
    not_equal = list()

    for key in i1 | i2:
        if (key in i1) and (key in i2):
            if s1[key] == s2[key]:
                n_equal += 1
            else:
                try:
                    if not isinstance(s1[key], BaseSectionObject):
                        not_equal.append(f'"{key}": {s1[key]} != {s2[key]}')
                    else:
                        diff = list()
                        for param in s1[key].to_dict_():
                            if not is_equal(s1[key][param], s2[key][param], precision=precision):
                                diff.append(f'{param}=({s1[key][param]} != {s2[key][param]})')
                        if diff:
                            not_equal.append(f'"{key}": ' + ' | '.join(diff))
                except:
                    not_equal.append(f'"{key}": can not compare')

        # -----------------------------
        elif (key in i1) and (key not in i2):
            not_in_1.append(f'"{key}"')
        elif (key not in i1) and (key in i2):
            not_in_2.append(f'"{key}"')

    # -----------------------------
    if not_equal:
        s_warnings += 'not equal: \n    ' + '\n    '.join(not_equal) + '\n'

    if not_in_1:
        s_warnings += f'not in inp1 ({len(not_in_1)}): ' + ' | '.join(not_in_1) + '\n'

    if not_in_2:
        s_warnings += f'not in inp2 ({len(not_in_2)}): ' + ' | '.join(not_in_2) + '\n'

    # -----------------------------
    res = ''
    if s_warnings:
        res += s_warnings
    else:
        res += 'good!\n'

    res += f'{n_equal}/{len(i1 | i2)} objects are equal\n'

    return res


def compare_inp_files(fn1, fn2, precision=2):
    """
    compare two inp files and get the differences as string output

    Args:
        fn1 (str): filename for the first inp file
        fn2 (str): filename for the second inp file
        precision (int): number of relevant decimal places

    Returns:
        str: differences of the files
    """
    s = f'Comparing \n' \
        f'   "{fn1}" (=inp1)\n' \
        f'   to\n' \
        f'   "{fn2}" (=inp2)\n\n'
    inp1 = SwmmInput.read_file(fn1)
    inp2 = SwmmInput.read_file(fn2)

    sections = set(inp1.keys()) | set(inp2.keys())

    for section in sorted(sections, key=_sort_by):
        if section in [sec.TITLE]:
            continue
        s += '\n' + '#' * 100 + f'\n[{section}]\n'

        if (section in inp1) and (section in inp2):
            s += compare_sections(inp1[section], inp2[section], precision=precision)
        elif (section not in inp1) and (section in inp2):
            s += f'only in inp2\n'
        elif (section in inp1) and (section not in inp2):
            s += f'only in inp1\n'
        else:
            s += f'not in both inps\n'  # should not happen

    return s
