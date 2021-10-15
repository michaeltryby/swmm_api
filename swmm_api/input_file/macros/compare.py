from ... import SwmmInput
from .. import section_labels as sec
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
    s_warnings = str()
    not_in_1 = list()
    not_in_2 = list()
    n_equal = 0
    not_equal = list()

    for key in sorted(i1 | i2):
        if (key in i1) and (key in i2):
            if s1[key] == s2[key]:
                n_equal += 1
            else:
                try:
                    if not isinstance(s1[key], BaseSectionObject):
                        not_equal.append(f'{key}: {s1[key]} != {s2[key]}')
                    else:
                        diff = list()
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
        if section in [sec.TITLE]:
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

    return s
