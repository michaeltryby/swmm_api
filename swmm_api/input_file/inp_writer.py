from .inp_helpers import InpSection, InpSectionGeneric, InpData, inp_sep
from .inp_sections.labels import *

sections_order = [TITLE,
                  OPTIONS,
                  REPORT,
                  EVAPORATION,
                  TEMPERATURE,

                  JUNCTIONS,
                  OUTFALLS,
                  STORAGE,
                  DWF,
                  INFLOWS,

                  CONDUITS,
                  WEIRS,
                  ORIFICES,
                  OUTLETS,

                  LOSSES,
                  XSECTIONS,
                  TRANSECTS,

                  CURVES,
                  TIMESERIES,
                  RAINGAGES,
                  PATTERNS,

                  SUBCATCHMENTS,
                  SUBAREAS,
                  INFILTRATION,

                  POLLUTANTS,
                  LOADINGS,
                  ]


def _sort_by(key):
    if key in sections_order:
        return sections_order.index(key)
    else:
        return len(sections_order)


def section_to_string(section, fast=True):
    """
    create a string of a section in an ``.inp``-file

    Args:
        section (swmm_api.input_file.inp_helpers.InpSection | swmm_api.input_file.inp_helpers.InpSectionGeneric):
            section of an ``.inp``-file
        fast (bool): don't use any formatting else format as table

    Returns:
        str: string of the ``.inp``-file section
    """
    f = ''

    # ----------------------
    if isinstance(section, str):  # Title
        f += section.replace(inp_sep, '').strip()

    # ----------------------
    # elif isinstance(section, list):  # V0.1
    #     for line in section:
    #         f += type2str(line) + '\n'
    #
    # # ----------------------
    # elif isinstance(section, dict):  # V0.2
    #     max_len = len(max(section.keys(), key=len)) + 2
    #     for sub in section:
    #         f += '{key}{value}'.format(key=sub.ljust(max_len),
    #                                    value=type2str(section[sub]) + '\n')
    #
    # ----------------------
    # elif isinstance(section, (DataFrame, Series)):  # V0.3
    #     if section.empty:
    #         f += ';; NO data'
    #
    #     if isinstance(section, DataFrame):
    #         f += dataframe_to_inp_string(section)
    #
    #     elif isinstance(section, Series):
    #         f += section.apply(type2str).to_string()

    # ----------------------
    elif isinstance(section, (InpSection, InpSectionGeneric)):  # V0.4
        f += section.to_inp_lines(fast=fast)

    # ----------------------
    f += '\n'
    return f


def inp_to_string(inp: InpData, fast=True):
    """
    create the string of a new ``.inp``-file

    Args:
        inp (swmm_api.input_file.inp_helpers.InpData): dict-like Input-file data with several sections
        fast (bool): don't use any formatting else format as table

    Returns:
        str: string of input file text
    """
    f = ''
    sep = f'\n{inp_sep}\n[{{}}]\n'
    # sep = f'\n[{{}}]  ;;{"_" * 100}\n'
    for head in sorted(inp.keys(), key=_sort_by):
        f += sep.format(head)
        section_data = inp[head]
        f += section_to_string(section_data, fast=fast)
    return f


def write_inp_file(inp: InpData, filename, fast=True):
    """
    create/write a new ``.inp``-file

    Args:
        inp (InpData): dict-like ``.inp``-file data with several sections
        filename (str): path/filename of created ``.inp``-file
        fast (bool): don't use any formatting else format as table
    """
    with open(filename, 'w') as f:
        f.write(inp_to_string(inp, fast=fast))
