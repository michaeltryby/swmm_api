import os
from statistics import mean

import pandas as pd

from .collection import nodes_dict, links_dict
from .graph import links_connected
from .tags import get_subcatchment_tags, get_node_tags
from ..inp import SwmmInput
from ..section_labels import *
from ..section_lists import LINK_SECTIONS, NODE_SECTIONS
from ..sections import TimeseriesFile
from ..sections.link import _Link
from ..sections.link_component import CrossSection

"""
a collection of macros to manipulate an inp-file

use this file as an example for the usage of this package
"""


########################################################################################################################
def find_node(inp: SwmmInput, label):
    """
    find node in inp-file data

    Args:
        inp (SwmmInput): inp-file data
        label (str): node Name/label

    Returns:
        _Node | Junction | swmm_api.input_file.sections.node.Storage | Outfall: searched node (if not found None)
    """
    return nodes_dict(inp).get(label, None)


def find_link(inp: SwmmInput, label):
    """
    find link in inp-file data

    Args:
        inp (SwmmInput): inp-file data
        label (str): link Name/label

    Returns:
        _Link | Conduit | Weir | Outlet | Orifice | Pump: searched link (if not found None)
    """
    return links_dict(inp).get(label, None)


########################################################################################################################
def calc_slope(inp: SwmmInput, conduit):
    """
    calculate the slop of a conduit

    Args:
        inp (SwmmInput): inp-file data
        conduit (Conduit): link

    Returns:
        float: slop of the link
    """
    nodes = nodes_dict(inp)
    return (nodes[conduit.FromNode].Elevation + conduit.InOffset - (
            nodes[conduit.ToNode].Elevation + conduit.OutOffset)) / conduit.Length


def conduit_slopes(inp: SwmmInput):
    """
    get the slope of all conduits

    Args:
        inp (SwmmInput):

    Returns:
        pandas.Series: slopes
    """
    slopes = {}
    for conduit in inp.CONDUITS.values():
        slopes[conduit.Name] = calc_slope(inp, conduit)
    return pd.Series(slopes)


########################################################################################################################
def _rel_diff(a, b):
    m = mean([a + b])
    if m == 0:
        return abs(a - b)
    return abs(a - b) / m


def _rel_slope_diff(inp: SwmmInput, l0, l1):
    nodes = nodes_dict(inp)
    slope_res = (nodes[l0.FromNode].Elevation + l0.InOffset
                 - (nodes[l1.ToNode].Elevation + l1.OutOffset)
                 ) / (l0.Length + l1.Length)
    return _rel_diff(calc_slope(inp, l0), slope_res)


########################################################################################################################
def conduits_are_equal(inp: SwmmInput, link0, link1, diff_roughness=0.1, diff_slope=0.1, diff_height=0.1):
    """
    check if the links (with all there components) are equal

    Args:
        inp (SwmmInput):
        link0 (Conduit | Weir | Outlet | Orifice | Pump | _Link): first link
        link1 (Conduit | Weir | Outlet | Orifice | Pump | _Link): second link
        diff_roughness (float): difference from which it is considered different.
        diff_slope (float): difference from which it is considered different.
        diff_height (float): difference from which it is considered different.

    Returns:
        bool: if the links are equal
    """
    all_checks_out = True

    # Roughness values match within a specified percent tolerance
    if diff_roughness is not None:
        all_checks_out &= _rel_diff(link0.Roughness, link1.Roughness) < diff_roughness

    xs0 = inp[XSECTIONS][link0.Name]  # type: CrossSection
    xs1 = inp[XSECTIONS][link1.Name]  # type: CrossSection

    # Diameter values match within a specified percent tolerance (1 %)
    if diff_height is not None:
        all_checks_out &= _rel_diff(xs0.Geom1, xs1.Geom1) < diff_height

    # Cross-section shapes must match exactly
    all_checks_out &= xs0.Shape == xs1.Shape

    # Shape curves must match exactly
    if xs0.Shape == CrossSection.SHAPES.CUSTOM:
        all_checks_out &= xs0.Curve == xs1.Curve

    # Transects must match exactly
    elif xs0.Shape == CrossSection.SHAPES.IRREGULAR:
        all_checks_out &= xs0.Tsect == xs1.Tsect

    # Slope values match within a specified tolerance
    if diff_slope is not None:
        rel_slope_diff = _rel_diff(calc_slope(inp, link0), calc_slope(inp, link1))

        # if rel_slope_diff < 0:
        #     nodes = nodes_dict(inp)
        #     print(nodes[link0.FromNode].Elevation, link0.InOffset, nodes[link0.ToNode].Elevation, link0.OutOffset)
        #     print(nodes[link1.FromNode].Elevation, link1.InOffset, nodes[link1.ToNode].Elevation, link1.OutOffset)
        #     print('rel_slope_diff < 0', link0, link1)
        all_checks_out &= rel_slope_diff < diff_slope

    return all_checks_out


