__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

from io import StringIO
import pandas as pd
import re
from numpy import NaN


def _get_title_of_part(part, alt):
    """
    read title in part text of the report file

    Args:
        part (str): string of a part in the report file
        alt (str): alternative title

    Returns:
        str: title of the part
    """
    if 'EPA STORM WATER MANAGEMENT MODEL - VERSION' in part:
        return 'Version+Title'

    elif 'NOTE:' in part:
        return 'Note'

    else:
        lines = part.split('\n')
        for no, line in enumerate(lines):
            if no == 0 or no == len(lines) - 1:
                continue
            if '***' in lines[no + 1] and '***' in lines[no - 1]:
                start_char = lines[no - 1].index('*')
                len_title = lines[no - 1].count('*')
                return line[start_char:start_char + len_title].strip()
        return str(alt)


def _remove_lines(part, title=True, empty=False, sep=False):
    """
    remove unneeded lines of part string

    Args:
        part (str): part in report file
        title (bool): if title should be removed
        empty (bool): if empty lines should be removed
        sep (bool):  if separator should be removed

    Returns:
        str: converted part
    """
    lines = part.split('\n')
    remove_lines = list()
    for no, line in enumerate(lines):

        if title:
            if no == 0 or no == len(lines) - 1:
                continue
            if '***' in lines[no + 1] and '***' in lines[no - 1]:
                remove_lines.append(no - 1)
                remove_lines.append(no)
                remove_lines.append(no + 1)

        if empty:
            if len(line.strip()) == 0:
                remove_lines.append(no)

        if sep:
            if len(line.replace('-', '').strip()) == 0:
                remove_lines.append(no)

    new_lines = lines
    for r in sorted(remove_lines, reverse=True):
        new_lines.pop(r)

    return '\n'.join(new_lines)


def _part_to_frame(part):
    """
    convert the table of a part of the report file to a dataframe

    Args:
        part (str): part of the report file

    Returns:
        pandas.DataFrame: some kind of summary table
    """
    subs = re.split(r"\s*-+\n", part)
    if len(subs) == 4:
        notes, header, data, sytem = subs
    elif len(subs) == 1:
        # no data
        return pd.DataFrame()
    else:
        notes, header, data = subs
    header = ['_'.join([i for i in c if i is not NaN]) for c in pd.read_fwf(StringIO(header), header=None).values.T]
    # re.split(r"\s\s\s+", line.strip())
    df = pd.DataFrame(line.split() for line in data.split('\n'))

    if 'ltr' in df.iloc[:, -1].unique():
        del df[df.columns[-1]]

    for c, h in enumerate(header):
        if 'days hr:min' in h:
            df[c] = df[c] + ' ' + df.pop(c+1)

    df.columns = header

    df = df.set_index(header[0])

    # New error in Version 5.1.015 ????
    df = df.replace('-nan(ind)', NaN)

    for col in df:
        if 'Type' in col:
            pass
        elif 'days hr:min' in col:
            df[col] = pd.to_timedelta(df[col].str.replace('  ', ' days ') + ':00')
        else:
            df[col] = df[col].astype(float)
    #
    # notes = str()
    # data = []
    # header = []
    # sep_count = 0
    # for line in part.split('\n'):
    #     if len(line.strip()) == line.count('-'):  # line is only separator  OLD: '-----' in line:
    #         sep_count += 1
    #     elif sep_count == 0:
    #         notes += line + '\n'
    #     elif sep_count == 1:
    #         header.append(line)
    #     else:
    #         data.append(line)
    #
    # # --------------------------------------------
    # df = pd.read_fwf(StringIO('\n'.join(header)), header=list(range(len(header))))
    # rename_cols = lambda col: '_'.join(str(c) for c in col if 'Unnamed:' not in c).strip().replace('_/', '/').replace(
    #     '/_', '/')
    # df.columns = [rename_cols(col) for col in df.columns.to_list()]
    #
    # df = pd.read_fwf(StringIO('\n'.join(header + data)),
    #                  header=list(range(len(header))), index_col=0)
    # rename_cols = lambda col: '_'.join(str(c) for c in col if 'Unnamed:' not in c).strip().replace('_/', '/').replace('/_', '/')
    # df.columns = [rename_cols(col) for col in df.columns.to_list()]
    # for col in df:
    #     if 'Type' in col:
    #         pass
    #     elif 'days hr:min' in col:
    #         df[col] = pd.to_timedelta(df[col].str.replace('  ', ' days ') + ':00')
    #     else:
    #         df[col] = df[col].astype(float)
    return df.copy()


def _continuity_part_to_dict(raw):
    # p = self.converted('Flow Routing Continuity')
    # title = raw[:raw.index(p)]
    if raw is None:
        return dict()

    df = pd.read_fwf(StringIO(raw), index_col=0, header=[0, 1, 2])

    df.columns = df.columns.droplevel(2)
    df.columns.name = None
    # df.columns.names = [None, None]
    df.columns = ['_'.join(str(c) for c in col).strip() for col in df.columns.values]

    df.index.name = None
    df.index = df.index.str.replace('.', '', regex=False).str.strip()

    res = df.to_dict(orient='index')
    res['Continuity Error (%)'] = list(res['Continuity Error (%)'].values())[0]

    # res = dict()
    # for line in p.split('\n'):
    #     key, *values = line.split()
    #     if '..' in line:
    #         key = line[:line.find('..')].strip()
    #         value = line[line.rfind('..') + 2:].strip()
    #         res[key] = value

    return res


# def get_item_in_line(line, item):
#     return float([v.strip() for v in line.split()][item])

class UNIT:
    _METRIC_FLOWS = ['CMS', 'LPS', 'MLD']
    _IMPERIAL_FLOWS = ['CFS', 'GPM', 'MGD']

    def __init__(self, flow_unit):
        self.FLOW = flow_unit
        if flow_unit in self._METRIC_FLOWS:
            self.VOL1 = 'hectare-m'
            self.VOL2 = 'ltr'
            self.DEPTH1 = 'mm'  # hydrological
            self.DEPTH2 = 'Meters'  # hydraulic
            self.MASS = 'kg'
            self.LENGTH = 'm'
        else:
            self.VOL1 = 'acre-feet'
            self.VOL2 = 'gal'
            self.DEPTH1 = 'inches'  # hydrological
            self.DEPTH2 = 'Feet'  # hydraulic
            self.MASS = 'lbs'
            self.LENGTH = 'ft'

        self.VOL3 = self.LENGTH + '3'
        self.VELO = self.LENGTH + '/sec'


class VARS:
    class CONTINUITY:
        VOL_HM3 = 'Volume_hectare-m'
        VOL_1e6L = 'Volume_10^6 ltr'
        DEPTH_MM = 'Depth_mm'

    class CONTINUITY_imp:
        VOL_HM3 = 'Volume_acre-feet'
        VOL_1e6L = 'Volume_10^6 gal'
        DEPTH_MM = 'Depth_inches'
