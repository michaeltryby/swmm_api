import pandas as pd
from io import StringIO


def get_item_in_line(line, item):
    return float([v.strip() for v in line.split()][item])


def report_to_dict(fn):
    parts = dict()

    with open(fn, 'r') as file:
        lines = file.readlines()
    parts0 = ''.join(lines).split('\n  \n  ****')

    for i, part in enumerate(parts0):
        if part.startswith('*'):
            part = '  ****' + part

        parts[get_title_of_part(part, i)] = convert_part(part, remove_title=False, remove_empty=True, remove_sep=False)

    return parts


def get_title_of_part(part, alt):
    if 'EPA STORM WATER MANAGEMENT MODEL - VERSION' in part:
        return 'Version+Titel'

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


def convert_part(part, remove_title=True, remove_empty=False, remove_sep=False):
    """ remove title lines and empty lines """
    lines = part.split('\n')
    remove_lines = list()
    for no, line in enumerate(lines):

        if remove_title:
            if no == 0 or no == len(lines) - 1:
                continue
            if '***' in lines[no + 1] and '***' in lines[no - 1]:
                remove_lines.append(no - 1)
                remove_lines.append(no)
                remove_lines.append(no + 1)

        if remove_empty:
            if len(line.strip()) == 0:
                remove_lines.append(no)

        if remove_sep:
            if len(line.replace('-', '').strip()) == 0:
                remove_lines.append(no)

    new_lines = lines
    for r in sorted(remove_lines, reverse=True):
        new_lines.pop(r)

    return '\n'.join(new_lines)


def part_to_df(part):
    df = pd.read_fwf(StringIO(part), index_col=0)
    df.replace('-', ' ')
    return df


def check_report(fn):
    parts = report_to_dict(fn)
    res = dict()
    #########################################################################
    p = parts['Flow Routing Continuity']
    for line in p.split('\n'):
        if 'Wet Weather Inflow' in line:
            res['Gesamter Oberflächenabfluss'] = get_item_in_line(line, -1) * 1000

        elif 'Continuity Error (%)' in line:
            res['Routingfehler'] = get_item_in_line(line, -1)

    #########################################################################
    p = parts['Outfall Loading Summary']
    res['Überlaufvolumen MÜB'] = 0
    for line in p.split('\n'):
        if 'OF_MUEN' in line:
            res['Überlaufvolumen MÜ-Nord'] = get_item_in_line(line, -1) * 1000

        elif 'OF_MUEB_BUE' in line:
            res['Überlaufvolumen MÜB'] += get_item_in_line(line, -1) * 1000

        elif 'OF_MUEB_KUE' in line:
            res['Überlaufvolumen MÜB'] += get_item_in_line(line, -1) * 1000

        elif 'OF_ARA' in line:
            vals = [v.strip() for v in line.split()]
            res['Abfluss zur ARA'] = float(vals[-1]) * 1000
    return res


def check_report2(fn):
    df = get_flooding_report(fn)
    return df.index.tolist()


def get_flooding_report(fn):
    parts = report_to_dict(fn)

    # --------------------------------------------
    p = convert_part(parts['Node Flooding Summary'], remove_title=True, remove_empty=False)

    if 'No nodes were flooded.' in p:
        return pd.DataFrame()

    lines = p.split('\n')

    notes = []
    data = []
    header = []

    sep_count = 0

    for line in lines:
        if '-----' in line:
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


def get_runoff_report(fn):
    df = get_subcatchment_report(fn)
    return df['Total_Runoff_10^6 ltr'].copy() * 1000


def get_subcatchment_report(fn):
    parts = report_to_dict(fn)

    # --------------------------------------------
    p = convert_part(parts['Subcatchment Runoff Summary'], remove_title=True, remove_empty=False)

    lines = p.split('\n')

    notes = []
    data = []
    header = []

    sep_count = 0

    for line in lines:
        if '-----' in line:
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


def get_overflow_report(fn):
    df = get_outfall_report(fn)
    return df['Total_Volume_10^6 ltr'].copy() * 1000


def get_outfall_report(fn):
    parts = report_to_dict(fn)

    # --------------------------------------------
    p = convert_part(parts['Outfall Loading Summary'], remove_title=True, remove_empty=False)

    lines = p.split('\n')

    notes = []
    data = []
    header = []

    sep_count = 0

    for line in lines:
        if '-----' in line:
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
