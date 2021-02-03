from collections import ChainMap
from math import ceil
from os import path, mkdir, listdir

import numpy as np
from networkx import DiGraph, all_simple_paths, subgraph, node_connected_component, shortest_path
from statistics import mean
from typing import Dict, List, Any

from .inp_helpers import InpData, InpSection
from .inp_reader import read_inp_file, convert_section
from .inp_sections import *
from .inp_sections import labels as sec
from .inp_sections.identifiers import IDENTIFIERS
from .inp_sections.labels import VERTICES, COORDINATES, XSECTIONS
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


########################################################################################################################
def combined_subcatchment_frame(inp: InpData):
    """
    combine all information of the subcatchment data-frames

    Args:
        inp (InpData): inp-file data

    Returns:
        pandas.DataFrame: combined subcatchment data
    """
    return inp[sec.SUBCATCHMENTS].frame.join(inp[sec.SUBAREAS].frame).join(inp[sec.INFILTRATION].frame)


########################################################################################################################
def nodes_dict(inp: InpData):
    """
    get a dict of all nodes

    the objects are referenced, so you can use it to modify too.

    Args:
        inp (InpData): inp-file data

    Returns:
        dict[str, Junction or Storage or Outfall]: dict of {labels: objects}
    """
    nodes: ChainMap[str, Junction] = ChainMap()
    for section in [sec.JUNCTIONS, sec.OUTFALLS, sec.DIVIDERS, sec.STORAGE]:
        if section in inp:
            nodes.maps.append(inp[section])
    return nodes


def find_node(inp: InpData, node_label):
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


def links_dict(inp: InpData):  # or Weir or Orifice or Pump or Outlet
    """
    get a dict of all links

    the objects are referenced, so you can use it to modify too.

    Args:
        inp (InpData): inp-file data

    Returns:
        dict[str, Conduit or Weir or Orifice or Pump or Outlet]: dict of {labels: objects}
    """
    links: ChainMap[str, Conduit] = ChainMap()
    for section in [sec.CONDUITS, sec.PUMPS, sec.ORIFICES, sec.WEIRS, sec.OUTLETS]:
        if section in inp:
            links.maps.append(inp[section])
    return links


def find_link(inp: InpData, label):
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


########################################################################################################################
def calc_slope(inp: InpData, link):
    """
    calculate the slop of a link

    Args:
        inp (InpData): inp-file data
        link (Conduit | Weir | Outlet | Orifice | Pump): link

    Returns:
        float: slop of the link
    """
    nodes = nodes_dict(inp)
    return (nodes[link.FromNode].Elevation + link.InOffset - (
            nodes[link.ToNode].Elevation + link.OutOffset)) / link.Length


def rel_diff(a, b):
    m = mean([a + b])
    if m == 0:
        return abs(a - b)
    return abs(a - b) / m


def rel_slope_diff(inp: InpData, l0, l1):
    nodes = nodes_dict(inp)
    slope_res = (nodes[l0.FromNode].Elevation + l0.InOffset
                 - (nodes[l1.ToNode].Elevation + l1.OutOffset)
                 ) / (l0.Length + l1.Length)
    return rel_diff(calc_slope(inp, l0), slope_res)


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


def conduits_are_equal(inp: InpData, link0, link1, diff_roughness=0.1, diff_slope=0.1, diff_height=0.1):
    all_checks_out = True

    # Roughness values match within a specified percent tolerance
    if diff_roughness is not None:
        all_checks_out &= rel_diff(link0.Roughness, link1.Roughness) < diff_roughness

    xs0 = inp[sec.XSECTIONS][link0.Name]  # type: CrossSection
    xs1 = inp[sec.XSECTIONS][link1.Name]  # type: CrossSection

    # Diameter values match within a specified percent tolerance (1 %)
    if diff_height is not None:
        all_checks_out &= rel_diff(xs0.Geom1, xs1.Geom1) < diff_height

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
        rel_slope_diff = rel_diff(calc_slope(inp, link0), calc_slope(inp, link1))

        # if rel_slope_diff < 0:
        #     nodes = nodes_dict(inp)
        #     print(nodes[link0.FromNode].Elevation, link0.InOffset, nodes[link0.ToNode].Elevation, link0.OutOffset)
        #     print(nodes[link1.FromNode].Elevation, link1.InOffset, nodes[link1.ToNode].Elevation, link1.OutOffset)
        #     print('rel_slope_diff < 0', link0, link1)
        all_checks_out &= rel_slope_diff < diff_slope

    return all_checks_out


