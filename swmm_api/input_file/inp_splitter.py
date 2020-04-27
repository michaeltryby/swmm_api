import networkx as nx
from networkx.algorithms.components import node_connected_component

from .helpers.sections import *
from .inp_helpers import InpSection
from .inp_macros import reduce_curves, reduce_raingages
from .inp_sections_generic import TagsSection
from .testing.inp_graph_network import inp_to_graph


def split_network(inp, keep_node, split_at_node=None, keep_split_node=True):
    if CONTROLS in inp:
        del inp[CONTROLS]

    g = inp_to_graph(inp)

    if split_at_node is not None:
        g.remove_node(split_at_node)
    sub = nx.subgraph(g, node_connected_component(g, keep_node))

    print(f'Reduced Network from {len(g.nodes)} nodes to {len(sub.nodes)} nodes.')

    final_nodes = list(sub.nodes)
    if split_at_node is not None and keep_split_node:
        final_nodes.append(split_at_node)
    final_nodes = set(final_nodes)

    # __________________________________________
    for section in [JUNCTIONS,
                    OUTFALLS,
                    STORAGE]:
        if section not in inp:
            continue
        section_nodes = set(inp[section].keys()).intersection(final_nodes)
        new_section = InpSection(inp[section].index)
        for node in section_nodes:
            new_section.append(inp[section][node])

        if new_section.empty:
            del inp[section]
        else:
            inp[section] = new_section

    # __________________________________________
    for section in [INFLOWS, DWF]:
        if section not in inp:
            continue
        new_section = InpSection(inp[section].index)
        for name, thing in inp[section].items():
            if thing.Node in final_nodes:
                new_section.append(thing)

        if new_section.empty:
            del inp[section]
        else:
            inp[section] = new_section

    # __________________________________________
    final_links = list()
    for section in [CONDUITS,
                    PUMPS,
                    ORIFICES,
                    WEIRS, OUTLETS]:
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
    for section in [XSECTIONS, LOSSES]:
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
    for section in [SUBCATCHMENTS]:
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
    for section in [SUBAREAS, INFILTRATION]:
        if section not in inp:
            continue
        new_section = InpSection(inp[section].index)
        for name, thing in inp[section].items():
            if thing.subcatchment in inp[SUBCATCHMENTS]:
                new_section.append(thing)

        if new_section.empty:
            del inp[section]
        else:
            inp[section] = new_section

    # __________________________________________
    # section_filter[TAGS],  # node und link
    if TAGS in inp:
        old_tags = inp[TAGS][TagsSection.Types.Node].copy()
        for name in old_tags:
            if name not in final_nodes:
                inp[TAGS][TagsSection.Types.Node].pop(name)

        old_tags = inp[TAGS][TagsSection.Types.Link].copy()
        for name in old_tags:
            if name not in final_links:
                inp[TAGS][TagsSection.Types.Link].pop(name)

    # __________________________________________
    if COORDINATES in inp:
        new_coordinates = list()
        for line in inp[COORDINATES]:
            name = line[0]
            if name in final_nodes:
                new_coordinates.append(line)
        inp[COORDINATES] = new_coordinates

    # __________________________________________
    if VERTICES in inp:
        new_verticies = list()
        for line in inp[VERTICES]:
            name = line[0]
            if name in final_links:
                new_verticies.append(line)
        inp[VERTICES] = new_verticies

    # __________________________________________
    inp = reduce_curves(inp)
    inp = reduce_raingages(inp)

    return inp
