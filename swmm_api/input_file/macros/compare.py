from .collection import nodes_dict, links_dict
from .graph import inp_to_graph, next_nodes, previous_links, next_links
from ..inp import SwmmInput
from ..section_labels import TITLE
from .._type_converter import is_equal
from ..helpers import BaseSectionObject, _sort_by


class CompareSections:
    def __init__(self, section_1, section_2, precision=3):
        """
        compare two inp file sections

        Args:
            section_1 (swmm_api.input_file.helpers.InpSection): filename for the first inp file
            section_2 (swmm_api.input_file.helpers.InpSection): filename for the second inp file
            precision (int): number of relevant decimal places
        """
        self.set_labels_1 = set(section_1.keys())
        self.set_labels_2 = set(section_2.keys())
        self.set_labels_equal = set()
        self.dict_not_equal = {}

        # self.equal_section_type = section_1._section_object == section_2._section_object
        # self.section_1._section_object.__name__
        # self.label = section_1._label

        for key in sorted(self.set_labels_1 & self.set_labels_2):
            if section_1[key] == section_2[key]:
                self.set_labels_equal.add(key)
            else:
                try:
                    if not isinstance(section_1[key], BaseSectionObject):
                        self.dict_not_equal[key] = f'{section_1[key]} != {section_2[key]}'
                    else:
                        diff = []
                        for param in section_1[key].to_dict_():
                            if not is_equal(section_1[key][param], section_2[key][param], precision=precision):
                                diff.append(f'{param}=({section_1[key][param]} != {section_2[key][param]})')
                        if diff:
                            self.dict_not_equal[key] = ' | '.join(diff)
                        else:
                            self.set_labels_equal.add(key)
                except:
                    self.dict_not_equal[key] = 'can not compare'

        self.set_labels_not_in_1 = self.set_labels_2 - self.set_labels_1
        self.set_labels_not_in_2 = self.set_labels_1 - self.set_labels_2

    @property
    def len_full(self):
        return len(self.set_labels_1 | self.set_labels_2)

    def get_diff_string(self):
        """
        get the differences as string output

        Returns:
            str: differences of the sections
        """
        s_warnings = ''
        if self.dict_not_equal:
            s_warnings += (f'not equal ({len(self.dict_not_equal)}): \n    '
                           + '\n    '.join([f'{k}: {v}' for k, v in self.dict_not_equal.items()]) + '\n')

        if self.set_labels_not_in_1:
            s_warnings += (f'not in inp1 ({len(self.set_labels_not_in_1)}): '
                           + ' | '.join(sorted(self.set_labels_not_in_1)) + '\n')

        if self.set_labels_not_in_2:
            s_warnings += (f'not in inp2 ({len(self.set_labels_not_in_2)}): '
                           + ' | '.join(sorted(self.set_labels_not_in_2)) + '\n')

        return (s_warnings or 'good!\n') + f'{len(self.set_labels_equal)}/{self.len_full} objects are equal\n'

    def get_diff_count_string(self):
        """
        get the number of differences as string output

        Returns:
            str: differences of the sections
        """
        s_warnings = ''
        if self.dict_not_equal:
            s_warnings += f'{len(self.dict_not_equal)} are not equal.\n'

        if self.set_labels_not_in_1:
            s_warnings += f'{len(self.set_labels_not_in_1)} are not in inp1.\n'

        if self.set_labels_not_in_2:
            s_warnings += f'{len(self.set_labels_not_in_2)} are not in inp2.\n'

        return (s_warnings or 'The  section is equal.\n') + f'{len(self.set_labels_equal)}/{self.len_full} objects are equal\n'

    @property
    def summary(self):
        return {
            'equal': len(self.set_labels_equal),
            'not in 1': len(self.set_labels_not_in_1),
            'not in 2': len(self.set_labels_not_in_2),
            'changes': len(self.dict_not_equal)
        }


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
            s += CompareSections(inp1[section], inp2[section], precision=precision).get_diff_string()
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
