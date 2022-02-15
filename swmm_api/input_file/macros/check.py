import itertools

from ..section_labels import SUBCATCHMENTS
from .collection import links_dict, nodes_dict
from ..section_lists import NODE_SECTIONS, LINK_SECTIONS


def check_for_nodes(inp):
    """
    check if any link-end-node is missing

    Args:
        inp (swmm_api.SwmmInput): inp data

    Returns:
       tuple[set[swmm_api.input_file.sections.link._Link], set[str]]: set of corrupt links and a set of missing nodes
    """
    links = links_dict(inp)
    node_labels = set(nodes_dict(inp).keys())
    nodes_missing = set()
    links_corrupt = set()
    for link in links.values():
        if link.FromNode not in node_labels:
            nodes_missing.add(link.FromNode)
            links_corrupt.add(link)

        if link.ToNode not in node_labels:
            nodes_missing.add(link.ToNode)
            links_corrupt.add(link)

    return links_corrupt, nodes_missing


def check_for_duplicates(inp):
    """
    check if any node, link or subcatchment has a duplicate label in a different section

    Args:
        inp (swmm_api.SwmmInput): inp data

    Returns:
        tuple[set[str], set[str]]: set of duplicate nodes, links and subcatchments
    """

    nodes = {s: set(inp[s]) for s in NODE_SECTIONS + [SUBCATCHMENTS] if s in inp}

    nodes_duplicate = set()
    for s1, s2 in itertools.combinations(nodes.keys(), 2):
        nodes_duplicate |= nodes[s1] & nodes[s2]

    # -------------------
    links = {s: set(inp[s]) for s in LINK_SECTIONS if s in inp}

    links_duplicate = set()
    for s1, s2 in itertools.combinations(links.keys(), 2):
        links_duplicate |= links[s1] & links[s2]

    return nodes_duplicate, links_duplicate


def check_for_subcatchment_outlets(inp):
    """
    check if any subcatchments lost their outlets

    Args:
        inp (swmm_api.SwmmInput): inp data

    Returns:
        tuple[set[swmm_api.input_file.sections.subcatch.SubCatchment], set[str]]: : set of subcatchments_corrupt, outlets_missing
    """
    if SUBCATCHMENTS in inp:
        possible_outlets = set(nodes_dict(inp).keys()) | set(inp.SUBCATCHMENTS.keys())
        outlets = inp.SUBCATCHMENTS.frame.Outlet
        outlets_missing = set(outlets) - possible_outlets
        subcatchments_corrupt = {sc for sc in inp.SUBCATCHMENTS.values() if sc.Outlet in outlets_missing}
        return subcatchments_corrupt, outlets_missing