def delete_node(inp: InpData, node_label, graph: DiGraph = None, alt_node=None):
    """
    delete node in inp data

    Args:
        inp (InpData): inp data
        node_label (str): label of node to delete
        graph (DiGraph): networkx graph of model

    Returns:
        InpData: inp data
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


def move_flows(inp, from_node, to_node, only_Constituent=None):
    for section in (sec.INFLOWS, sec.DWF):
        if section not in inp:
            continue
        if only_Constituent is None:
            only_Constituent = [DryWeatherFlow.TYPES.FLOW]
        for t in only_Constituent:
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


def delete_link(inp: InpData, link):
    for s in [sec.CONDUITS, sec.PUMPS, sec.ORIFICES, sec.WEIRS, sec.OUTLETS, sec.XSECTIONS, sec.LOSSES, sec.VERTICES]:
        if (s in inp) and (link in inp[s]):
            inp[s].pop(link)


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
            node = Junction(Name=f'{from_node.Name}_{to_node.Name}_{chr(new_node_i+97)}',
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
                                                    x=np.interp(x, [0, conduit.Length], [from_node_coord.x, to_node_coord.x]),
                                                    y=np.interp(x, [0, conduit.Length], [from_node_coord.y, to_node_coord.y])))

        link = Conduit(Name=f'{conduit.Name}_{chr(new_node_i+97)}',
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


def combine_vertices(inp, label1, label2):
    common_node = links_dict(inp)[label1].ToNode
    if sec.VERTICES in inp and label1 in inp[sec.VERTICES]:
        new_vertices = inp[sec.VERTICES][label1].vertices
        if sec.COORDINATES in inp and common_node in inp[sec.COORDINATES]:
            new_vertices += [inp[sec.COORDINATES][common_node].point]
        new_vertices += inp[sec.VERTICES][label2].vertices
        inp[sec.VERTICES][label1].vertices = new_vertices


def combine_conduits(inp, c1, c2, graph: DiGraph = None):
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
    new_out_offset = - calc_slope(inp, c1) * c2.Length \
                     + c1.OutOffset \
                     + nodes[c1.ToNode].Elevation \
                     - nodes[c2.ToNode].Elevation
    c1 = combine_conduits(inp, c1, c2, graph=graph)
    c1.OutOffset = round(new_out_offset, 2)
    return c1


def dissolve_conduit(inp, c: Conduit, graph: DiGraph = None):
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
        inp (InpData): inp-file data
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
        inp (InpData): inp-file data
        label (str): label of the junction
        *args: argument of the :class:`~swmm_api.input_file.inp_sections.node.Storage`-class
        **kwargs: keyword arguments of the :class:`~swmm_api.input_file.inp_sections.node.Storage`-class
    """
    j = inp[sec.JUNCTIONS].pop(label)  # type: Junction
    if sec.STORAGE not in inp:
        inp[sec.STORAGE] = InpSection(Storage)
    inp[sec.STORAGE].add_obj(Storage(Name=label, Elevation=j.Elevation, MaxDepth=j.MaxDepth,
                                     InitDepth=j.InitDepth, Apond=j.Aponded, *args, **kwargs))


def junction_to_outfall(inp, label, *args, **kwargs):
    """
    convert :class:`~swmm_api.input_file.inp_sections.node.Junction` to
    :class:`~swmm_api.input_file.inp_sections.node.Outfall`

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
    inp[sec.OUTFALLS].add_obj(Outfall(Name=label, Elevation=j.Elevation, *args, **kwargs))


def conduit_to_orifice(inp, label, Type, Offset, Qcoeff, FlapGate=False, Orate=0):
    """
    convert :class:`~swmm_api.input_file.inp_sections.link.Conduit` to
    :class:`~swmm_api.input_file.inp_sections.link.Orifice`

    and add it to the ORIFICES section

    Args:
        inp (InpData): inp-file data
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


def rename_node(inp, old_label, new_label):
    for section in [sec.JUNCTIONS, sec.OUTFALLS, sec.DIVIDERS, sec.STORAGE, sec.COORDINATES]:
        if (section in inp) and (old_label in inp[section]):
            inp[section][new_label] = inp[section].pop(old_label)
            if hasattr(inp[section][new_label], 'Name'):
                inp[section][new_label].Name = new_label
            else:
                inp[section][new_label].Node = new_label


def rename_link(inp, old_label, new_label):
    for section in [sec.CONDUITS, sec.PUMPS, sec.ORIFICES, sec.WEIRS, sec.OUTLETS, sec.XSECTIONS, sec.LOSSES,
                    sec.VERTICES]:
        if (section in inp) and (old_label in inp[section]):
            inp[section][new_label] = inp[section].pop(old_label)
            if hasattr(inp[section][new_label], 'Name'):
                inp[section][new_label].Name = new_label
            else:
                inp[section][new_label].Link = new_label


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
        inp (InpData):  inp-file data

    Returns:
        InpData: inp-file data with filtered RAINGAGES section
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
            inp[section] = inp[section].slice_section(final_nodes)

    # __________________________________________
    for section in [sec.INFLOWS, sec.DWF]:
        if section in inp:
            inp[section] = inp[section].slice_section(final_nodes, by=IDENTIFIERS.Node)

    # __________________________________________
    if sec.TAGS in inp:
        inp[sec.TAGS] = inp[sec.TAGS].slice_section(((Tag.TYPES.Node, k) for k in final_nodes))

    # __________________________________________
    inp = remove_empty_sections(inp)
    return inp


