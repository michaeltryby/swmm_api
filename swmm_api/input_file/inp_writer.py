from pandas import DataFrame, Series, set_option as set_pandas_options

from .inp_helpers import InpSection, dataframe_to_inp_string
from .helpers.type_converter import type2str
import yaml

set_pandas_options("display.max_colwidth", 10000)


def curves2string(cat):
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


def list2string(line):
    return ' '.join(type2str(l) for l in line)


def line2string(line):
    f = ''
    if isinstance(line, str):
        f += line
    elif isinstance(line, list):
        f += list2string(line)
    else:
        f += type2str(line)
    f += '\n'
    return f


def pandas2string(cat):
    if cat.empty:
        return '; NO data'
    f = ''
    if isinstance(cat, DataFrame):
        f += dataframe_to_inp_string(cat)

    elif isinstance(cat, Series):
        f += cat.apply(type2str).to_string()
    else:
        raise NotImplementedError()
    return f


def general_category2string(cat):
    f = ''

    if isinstance(cat, str):  # Title
        f += cat

    elif isinstance(cat, list):  # V0.1
        for line in cat:
            f += line2string(line)

    elif isinstance(cat, dict):  # V0.2
        for sub in cat:
            f += sub + ' ' + line2string(cat[sub])

    elif isinstance(cat, (DataFrame, Series)):  # V0.3
        f += pandas2string(cat)

    elif isinstance(cat, InpSection):  # V0.4
        f += str(cat)

    f += '\n'
    return f


sections = ['TITLE',
            'OPTIONS',
            'REPORT',
            'EVAPORATION',

            'JUNCTIONS',
            'DWF',
            'OUTFALLS',
            'STORAGE',

            'CONDUITS',
            'WEIRS',
            'ORIFICES',
            'OUTLETS',

            'LOSSES',
            'XSECTIONS',

            'INFLOWS',
            'CURVES',
            'TIMESERIES',
            'RAINGAGES',

            'SUBCATCHMENTS',
            'SUBAREAS',
            'INFILTRATION',

            'POLLUTANTS',
            'LOADINGS',

            'PATTERNS']


def inp2string(network):
    f = ''
    for head in sections:
        if head not in network:
            continue
        f += ('\n;' + '_' * 100 + '\n')
        f += ('[{}]\n'.format(head))
        cat = network[head]

        if head == 'CURVES':
            f += curves2string(cat)
            continue

        if head == 'TIMESERIES':
            f += timeseries2string(cat)
            continue

        f += general_category2string(cat)
    return f


def write_inp_file(network, filename):
    with open(filename, 'w') as f:
        f.write(inp2string(network))


def network2yaml(network, fn):
    basic_nw = network.copy()
    for head, data in basic_nw.items():
        if isinstance(data, DataFrame):
            basic_nw[head] = data.applymap(type2str).to_dict(orient='index')
        elif isinstance(data, Series):
            basic_nw[head] = data.apply(type2str).to_dict()

    yaml.dump(basic_nw, open(fn + '.yaml', 'w'), default_flow_style=False)
