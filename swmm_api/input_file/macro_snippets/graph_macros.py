import networkx as nx
from networkx import node_connected_component

from ..inp_macros import (filter_nodes, filter_links, filter_subcatchments, reduce_curves,
                          reduce_raingages, remove_empty_sections, links_dict, nodes_dict, )
from ..inp_sections import Conduit
from ..inp_sections.labels import CONDUITS, WEIRS, PUMPS, ORIFICES, OUTLETS


def inp_to_graph(inp):
    """

    Args:
        inp ():

    Returns:

    """
    # g = nx.Graph()
    g = nx.DiGraph()
    for link in links_dict(inp).values():  # type: Conduit
        g.add_node(link.FromNode)
        g.add_edge(link.FromNode, link.ToNode, label=link.Name)
    return g


def get_path(g, start, end):
    """

    Args:
        g ():
        start ():
        end ():

    Returns:

    """
    return list(nx.all_simple_paths(g, start, end))[0]


def next_links(g, node):
    for i in g.out_edges(node):
        yield g.get_edge_data(*i)['label']


def next_nodes(g, node):
    return g.successors(node)


def previous_links(g, node):
    for i in g.in_edges(node):
        yield g.get_edge_data(*i)['label']


def previous_nodes(g, node):
    return g.predecessors(node)


def split_network(inp, keep_node, split_at_node=None, keep_split_node=True):
    """

    Args:
        inp ():
        keep_node ():
        split_at_node ():
        keep_split_node ():

    Returns:

    """
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