def update_no_duplicates(inp_base, inp_update) -> SwmmInput:
    inp_new = inp_base.copy()
    inp_new.update(inp_update)

    for node in nodes_dict(inp_new):
        if sum((node in inp_new[s] for s in NODE_SECTIONS + [SUBCATCHMENTS] if s in inp_new)) != 1:
            for s in NODE_SECTIONS + [SUBCATCHMENTS]:
                if (s in inp_new) and (node in inp_new[s]) and (node not in inp_update[s]):
                    del inp_new[s][node]

    for link in links_dict(inp_new):
        if sum((link in inp_new[s] for s in LINK_SECTIONS if s in inp_new)) != 1:
            for s in LINK_SECTIONS:
                if (s in inp_new) and (link in inp_new[s]) and (link not in inp_update[s]):
                    del inp_new[s][link]

    return inp_new


########################################################################################################################
def increase_max_node_depth(inp, node_label):
    # swmm raises maximum node depth to surrounding xsection height
    previous_, next_ = links_connected(inp, node_label)
    node = nodes_dict(inp)[node_label]
    max_height = node.MaxDepth
    for link in previous_ + next_:
        max_height = max((max_height, inp[XSECTIONS][link.Name].Geom1))
    print(f'MaxDepth increased for node "{node_label}" from {node.MaxDepth} to {max_height}')
    node.MaxDepth = max_height


def set_times(inp, start, end, head=None, tail=None):
    """
    set start and end time of the inp-file

    Args:
        inp (SwmmInput): inp data
        start (datetime.datetime): start time of the simulation and the reporting
        end (datetime.datetime): end time of the simulation
        head (datetime.timedelta): brings start time forward
        tail (datetime.timedelta): brings end time backward

    Returns:
        SwmmInput: changed inp data
    """
    if head is None:
        sim_start = start
    else:
        sim_start = start - head

    if tail is None:
        end = end
    else:
        end = end + tail

    report_start = start
    inp[OPTIONS]['START_DATE'] = sim_start.date()
    inp[OPTIONS]['START_TIME'] = sim_start.time()
    inp[OPTIONS]['REPORT_START_DATE'] = report_start.date()
    inp[OPTIONS]['REPORT_START_TIME'] = report_start.time()
    inp[OPTIONS]['END_DATE'] = end.date()
    inp[OPTIONS]['END_TIME'] = end.time()
    return inp


def combined_subcatchment_frame(inp: SwmmInput):
    """
    combine all information of the subcatchment data-frames

    Args:
        inp (SwmmInput): inp-file data

    Returns:
        pandas.DataFrame: combined subcatchment data
    """
    df = inp[SUBCATCHMENTS].frame.join(inp[SUBAREAS].frame).join(inp[INFILTRATION].frame)
    df = df.join(get_subcatchment_tags(inp))
    return df


def combined_nodes_frame(inp: SwmmInput):
    pass  # TODO


def nodes_data_frame(inp, label_sep='.'):
    nodes_tags = get_node_tags(inp)
    res = None
    for s, _ in iter_sections(inp, NODE_SECTIONS):
        df = inp[s].frame.rename(columns=lambda c: f'{label_sep}{c}')

        if s == STORAGE:
            df[f'{STORAGE}{label_sep}Curve'] = df[f'{STORAGE}{label_sep}Curve'].astype(str)

        for sub_sec in [DWF, INFLOWS]:
            if sub_sec in inp:
                x = inp[sub_sec].frame.unstack(1)
                x.columns = [f'{label_sep}'.join([sub_sec, c[1], c[0]]) for c in x.columns]
                df = df.join(x)

        df = df.join(inp[COORDINATES].frame).join(nodes_tags)

        if res is None:
            res = df
        else:
            res = res.append(df)
    return res


def iter_sections(inp, section_list):
    for s in section_list:
        if s in inp:
            yield s, inp[s]


def delete_sections(inp, section_list):
    for s in section_list:
        if s in inp:
            del inp[s]


def set_absolute_file_paths(inp, path_data_base):
    """

    Args:
        inp (SwmmInput):
        path_data_base:

    Returns:

    """
    if FILES in inp:
        pass  # ?

    if RAINGAGES in inp:
        for rg in inp.RAINGAGES.values():
            if isinstance(rg.Filename, str):
                rg.Filename = os.path.join(path_data_base, rg.Filename)

    if TEMPERATURE in inp:
        if 'FILE' in inp.TEMPERATURE:
            inp.TEMPERATURE['FILE'] = os.path.join(path_data_base, inp.TEMPERATURE['FILE'])

    if TIMESERIES in inp:
        for ts in inp.TIMESERIES.values():
            if isinstance(ts, TimeseriesFile):
                ts.filename = os.path.join(path_data_base, ts.filename)
