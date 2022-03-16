from .collection import nodes_dict, links_dict
from .graph import inp_to_graph, next_nodes, previous_links, next_links
from ..inp import SwmmInput
from ..section_labels import TITLE
from .._type_converter import is_equal
from ..helpers import BaseSectionObject, _sort_by


def compare_sections(s1, s2, precision=3):
    """
    compare two inp file sections and get the differences as string output

    Args:
        s1 (InpSection): filename for the first inp file
        s2 (InpSection): filename for the second inp file
        precision (int): number of relevant decimal places

    Returns:
        str: differences of the sections
    """
    i1 = set(s1.keys())
    i2 = set(s2.keys())
    s_warnings = ''
    not_in_1 = []
    not_in_2 = []
    n_equal = 0
    not_equal = []

    for key in sorted(i1 | i2):
        if (key in i1) and (key in i2):
            if s1[key] == s2[key]:
                n_equal += 1
            else:
                try:
                    if not isinstance(s1[key], BaseSectionObject):
                        not_equal.append(f'{key}: {s1[key]} != {s2[key]}')
                    else:
                        diff = []
                        for param in s1[key].to_dict_():
                            if not is_equal(s1[key][param], s2[key][param], precision=precision):
                                diff.append(f'{param}=({s1[key][param]} != {s2[key][param]})')
                        if diff:
                            not_equal.append(f'{key}: ' + ' | '.join(diff))
                except:
                    not_equal.append(f'{key}: can not compare')

        # -----------------------------
        elif (key in i1) and (key not in i2):
            not_in_2.append(str(key))
        elif (key not in i1) and (key in i2):
            not_in_1.append(str(key))

    # -----------------------------
    if not_equal:
        s_warnings += f'not equal ({len(not_equal)}): \n    ' + '\n    '.join(not_equal) + '\n'

    if not_in_1:
        s_warnings += f'not in inp1 ({len(not_in_1)}): ' + ' | '.join(not_in_1) + '\n'

    if not_in_2:
        s_warnings += f'not in inp2 ({len(not_in_2)}): ' + ' | '.join(not_in_2) + '\n'

    # -----------------------------
    res = ''
    if s_warnings:
        res += s_warnings
    else:
        res += 'good!\n'

    res += f'{n_equal}/{len(i1 | i2)} objects are equal\n'

    return res


def compare_inp_files(fn1, fn2, precision=2, skip_section=None):
    """
    compare two inp files and get the differences as string output

    Args:
        fn1 (str): filename for the first inp file
        fn2 (str): filename for the second inp file
        precision (int): number of relevant decimal places
        skip_section (list): skip sections if you don't care for specific changes

    Returns:
        str: differences of the files
    """
    s = f'Comparing \n' \
        f'   "{fn1}" (=inp1)\n' \
        f'   to\n' \
        f'   "{fn2}" (=inp2)\n\n'
    inp1 = SwmmInput.read_file(fn1)
    inp2 = SwmmInput.read_file(fn2)

    sections = set(inp1.keys()) | set(inp2.keys())

    for section in sorted(sections, key=_sort_by):
        if skip_section is not None and section in skip_section:
            continue
        if section in [TITLE]:
            continue
        s += '\n' + '#' * 100 + f'\n[{section}]\n'

        if (section in inp1) and (section in inp2):
            s += compare_sections(inp1[section], inp2[section], precision=precision)
        elif (section not in inp1) and (section in inp2):
            s += f'only in inp2\n'
        elif (section in inp1) and (section not in inp2):
            s += f'only in inp1\n'
        else:
            s += f'not in both inps\n'  # should not happen

    inp_version_control(inp1, inp2)

    return s


def _to_coordinates_list(geo_series):
    return list(zip(geo_series.x, geo_series.y))


def _next_nodes():
    # TODO ...
    coords_from = _to_coordinates_list(geometry_from.geometry)
    coords_to = _to_coordinates_list(geometry_to.geometry)
    # distance_matrix = distance.cdist(coords_from, coords_to, 'euclidean')
    # return np.argmin(distance_matrix, axis=1)

    from sklearn.neighbors import NearestNeighbors
    n_neighbors = 1
    nbrs = NearestNeighbors(n_neighbors=n_neighbors, algorithm='ball_tree').fit(coords_to)
    distances, indices = nbrs.kneighbors(coords_from)


def inp_version_control(inp_v1, inp_v2):
    # zuerst neue knoten erstellen
    #   wurde nur konvertiert oder umbenannt?
    #

    # bestehende links zu neuen knoten umleiten
    # neue links einfügen
    # alte knoten löschen

    # ----
    g1 = inp_to_graph(inp_v1)
    g2 = inp_to_graph(inp_v2)
    # ----
    # NODES
    nodes1 = nodes_dict(inp_v1)
    nodes2 = nodes_dict(inp_v2)

    # Knoten wurde konvertiert
    for node in set(nodes2.keys()) & set(nodes1.keys()):
        if type(nodes1[node]) != type(nodes2[node]):
            print(f'Für Knoten "{node}" hat sich der Objekt-Typ geändert: "{type(nodes1[node])}" zu "{type(nodes2[node])}"')

    nodes_new = set(nodes2.keys()) - set(nodes1.keys())
    for node_new in nodes_new:
        # wurde umbenannt
        # gleiche koordinate
        # oder gleichen inflow und outflow
        previous_links(inp_v2, node_new, g=g2)
        next_links(inp_v2, node_new, g=g2)

        pass
    nodes_removed = set(nodes1.keys()) - set(nodes2.keys())

    # ----
    # LINKS
    links1 = links_dict(inp_v1)
    links2 = links_dict(inp_v2)
    links_removed = set(links1.keys()) - set(links2.keys())
    links_new = set(links2.keys()) - set(links1.keys())

    # Link wurde konvertiert
    for link in set(links1.keys()) & set(links2.keys()):
        if type(links1[link]) != type(links2[link]):
            print(f'Für Knoten "{link}" hat sich der Objekt-Typ geändert: "{type(links1[link])}" zu "{type(links2[link])}"')