def filter_links_within_nodes(inp, final_nodes):
    """
    filter links by nodes in the network

    Args:
        inp (InpData): inp-file data
        final_nodes (list | set):

    Returns:
        InpData: new inp-file data
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
    inp = filter_link_components(inp, final_links)
    # __________________________________________
    inp = remove_empty_sections(inp)
    return inp


def filter_links(inp, final_links):
    """
    filter links by nodes in the network

    Args:
        inp (InpData): inp-file data
        final_nodes (list | set):

    Returns:
        InpData: new inp-file data
    """
    for section in [sec.CONDUITS,
                    sec.PUMPS,
                    sec.ORIFICES,
                    sec.WEIRS,
                    sec.OUTLETS]:
        if section in inp:
            inp[section] = inp[section].slice_section(final_links)

    # __________________________________________
    inp = filter_link_components(inp, final_links)
    # __________________________________________
    inp = remove_empty_sections(inp)
    return inp


def filter_link_components(inp, final_links):
    for section in [sec.XSECTIONS, sec.LOSSES, sec.VERTICES]:
        if section in inp:
            inp[section] = inp[section].slice_section(final_links)

    # __________________________________________
    if sec.TAGS in inp:
        inp[sec.TAGS] = inp[sec.TAGS].slice_section(((Tag.TYPES.Link, k) for k in final_links))

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
        inp[sec.SUBCATCHMENTS] = inp[sec.SUBCATCHMENTS].slice_section(final_nodes, by='Outlet')
        # all with an outlet to an subcatchment
        inp[sec.SUBCATCHMENTS].update(sub_orig.slice_section(inp[sec.SUBCATCHMENTS].keys(), by='Outlet'))

        # __________________________________________
        for section in [sec.SUBAREAS, sec.INFILTRATION, sec.POLYGONS]:
            if section in inp:
                inp[section] = inp[section].slice_section(inp[sec.SUBCATCHMENTS])

        # __________________________________________
        if sec.TAGS in inp:
            inp[sec.TAGS] = inp[sec.TAGS].slice_section(((Tag.TYPES.Subcatch, k) for k in inp[sec.SUBCATCHMENTS]))

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

    Args:
        inp (InpData):
        node_range (float): minimal distance in m from the first and last vertices to the end nodes

    Returns:
        InpData:
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
def inp_to_graph(inp: InpData) -> DiGraph:
    """
    create a network of the model with the networkx package

    Args:
        inp (InpData): inp-file data

    Returns:
        networkx.DiGraph: networkx graph of the model
    """
    # g = nx.Graph()
    g = DiGraph()
    for link in links_dict(inp).values():
        g.add_node(link.FromNode)
        g.add_edge(link.FromNode, link.ToNode, label=link.Name)
    return g


def get_path(g, start, end):
    # dijkstra_path(g, start, end)
    return list(all_simple_paths(g, start, end))[0]


def get_path_subgraph(base, start, end):
    if isinstance(base, InpData):
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
    return len(g.predecessors(node)), len(g.successors(node))


########################################################################################################################
def split_network(inp, keep_node, split_at_node=None, keep_split_node=True, graph=None):
    """
    split model network at the ``split_at_node``-node and keep the part with the ``keep_node``-node.

    If you don't want to keep the ``split_at_node``-node toggle ``keep_split_node`` to False

    Set ``graph`` if a network-graph already exists (is faster).

    Args:
        inp (InpData): inp-file data
        keep_node (str): label of a node in the part you want to keep
        split_at_node (str): if you want to split the network, define the label of the node where you want to split it.
        keep_split_node (bool): if you want to keep the ``split_at_node`` node.
        graph (networkx.DiGraph): networkx graph of the model

    Returns:
        InpData: filtered inp-file data
    """
    if graph is None:
        graph = inp_to_graph(inp)

    if split_at_node is not None:
        graph.remove_node(split_at_node)
    sub = subgraph(graph, node_connected_component(graph, keep_node))

    print(f'Reduced Network from {len(graph.nodes)} nodes to {len(sub.nodes)} nodes.')

    final_nodes = list(sub.nodes)
    if split_at_node is not None and keep_split_node:
        final_nodes.append(split_at_node)
    final_nodes = set(final_nodes)

    # __________________________________________
    inp = filter_nodes(inp, final_nodes)

    # __________________________________________
    inp = filter_links(inp, final_nodes)

    # __________________________________________
    inp = filter_subcatchments(inp, final_nodes)

    # __________________________________________
    # TODO
    # if CONTROLS in inp:
    #     del inp[CONTROLS]

    # __________________________________________
    inp = reduce_curves(inp)
    inp = reduce_raingages(inp)
    inp = remove_empty_sections(inp)
    return inp


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
