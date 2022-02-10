from ..section_abr import SEC
from .collection import links_dict, nodes_dict
from ..misc.curve_simplification import ramer_douglas


def reduce_curves(inp):
    """
    get used CURVES from [STORAGE, OUTLETS, PUMPS and XSECTIONS] and keep only used curves in the section

    Args:
        inp (SwmmInput): inp-file data

    Returns:
        SwmmInput: inp-file data with filtered CURVES section
    """
    if SEC.CURVES not in inp:
        return inp
    used_curves = set()
    for section in [SEC.STORAGE, SEC.OUTLETS, SEC.PUMPS, SEC.XSECTIONS]:
        if section in inp:
            for name in inp[section]:
                if isinstance(inp[section][name].Curve, str):
                    used_curves.add(inp[section][name].Curve)

    inp[SEC.CURVES] = inp[SEC.CURVES].slice_section(used_curves)
    return inp


def reduce_pattern(inp):
    used_pattern = set()
    if SEC.EVAPORATION in inp:
        #  optional monthly time pattern of multipliers for infiltration recovery rates during dry periods
        if 'RECOVERY' in inp[SEC.EVAPORATION]:
            used_pattern.add(inp[SEC.EVAPORATION]['RECOVERY'])

    if SEC.AQUIFERS in inp:
        #  optional monthly time pattern used to adjust the upper zone evaporation fraction
        used_pattern |= set(inp[SEC.AQUIFERS].frame['Epat'].dropna().values)

    if SEC.INFLOWS in inp:
        #  optional time pattern used to adjust the baseline value on a periodic basis
        used_pattern |= set(inp[SEC.INFLOWS].frame['Pattern'].dropna().values)

    if SEC.DWF in inp:
        for i in range(1, 5):
            used_pattern |= set(inp[SEC.DWF].frame[f'pattern{i}'].dropna().values)

    if SEC.PATTERNS in inp:
        inp[SEC.PATTERNS] = inp[SEC.PATTERNS].slice_section(used_pattern)
    return inp


def reduce_controls(inp):
    """
    get used CONTROLS from [CONDUIT, ORIFICE, WEIR, OUTLET / NODE, LINK, CONDUIT, PUMP, ORIFICE, WEIR, OUTLET] and keep only used controls in the section

    Args:
        inp (SwmmInput): inp-file data

    Returns:
        SwmmInput: inp-file data with filtered CONTROLS section
    """
    if SEC.CONTROLS not in inp:
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
        del inp[SEC.CONTROLS]
    else:
        inp[SEC.CONTROLS] = inp[SEC.CONTROLS].slice_section(used_controls)
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
    if SEC.SUBCATCHMENTS not in inp or SEC.RAINGAGES not in inp:
        return inp
    needed_raingages = {inp[SEC.SUBCATCHMENTS][s].RainGage for s in inp[SEC.SUBCATCHMENTS]}
    inp[SEC.RAINGAGES] = inp[SEC.RAINGAGES].slice_section(needed_raingages)
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
