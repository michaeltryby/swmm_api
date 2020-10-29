import networkx as nx
from networkx.algorithms.components import node_connected_component

from .inp_macros import (reduce_curves, reduce_raingages, filter_nodes, filter_links, filter_subcatchments,
                         remove_empty_sections, )
from .testing.inp_graph_network import inp_to_graph


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
