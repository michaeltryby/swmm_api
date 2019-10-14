from pandas import DataFrame, Series, set_option as set_pandas_options

from .inp_helpers import InpSection, dataframe_to_inp_string, InpSectionGeneric
from .helpers.type_converter import type2str
from .helpers.sections import *

set_pandas_options("display.max_colwidth", 10000)


def curves2string(cat):
    if isinstance(cat, list):  # fast: not converted
        return general_category2string(cat)

    def get_names(shape):
        return {'shape': ['x', 'y'],
                'storage': ['h', 'A']}.get(shape.lower(), ['x', 'y'])

    f = ''
    for k in cat:
        for n in cat[k]:
            a, b = get_names(k)
            df = cat[k][n].copy()
            if k == 'shape':
                df = df[(df[a] != 0.) & (df[a] != 1.)].copy()
                df = df.reset_index(drop=True)
            df['Name'] = n
            df['Type'] = ''
            df.loc[0, 'Type'] = k
            df = df[['Name', 'Type', a, b]].copy().rename(columns={'Name': ';Name'})
            # print(df.applymap(type2str).to_string(index=None, justify='center'))
            f += (df.applymap(type2str).to_string(index=None, justify='center'))
            f += '\n'
    return f


def timeseries2string(cat):
    if isinstance(cat, list):  # fast: not converted
        return general_category2string(cat)
    f = ''
    for n in cat:
        if n == 'Files':
            # print(';' + n)
            f += general_category2string(cat[n])
            continue
        df = cat[n].copy()
        df['Date  Time'] = df.index.strftime('%m/%d/%Y %H:%M')
        df.columns.name = ';Name'
        df['<'] = n
        df.index = df['<'].rename(None)
        del df['<']
        df = df[['Date  Time', 'Value']].copy()
        f += df.to_string()
        f += '\n'
    return f


def tags2string(cat):
    f = ''
    max_len_type = len(max(cat.keys(), key=len)) + 2
    for type_, tags in cat.items():
        max_len_name = len(max(tags.keys(), key=len)) + 2
        for name, tag in tags.items():
            f += '{{:<{len1}}} {{:<{len2}}} {{}}\n'.format(len1=max_len_type, len2=max_len_name).format(type_, name,
                                                                                                        tag)
    return f


def general_category2string(cat, fast=False):
    f = ''

    # ----------------------
    if isinstance(cat, str):  # Title
        f += cat

    # ----------------------
    elif isinstance(cat, list):  # V0.1
        for line in cat:
            f += type2str(line) + '\n'

    # ----------------------
    elif isinstance(cat, dict):  # V0.2

        max_len = len(max(cat.keys(), key=len)) + 2
        for sub in cat:
            f += '{key}{value}'.format(key=sub.ljust(max_len),
                                       value=type2str(cat[sub]) + '\n')

    # ----------------------
    elif isinstance(cat, (DataFrame, Series)):  # V0.3
        if cat.empty:
            f += '; NO data'

        if isinstance(cat, DataFrame):
            f += dataframe_to_inp_string(cat)

        elif isinstance(cat, Series):
            f += cat.apply(type2str).to_string()

    # ----------------------
    elif isinstance(cat, InpSection):  # V0.4
        f += cat.to_inp(fast=fast)

    # ----------------------
    elif isinstance(cat, InpSectionGeneric):  # V0.5
        f += cat.to_inp(fast=fast)

    # ----------------------
    f += '\n'
    return f


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


def inp2string(inp, fast=False):
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
        f += ('\n;' + '_' * 100 + '\n')
        f += ('[{}]\n'.format(head))
        cat = inp[head]

        # if head == CURVES:
        #     f += curves2string(cat)
        if head == TIMESERIES:
            f += timeseries2string(cat)
        elif head == TAGS:
            f += tags2string(cat)
        else:
            f += general_category2string(cat, fast=fast)

    return f


def write_inp_file(inp, filename, fast=False):
    """
    write new .inp file

    Args:
        inp (swmm_api.input_file.inp_helpers.InpData):
        filename (str): path/filename of resulting .inp-file
        fast (bool): dont use any formatting else format as table
    """
    with open(filename, 'w') as f:
        f.write(inp2string(inp, fast=fast))
