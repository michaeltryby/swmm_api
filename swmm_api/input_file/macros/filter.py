from .reduce_unneeded import (reduce_controls, reduce_curves, reduce_raingages, remove_empty_sections, reduce_pattern,
                              reduce_timeseries, )
from ..section_labels import *
from ..section_lists import LINK_SECTIONS, NODE_SECTIONS
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
    for section in NODE_SECTIONS + [COORDINATES]:
        if section in inp:
            inp[section] = inp[section].slice_section(final_nodes)

    # __________________________________________
    for section in [INFLOWS, DWF]:
        if section in inp:
            inp[section] = inp[section].slice_section(final_nodes, by=IDENTIFIERS.node)

    # __________________________________________
    if TAGS in inp:
        new = inp[TAGS].create_new_empty()
        new.add_multiple(*inp[TAGS].filter_keys([Tag.TYPES.Subcatch, Tag.TYPES.Link], by='kind'))
        new.add_multiple(*inp[TAGS].filter_keys(((Tag.TYPES.Node, k) for k in final_nodes)))
        inp[TAGS] = new

    # __________________________________________
    remove_empty_sections(inp)
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
            inp[section] = inp[section].slice_section(final_nodes, by=['from_node', 'to_node'])
            final_links |= set(inp[section].keys())

    # __________________________________________
    inp = _filter_link_components(inp, final_links)
    # __________________________________________
    remove_empty_sections(inp)
    return inp


def filter_links(inp, final_links):
    """
    filter links by nodes in the network

    Args:
        inp (SwmmInput): inp-file data
        final_links (list | set):

    Returns:
        SwmmInput: new inp-file data
    """
    for section in LINK_SECTIONS:
        if section in inp:
            inp[section] = inp[section].slice_section(final_links)

    # __________________________________________
    inp = _filter_link_components(inp, final_links)
    # __________________________________________
    remove_empty_sections(inp)
    return inp


def _filter_link_components(inp, final_links):
    for section in [XSECTIONS, LOSSES, VERTICES]:
        if section in inp:
            inp[section] = inp[section].slice_section(final_links)

    # __________________________________________
    if TAGS in inp:
        new = inp[TAGS].create_new_empty()
        new.add_multiple(*inp[TAGS].filter_keys([Tag.TYPES.Subcatch, Tag.TYPES.Node], by='kind'))
        new.add_multiple(*inp[TAGS].filter_keys(((Tag.TYPES.Link, k) for k in final_links)))
        inp[TAGS] = new
        # inp[TAGS] = inp[TAGS].slice_section(((Tag.TYPES.Link, k) for k in final_links))

    # __________________________________________
    remove_empty_sections(inp)
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
    if SUBCATCHMENTS in inp:
        sub_orig = inp[SUBCATCHMENTS].copy()
        # all with an outlet to final_nodes
        inp[SUBCATCHMENTS] = inp[SUBCATCHMENTS].slice_section(final_nodes, by='outlet')
        # all with an outlet to an subcatchment
        inp[SUBCATCHMENTS].update(sub_orig.slice_section(inp[SUBCATCHMENTS].keys(), by='outlet'))

        # __________________________________________
        for section in [SUBAREAS, INFILTRATION, POLYGONS]:
            if section in inp:
                inp[section] = inp[section].slice_section(inp[SUBCATCHMENTS])

        # __________________________________________
        if TAGS in inp:
            new = inp[TAGS].create_new_empty()
            new.add_multiple(*inp[TAGS].filter_keys([Tag.TYPES.Link, Tag.TYPES.Node], by='kind'))
            new.add_multiple(*inp[TAGS].filter_keys(((Tag.TYPES.Subcatch, k) for k in inp[SUBCATCHMENTS])))
            inp[TAGS] = new
            # inp[TAGS] = inp[TAGS].slice_section(((Tag.TYPES.Subcatch, k) for k in inp[SUBCATCHMENTS]))

    else:
        for section in [SUBAREAS, INFILTRATION, POLYGONS]:
            if section in inp:
                del inp[section]

        if TAGS in inp:
            inp[TAGS] = inp[TAGS].slice_section([Tag.TYPES.Node, Tag.TYPES.Link], by='kind')

    # __________________________________________
    remove_empty_sections(inp)
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
    reduce_controls(inp)
    reduce_curves(inp)
    reduce_raingages(inp)
    reduce_pattern(inp)
    reduce_timeseries(inp)
    remove_empty_sections(inp)
    return inp
