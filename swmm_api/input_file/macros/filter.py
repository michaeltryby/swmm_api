from .reduce_unneeded import reduce_controls, reduce_curves, reduce_raingages, remove_empty_sections
from .. import section_labels as sec
from ..section_lists import LINK_SECTIONS
from ..sections import Tag
from ..sections._identifiers import IDENTIFIERS


def filter_tags(inp):
    pass


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
    for section in LINK_SECTIONS:
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
    for section in LINK_SECTIONS:
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
    inp = reduce_controls(inp)
    inp = reduce_curves(inp)
    inp = reduce_raingages(inp)
    inp = remove_empty_sections(inp)
    return inp
