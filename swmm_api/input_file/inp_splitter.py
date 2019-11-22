import networkx as nx
from networkx.algorithms.components import node_connected_component

from .helpers.sections import *
from .inp_helpers import InpSection
from .inp_macros import reduce_curves, reduce_raingages
from .inp_sections_generic import TagsSection
from .testing.inp_graph_network import inp_to_graph


def split_network(inp, split_at_node, keep_node):
    if CONTROLS in inp:
        del inp[CONTROLS]

    g = inp_to_graph(inp)

    last_node = split_at_node
    g.remove_node(last_node)
    sub = nx.subgraph(g, node_connected_component(g, keep_node))

    final_nodes = set(list(sub.nodes) + [last_node])

    # __________________________________________
    for section in [JUNCTIONS,
                    OUTFALLS,
                    STORAGE]:
        section_nodes = set(inp[section].keys()).intersection(final_nodes)
        new_section = InpSection(inp[section].index)
        for node in section_nodes:
            new_section.append(inp[section][node])
        inp[section] = new_section

    # __________________________________________
    for section in [INFLOWS, DWF]:
        new_section = InpSection(inp[section].index)
        for name, thing in inp[section].items():
            if thing.Node in final_nodes:
                new_section.append(thing)
        inp[section] = new_section

    # __________________________________________
    final_links = list()
    for section in [CONDUITS,
                    PUMPS,
                    ORIFICES,
                    WEIRS]:
        new_section = InpSection(inp[section].index)
        for name, thing in inp[section].items():
            if thing.ToNode in final_nodes:
                new_section.append(thing)
                final_links.append(name)
        inp[section] = new_section

    # __________________________________________
    for section in [XSECTIONS, LOSSES]:
        new_section = InpSection(inp[section].index)
        for name, thing in inp[section].items():
            if thing.Link in final_links:
                new_section.append(thing)
        inp[section] = new_section

    # __________________________________________
    for section in [SUBCATCHMENTS]:
        new_section = InpSection(inp[section].index)
        for name, thing in inp[section].items():
            if thing.Outlet in final_nodes:
                new_section.append(thing)

    # __________________________________________
    for section in [SUBAREAS, INFILTRATION]:
        new_section = InpSection(inp[section].index)
        for name, thing in inp[section].items():
            if thing.subcatchment in inp[SUBCATCHMENTS]:
                new_section.append(thing)
        inp[section] = new_section

    # __________________________________________
    # section_filter[TAGS],  # node und link
    old_tags = inp[TAGS][TagsSection.Types.Node].copy()
    for name in old_tags:
        if name not in final_nodes:
            inp[TAGS][TagsSection.Types.Node].pop(name)

    old_tags = inp[TAGS][TagsSection.Types.Link].copy()
    for name in old_tags:
        if name not in final_links:
            inp[TAGS][TagsSection.Types.Link].pop(name)

    # __________________________________________
    new_coordinates = list()
    for line in inp[COORDINATES]:
        name = line[0]
        if name in final_nodes:
            new_coordinates.append(line)
    inp[COORDINATES] = new_coordinates

    # __________________________________________
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
