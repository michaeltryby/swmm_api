from networkx import DiGraph, all_simple_paths, subgraph, node_connected_component

from ..inp import SwmmInput
from .collection import nodes_dict, links_dict
from .filter import create_sub_inp
from ..section_labels import SUBCATCHMENTS


def inp_to_graph(inp):
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
        g.add_edge(link.from_node, link.to_node, label=link.name)
    return g


def get_path(g, start, end):
    # dijkstra_path(g, start, end)
    return list(all_simple_paths(g, start, end))[0]


def get_path_subgraph(base, start, end):
    g = inp_to_graph(base) if isinstance(base, SwmmInput) else base
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
    return [g.get_edge_data(*i)['label'] for i in g.out_edges(node)]


def next_nodes(g, node):
    return list(g.successors(node))


def previous_links(inp, node, g=None):
    if g is None:
        g = inp_to_graph(inp)
    links = links_dict(inp)
    for i in g.in_edges(node):
        yield links[g.get_edge_data(*i)['label']]


def previous_links_labels(g, node):
    return [g.get_edge_data(*i)['label'] for i in g.in_edges(node)]


def previous_nodes(g, node):
    return list(g.predecessors(node))


def links_connected(inp, node, g=None):
    """
    Get the names of the links connected to the node.

    Args:
        inp (SwmmInput): inp-data.
        node (str): name of the node.
        g (networkx.DiGraph | optionl): graph of the swmm-network.

    Returns:
        tuple[list[swmm_api.input_file.sections.link._Link]]: list of the upstream and downstream links connected to the node
    """
    if g is None:
        g = inp_to_graph(inp)
    links = links_dict(inp)
    next_ = [links[g.get_edge_data(*i)['label']] for i in g.out_edges(node)]
    previous_ = [links[g.get_edge_data(*i)['label']] for i in g.in_edges(node)]
    return previous_, next_


def number_in_out(g, node):
    return len(list(g.predecessors(node))), len(list(g.successors(node)))


def downstream_nodes(graph, node):
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
        node_list = []
    node_list.append(node)
    next_nodes = list(graph.successors(node))
    if next_nodes:
        for n in next_nodes:
            if n in node_list:
                continue
            node_list = _downstream_nodes(graph, n, node_list)
    return node_list


def upstream_nodes(graph, node):
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
        node_list = []
    node_list.append(node)
    next_nodes = list(graph.predecessors(node))
    if next_nodes:
        for n in next_nodes:
            if n in node_list:
                continue
            node_list = _upstream_nodes(graph, n, node_list)
    return node_list


def get_network_forks(inp):
    # pd.DataFrame.from_dict(forks, orient='index')
    g = inp_to_graph(inp)
    nodes = nodes_dict(inp)
    return {n: number_in_out(g, n) for n in nodes}


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
        split_at_node (str | list | tuple | set): if you want to split the network,
                define the label of the node (or multiple) where you want to split it.
        keep_split_node (bool): if you want to keep the ``split_at_node`` node.
        graph (networkx.DiGraph): networkx graph of the model

    Returns:
        SwmmInput: filtered inp-file data
    """
    if graph is None:
        graph = inp_to_graph(inp)

    if split_at_node is not None:
        if isinstance(split_at_node, str):
            graph.remove_node(split_at_node)
        else:
            for n in split_at_node:
                graph.remove_node(n)

    if isinstance(graph, DiGraph):
        graph = graph.to_undirected()
    sub = subgraph(graph, node_connected_component(graph, keep_node))

    if init_print:
        print(f'Reduced Network from {len(graph.nodes)} nodes to {len(sub.nodes)} nodes.')

    # _______________
    final_nodes = list(sub.nodes)
    if split_at_node is not None and keep_split_node:
        if isinstance(split_at_node, str):
            final_nodes.append(split_at_node)
        else:
            final_nodes += list(split_at_node)
    final_nodes = set(final_nodes)

    # _______________
    return create_sub_inp(inp, final_nodes)


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

def inp_to_graph2(inp):
    """
    Create a network of the model with the networkx package.

    Args:
        inp (SwmmInput): inp-file data

    Returns:
        networkx.DiGraph: networkx graph of the model
    """
    # g = nx.Graph()
    g = DiGraph()
    for node_label, node in nodes_dict(inp).items():
        g.add_node(node_label, obj=node)

    if SUBCATCHMENTS in inp:
        for sc_label, sc in inp[SUBCATCHMENTS].items():
            g.add_node(sc.name, obj=sc)
        for sc in inp.SUBCATCHMENTS.values():
            g.add_edge(sc.name, sc.outlet, label=f'Outlet({sc.name})')

    for link in links_dict(inp).values():
        # if link.FromNode not in g:
        #     g.add_node(link.FromNode)
        # if link.ToNode not in g:
        #     g.add_node(link.ToNode)
        g.add_edge(link.from_node, link.to_node, label=link.name, obj=link)
    return g