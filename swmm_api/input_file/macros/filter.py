from .reduce_unneeded import reduce_controls, reduce_curves, reduce_raingages, remove_empty_sections, reduce_pattern
from ..section_abr import SEC
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
    for section in [SEC.JUNCTIONS,
                    SEC.OUTFALLS,
                    SEC.STORAGE,
                    SEC.COORDINATES]:  # ignoring dividers
        if section in inp:
            inp[section] = inp[section].slice_section(final_nodes)

    # __________________________________________
    for section in [SEC.INFLOWS, SEC.DWF]:
        if section in inp:
            inp[section] = inp[section].slice_section(final_nodes, by=IDENTIFIERS.Node)

    # __________________________________________
    if SEC.TAGS in inp:
        new = inp[SEC.TAGS].create_new_empty()
        new.add_multiple(*inp[SEC.TAGS].filter_keys([Tag.TYPES.Subcatch, Tag.TYPES.Link], by='kind'))
        new.add_multiple(*inp[SEC.TAGS].filter_keys(((Tag.TYPES.Node, k) for k in final_nodes)))
        inp[SEC.TAGS] = new

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
    for section in [SEC.XSECTIONS, SEC.LOSSES, SEC.VERTICES]:
        if section in inp:
            inp[section] = inp[section].slice_section(final_links)

    # __________________________________________
    if SEC.TAGS in inp:
        new = inp[SEC.TAGS].create_new_empty()
        new.add_multiple(*inp[SEC.TAGS].filter_keys([Tag.TYPES.Subcatch, Tag.TYPES.Node], by='kind'))
        new.add_multiple(*inp[SEC.TAGS].filter_keys(((Tag.TYPES.Link, k) for k in final_links)))
        inp[SEC.TAGS] = new
        # inp[SEC.TAGS] = inp[SEC.TAGS].slice_section(((Tag.TYPES.Link, k) for k in final_links))

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
    if SEC.SUBCATCHMENTS in inp:
        sub_orig = inp[SEC.SUBCATCHMENTS].copy()
        # all with an outlet to final_nodes
        inp[SEC.SUBCATCHMENTS] = inp[SEC.SUBCATCHMENTS].slice_section(final_nodes, by='Outlet')
        # all with an outlet to an subcatchment
        inp[SEC.SUBCATCHMENTS].update(sub_orig.slice_section(inp[SEC.SUBCATCHMENTS].keys(), by='Outlet'))

        # __________________________________________
        for section in [SEC.SUBAREAS, SEC.INFILTRATION, SEC.POLYGONS]:
            if section in inp:
                inp[section] = inp[section].slice_section(inp[SEC.SUBCATCHMENTS])

        # __________________________________________
        if SEC.TAGS in inp:
            new = inp[SEC.TAGS].create_new_empty()
            new.add_multiple(*inp[SEC.TAGS].filter_keys([Tag.TYPES.Link, Tag.TYPES.Node], by='kind'))
            new.add_multiple(*inp[SEC.TAGS].filter_keys(((Tag.TYPES.Subcatch, k) for k in inp[SEC.SUBCATCHMENTS])))
            inp[SEC.TAGS] = new
            # inp[SEC.TAGS] = inp[SEC.TAGS].slice_section(((Tag.TYPES.Subcatch, k) for k in inp[SEC.SUBCATCHMENTS]))

    else:
        for section in [SEC.SUBAREAS, SEC.INFILTRATION, SEC.POLYGONS]:
            if section in inp:
                del inp[section]

        if SEC.TAGS in inp:
            inp[SEC.TAGS] = inp[SEC.TAGS].slice_section([Tag.TYPES.Node, Tag.TYPES.Link], by='kind')

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
    inp = reduce_pattern(inp)
    return inp
