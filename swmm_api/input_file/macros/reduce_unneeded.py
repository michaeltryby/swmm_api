from .. import section_labels as sec
from .collection import links_dict, nodes_dict
from ..misc.curve_simplification import ramer_douglas, _vec2d_dist
from ..section_labels import VERTICES, COORDINATES


def reduce_curves(inp):
    """
    get used CURVES from [STORAGE, OUTLETS, PUMPS and XSECTIONS] and keep only used curves in the section

    Args:
        inp (SwmmInput): inp-file data

    Returns:
        SwmmInput: inp-file data with filtered CURVES section
    """
    if sec.CURVES not in inp:
        return inp
    used_curves = set()
    for section in [sec.STORAGE, sec.OUTLETS, sec.PUMPS, sec.XSECTIONS]:
        if section in inp:
            for name in inp[section]:
                if isinstance(inp[section][name].Curve, str):
                    used_curves.add(inp[section][name].Curve)

    inp[sec.CURVES] = inp[sec.CURVES].slice_section(used_curves)
    return inp


def reduce_controls(inp):
    """
    get used CONTROLS from [CONDUIT, ORIFICE, WEIR, OUTLET / NODE, LINK, CONDUIT, PUMP, ORIFICE, WEIR, OUTLET] and keep only used controls in the section

    Args:
        inp (SwmmInput): inp-file data

    Returns:
        SwmmInput: inp-file data with filtered CONTROLS section
    """
    if sec.CONTROLS not in inp:
        return inp

    used_controls = set()

    links = links_dict(inp)
    nodes = nodes_dict(inp)

    def _in_use(k, l):
        return (((k + 'S') in inp) and (l not in inp[k + 'S'])) or ((k == 'LINK') and (l not in links)) or ((k == 'NODE') and (l not in nodes))

    for control in inp.CONTROLS.values():
        is_used = True
        for kind, label, *_ in control.conditions:
            kind = kind.upper()
            if _in_use(kind, label):
                is_used = False
                break
        if is_used:
            for kind, label, *_ in control.actions:
                kind = kind.upper()
                if _in_use(kind, label):
                    is_used = False
                    break

        if is_used:
            used_controls.add(control.Name)

    if not used_controls:
        del inp[sec.CONTROLS]
    else:
        inp[sec.CONTROLS] = inp[sec.CONTROLS].slice_section(used_controls)
    return inp


def simplify_curves(curve_section, dist=0.001):
    """
    simplify curves with the algorithm by Ramer and Douglas

    Args:
        curve_section (InpSection[Curve]): old section
        dist (float): maximum Ramer-Douglas distance

    Returns:
        InpSection[Curve]: new section
    """
    # new = Curve.create_section()
    # for label, curve in curve_section.items():
    #     new[label] = Curve(curve.Name, curve.Type, points=ramer_douglas(curve_section[label].points, dist=dist))
    # return new
    for curve in curve_section.values():  # type: Curve
        curve.points = ramer_douglas(curve.points, dist=dist)
    return curve_section


def reduce_raingages(inp):
    """
    get used RAINGAGES from SUBCATCHMENTS and keep only used raingages in the section

    Args:
        inp (SwmmInput):  inp-file data

    Returns:
        SwmmInput: inp-file data with filtered RAINGAGES section
    """
    if sec.SUBCATCHMENTS not in inp or sec.RAINGAGES not in inp:
        return inp
    needed_raingages = {inp[sec.SUBCATCHMENTS][s].RainGage for s in inp[sec.SUBCATCHMENTS]}
    inp[sec.RAINGAGES] = inp[sec.RAINGAGES].slice_section(needed_raingages)
    return inp


def reduce_vertices(inp, node_range=0.25):
    """
    remove first and last vertices to keep only inner vertices (SWMM standard)

    important if data originally from GIS and export to SWMM

    Notes:
        works inplace

    Args:
        inp (SwmmInput):
        node_range (float): minimal distance in m from the first and last vertices to the end nodes

    Returns:
        SwmmInput:
    """
    links = links_dict(inp)

    for l in links.values():  # type: Conduit
        if l.Name in inp[VERTICES]:
            v = inp[VERTICES][l.Name].vertices
            p = inp[COORDINATES][l.FromNode].point
            if _vec2d_dist(p, v[0]) < node_range:
                v = v[1:]

            if v:
                p = inp[COORDINATES][l.ToNode].point
                if _vec2d_dist(p, v[-1]) < node_range:
                    v = v[:-1]

            if v:
                inp[VERTICES][l.Name].vertices = v
            else:
                del inp[VERTICES][l.Name]
    return inp


def remove_empty_sections(inp):
    """
    remove empty inp-file data sections

    Args:
        inp (SwmmInput): inp-file data

    Returns:
        SwmmInput: cleaned inp-file data
    """
    for section in list(inp.keys()):
        if not inp[section]:
            del inp[section]
    return inp