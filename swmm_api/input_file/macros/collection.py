from collections import ChainMap

from ... import SwmmInput
from .. import section_labels as sec
from ..section_lists import NODE_SECTIONS, LINK_SECTIONS
from ..sections.link import _Link
from ..sections.node import _Node


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
    for section in NODE_SECTIONS:
        if section in inp:
            nodes.maps.append(inp[section])
    return nodes


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
    for section in LINK_SECTIONS:
        if section in inp:
            links.maps.append(inp[section])
    return links


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
