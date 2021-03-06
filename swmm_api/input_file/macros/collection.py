from collections import ChainMap

from ..section_labels import SUBCATCHMENTS
from ..section_lists import NODE_SECTIONS, LINK_SECTIONS


def nodes_dict(inp):
    """
    get a dict of all nodes

    the objects are referenced, so you can use it to modify too.

    Args:
        inp (swmm_api.SwmmInput): inp-file data

    Returns:
        ChainMap[str, swmm_api.input_file.sections.node._Node]: dict of {labels: objects}
    """
    nodes = ChainMap()
    for section in NODE_SECTIONS:
        if section in inp:
            nodes.maps.append(inp[section])
    return nodes


def nodes_subcatchments_dict(inp):
    """
    get a dict of all nodes and subcatchments

    the objects are referenced, so you can use it to modify too.

    Args:
        inp (swmm_api.SwmmInput): inp-file data

    Returns:
        ChainMap[str, swmm_api.input_file.sections.node._Node | swmm_api.input_file.sections.subcatch.SubCatchment]: dict of {labels: objects}
    """
    nodes_subcatchments = nodes_dict(inp)
    if SUBCATCHMENTS in inp:
        nodes_subcatchments.maps.append(inp[SUBCATCHMENTS])
    return nodes_subcatchments


def links_dict(inp):
    """
    get a dict of all links

    the objects are referenced, so you can use it to modify too.

    Args:
        inp (swmm_api.SwmmInput): inp-file data

    Returns:
        ChainMap[str, swmm_api.input_file.sections.link._Link]: dict of {labels: objects}
    """
    links = ChainMap()
    for section in LINK_SECTIONS:
        if section in inp:
            links.maps.append(inp[section])
    return links


def subcatchments_per_node_dict(inp):
    """
    get dict where key=node and value=list of subcatchment connected to the node (set as outlet)

    Args:
        inp (swmm_api.SwmmInput): inp data

    Returns:
        dict[str, list[swmm_api.input_file.sections.subcatch.SubCatchment]]: dict[node] = list(subcatchments)
    """
    if SUBCATCHMENTS in inp:
        di = {n: [] for n in nodes_dict(inp)}
        for s in inp.SUBCATCHMENTS.values():
            di[s.outlet].append(s)
        return di
