from pandas import DataFrame, Series, set_option as set_pandas_options

from .inp_helpers import InpSection, dataframe_to_inp_string, InpSectionGeneric
from .helpers.type_converter import type2str
from .helpers.sections import *

set_pandas_options("display.max_colwidth", 10000)

sections_order = [TITLE,
                  OPTIONS,
                  REPORT,
                  EVAPORATION,
                  TEMPERATURE,

                  JUNCTIONS,
                  DWF,
                  OUTFALLS,
                  STORAGE,

                  CONDUITS,
                  WEIRS,
                  ORIFICES,
                  OUTLETS,

                  LOSSES,
                  XSECTIONS,

                  INFLOWS,
                  CURVES,
                  TIMESERIES,
                  RAINGAGES,

                  SUBCATCHMENTS,
                  SUBAREAS,
                  INFILTRATION,

                  POLLUTANTS,
                  LOADINGS,

                  PATTERNS]


def _sort_by(key):
    if key in sections_order:
        return sections_order.index(key)
    else:
        return len(sections_order)


def section_to_string(section, fast=True):
    f = ''

    # ----------------------
    if isinstance(section, str):  # Title
        f += section

    # ----------------------
    elif isinstance(section, list):  # V0.1
        for line in section:
            f += type2str(line) + '\n'

    # ----------------------
    elif isinstance(section, dict):  # V0.2

        max_len = len(max(section.keys(), key=len)) + 2
        for sub in section:
            f += '{key}{value}'.format(key=sub.ljust(max_len),
                                       value=type2str(section[sub]) + '\n')

    # ----------------------
    elif isinstance(section, (DataFrame, Series)):  # V0.3
        if section.empty:
            f += '; NO data'

        if isinstance(section, DataFrame):
            f += dataframe_to_inp_string(section)

        elif isinstance(section, Series):
            f += section.apply(type2str).to_string()

    # ----------------------
    elif isinstance(section, (InpSection, InpSectionGeneric)):  # V0.4
        f += section.to_inp(fast=fast)

    # ----------------------
    f += '\n'
    return f


def inp2string(inp, fast=True):
    """
    create string of inp file

    Args:
        inp (swmm_api.input_file.inp_helpers.InpData):
        fast (bool): dont use any formatting else format as table

    Returns:
        str: string of input file
    """
    f = ''
    for head in sorted(inp.keys(), key=_sort_by):
        f += '\n' + ';' + '_' * 100 + '\n' + '[{}]\n'.format(head)
        section_data = inp[head]
        f += section_to_string(section_data, fast=fast)
    return f


def write_inp_file(inp, filename, fast=True):
    """
    write new .inp file

    Args:
        inp (swmm_api.input_file.inp_helpers.InpData):
        filename (str): path/filename of resulting .inp-file
        fast (bool): dont use any formatting else format as table
    """
    with open(filename, 'w') as f:
        f.write(inp2string(inp, fast=fast))
