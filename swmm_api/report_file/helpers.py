__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

from io import StringIO
import pandas as pd


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
    lines = part.split('\n')

    notes = []
    data = []
    header = []

    sep_count = 0

    for line in lines:

        if len(line.strip()) == line.count('-'):  # line is only separator  OLD: '-----' in line:
            sep_count += 1
        else:
            if sep_count == 0:
                notes.append(line)
            elif sep_count == 1:
                header.append(line)
            else:
                data.append(line)

    # --------------------------------------------
    f = StringIO('\n'.join(header + data))
    df = pd.read_fwf(f, header=list(range(len(header))), index_col=0)
    df.columns = ['_'.join(str(c) for c in col if 'Unnamed:' not in c).strip() for col in df.columns.values]
    return df


def _continuity_part_to_dict(raw):
    # p = self.converted('Flow Routing Continuity')
    # title = raw[:raw.index(p)]
    df = pd.read_fwf(StringIO(raw), index_col=0, header=[0, 1, 2])

    df.columns = df.columns.droplevel(2)
    df.columns.name = None
    # df.columns.names = [None, None]
    df.columns = ['_'.join(str(c) for c in col).strip() for col in df.columns.values]

    df.index.name = None
    df.index = df.index.str.replace('.', '').str.strip()

    res = df.to_dict(orient='index')
    res['Continuity Error (%)'] = res['Continuity Error (%)']['Volume_hectare-m']

    # res = dict()
    # for line in p.split('\n'):
    #     key, *values = line.split()
    #     if '..' in line:
    #         key = line[:line.find('..')].strip()
    #         value = line[line.rfind('..') + 2:].strip()
    #         res[key] = value

    return res
