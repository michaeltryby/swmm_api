from ..section_labels import *
from .collection import links_dict, nodes_dict
from ..misc.curve_simplification import ramer_douglas
from ..section_types import SECTION_TYPES
from ..sections import Control, EvaporationSection


def reduce_curves(inp):
    """
    remove unused curves

    only keep used CURVES from the sections [STORAGE, OUTLETS, PUMPS and XSECTIONS]

    Args:
        inp (swmm_api.SwmmInput): inp-file data

    .. Important::
        works inplace
    """
    if CURVES not in inp:
        return inp
    used_curves = set()
    for section in [STORAGE, OUTLETS, PUMPS, XSECTIONS]:
        if section in inp:
            for name in inp[section]:
                if isinstance(inp[section][name].Curve, str):
                    used_curves.add(inp[section][name].Curve)

    inp[CURVES] = inp[CURVES].slice_section(used_curves)


def reduce_pattern(inp):
    used_pattern = set()
    if EVAPORATION in inp:
        #  optional monthly time pattern of multipliers for infiltration recovery rates during dry periods
        if 'RECOVERY' in inp[EVAPORATION]:
            used_pattern.add(inp[EVAPORATION]['RECOVERY'])

    if AQUIFERS in inp:
        #  optional monthly time pattern used to adjust the upper zone evaporation fraction
        used_pattern |= set(inp[AQUIFERS].frame['Epat'].dropna().values)

    if INFLOWS in inp:
        #  optional time pattern used to adjust the baseline value on a periodic basis
        used_pattern |= set(inp[INFLOWS].frame['Pattern'].dropna().values)

    if DWF in inp:
        for i in range(1, 5):
            used_pattern |= set(inp[DWF].frame[f'pattern{i}'].dropna().values)

    if PATTERNS in inp:
        inp[PATTERNS] = inp[PATTERNS].slice_section(used_pattern)


def reduce_controls(inp):
    """
    remove unused controls

    only keep used CONTROLS the sections [CONDUIT, ORIFICE, WEIR, OUTLET / NODE, LINK, CONDUIT, PUMP, ORIFICE, WEIR, OUTLET]

    if unavailable object in condition: remove whole rule
    if unavailable object in action: remove only this action

    Args:
        inp (swmm_api.SwmmInput): inp-file data

    .. Important::
        works inplace
    """
    if CONTROLS not in inp:
        return

    # c0 = Control.create_section(inp.CONTROLS.to_inp_lines())

    links = links_dict(inp)
    nodes = nodes_dict(inp)

    for label in list(inp.CONTROLS.keys()):
        control = inp.CONTROLS[label]
        # if unavailable object in condition: remove whole rule
        for condition in control.conditions:
            if condition.kind + 'S' in inp:
                # CONDUIT PUMP ORIFICE WEIR OUTLET
                if condition.label not in inp[condition.kind + 'S']:
                    # pass  # delete
                    del inp.CONTROLS[label]
                    continue
            elif condition.kind == Control.OBJECTS.NODE:
                if condition.label not in nodes:
                    # pass  # delete
                    del inp.CONTROLS[label]
                    continue
            elif condition.kind == Control.OBJECTS.LINK:
                if condition.label not in links:
                    # pass  # delete
                    del inp.CONTROLS[label]
                    continue

        # if unavailable object in action: remove only this action
        for action in list(control.actions):
            i = control.actions.index(action)
            if action.kind + 'S' in inp:
                # CONDUIT PUMP ORIFICE WEIR OUTLET
                if action.label not in inp[action.kind + 'S']:
                    # pass  # delete
                    inp.CONTROLS[label].actions.pop(i)
            elif action.kind + 'S' in SECTION_TYPES and action.kind + 'S' not in inp:
                inp.CONTROLS[label].actions.pop(i)
            elif action.kind == Control.OBJECTS.NODE:
                if action.label not in nodes:
                    # pass  # delete
                    inp.CONTROLS[label].actions.pop(i)
            elif action.kind == Control.OBJECTS.LINK:
                if action.label not in links:
                    # pass  # delete
                    inp.CONTROLS[label].actions.pop(i)

        # if no actions left
        if not control.actions:
            del inp.CONTROLS[label]


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
    if (SUBCATCHMENTS in inp) and (RAINGAGES in inp):
        needed_raingages = {inp[SUBCATCHMENTS][s].RainGage for s in inp[SUBCATCHMENTS]}
        inp[RAINGAGES] = inp[RAINGAGES].slice_section(needed_raingages)


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


def reduce_timeseries(inp):
    if TIMESERIES not in inp:
        return

    needed_timeseries = set()
    key = EvaporationSection.KEYS.TIMESERIES  # TemperatureSection.KEYS.TIMESERIES, ...

    if RAINGAGES in inp:
        f = inp[RAINGAGES].frame
        needed_timeseries |= set(f.loc[f['Source'].str.upper() == key, 'Timeseries'])

    if EVAPORATION in inp:
        if key in inp[EVAPORATION]:
            needed_timeseries.add(inp[EVAPORATION][key])

    if TEMPERATURE in inp:
        if key in inp[TEMPERATURE]:
            needed_timeseries.add(inp[TEMPERATURE][key])

    if OUTFALLS in inp:
        f = inp[OUTFALLS].frame
        needed_timeseries |= set(f.loc[f['Type'].str.upper() == key, 'Data'])

    if INFLOWS in inp:
        f = inp[INFLOWS].frame
        needed_timeseries |= set(f['TimeSeries'])

    inp[TIMESERIES] = inp[TIMESERIES].slice_section(needed_timeseries)
