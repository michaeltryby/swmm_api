from warnings import warn

from .. import section_labels as sec
from .collection import links_dict, nodes_dict
from ..section_lists import NODE_SECTIONS, LINK_SECTIONS


def check_for_nodes(inp):
    links = links_dict(inp)
    nodes = nodes_dict(inp)
    for link in links.values():
        if link.FromNode not in nodes:
            warn(f'Nodes not Found | {link} |  {link.FromNode}')
        if link.ToNode not in nodes:
            warn(f'Nodes not Found | {link} |  {link.ToNode}')


def check_for_duplicates(inp):
    """
    print duplicate objects in the links and nodes

    Args:
        inp (SwmmInput): inp data
    """
    print('DUPLICATE NODES')
    for node in nodes_dict(inp):
        if sum((node in inp[s] for s in NODE_SECTIONS + [sec.SUBCATCHMENTS] if s in inp)) != 1:
            print('-', *[inp[s][node] for s in NODE_SECTIONS + [sec.SUBCATCHMENTS] if s in inp and node in inp[s]], sep='\n  ')
    print('\nDUPLICATE LINKS')
    for link in links_dict(inp):
        if sum((link in inp[s] for s in LINK_SECTIONS if s in inp)) != 1:
            print('-', *[inp[s][link] for s in LINK_SECTIONS if s in inp and link in inp[s]], sep='\n')
