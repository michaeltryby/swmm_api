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
        alt: alternative title

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
    remove_lines = []
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
        return

    elif len(subs) == 2:
        # input summary tables
        header, data = subs
    else:
        notes, header, data = subs
    header = ['_'.join([i for i in c if i is not NaN]) for c in pd.read_fwf(StringIO(header), header=None).values.T]

    # Pumping Summary
    if '% Time Off_Pump Curve_Low   High' in header:
        header.remove('% Time Off_Pump Curve_Low   High')
        header.append('% Time Off_Pump Curve_Low')
        header.append('% Time Off_Pump Curve_High')

    df = pd.DataFrame(line.split() for line in data.split('\n'))

    last_col_values = df.iloc[:, -1].unique()
    if 'ltr' in last_col_values or 'gal' in last_col_values:
        del df[df.columns[-1]]

    for c, h in enumerate(header):
        if (('days hr:min' in h)
                or ('Recording_Frequency' in h)
                or ('Interval' in h)
                or ('CoPollutant' in h)):
            if c+1 not in df.columns:
                continue
            df[c] = df[c] + ' ' + df.pop(c+1)

    if len(df.columns) < len(header):
        df.columns = header[:len(df.columns)]
        for h in header[len(df.columns):]:
            df[h] = NaN
    else:
        df.columns = header

    df = df.set_index(header[0])

    # New error in Version 5.1.015 ????
    df = df.replace('-nan(ind)', NaN)

    for col in df:
        if 'days hr:min' in col:
            df[col] = pd.to_timedelta(df[col].str.replace('  ', ' days ') + ':00')
        else:
            df[col] = pd.to_numeric(df[col], errors='ignore')

    return df.copy()


def _routing_part_to_dict(raw):
    elements = {}
    if (raw.startswith('  All ') and raw.endswith('.')) or (raw.strip() == 'None') or (raw.strip() == ''):
        return elements

    for line in raw.split('\n'):
        line = line.split()
        elements[line[1]] = line[-1][1:-1]
    return elements


def _continuity_part_to_dict(raw):
    if raw is None:
        return {}

    df = pd.read_fwf(StringIO(raw), index_col=0, header=[0, 1, 2])

    df.columns = df.columns.droplevel(2)
    df.columns.name = None
    df.columns = ['_'.join(str(c) for c in col).strip() for col in df.columns.values]

    df.index.name = None
    df.index = df.index.str.replace('.', '', regex=False).str.strip()

    res = df.to_dict(orient='index')
    res['Continuity Error (%)'] = list(res['Continuity Error (%)'].values())[0]

    return res


def _quality_continuity_part_to_dict(raw):
    if raw is None:
        return {}
    first_line = raw.split('\n')[0]
    for word in first_line.strip(' *').split():
        if len(word) > 14:
            raw = raw.replace(word, f'{word[:14]} {word[14:]}')

    df = pd.read_fwf(StringIO(raw), index_col=0, header=[0, 1, 2])

    df.columns = df.columns.droplevel(2)
    df.columns.name = None
    df.columns = ['_'.join(str(c) for c in col).strip() for col in df.columns.values]

    df.index.name = None
    df.index = df.index.str.strip('. ')

    res = df.to_dict(orient='index')
    return res


class ReportUnitConversion:
    """
    Unit conversion for the simulation results in the report file
    
    Attributes:
        FLOW (str): for metric one of ['CMS', 'LPS', 'MLD'] | for imperial one of ['CFS', 'GPM', 'MGD']
        VOL1 (str): for metric: 'hectare-m' | for imperial:
        VOL2 (str): for metric: 'ltr' | for imperial: 'acre-feet'
        DEPTH1 (str): for metric: 'mm'| for imperial: 'gal'
        DEPTH2 (str): hydrological | for metric: 'Meters' | for imperial: 'inches'
        MASS (str): hydraulic | for metric: 'kg' | for imperial: 'Feet'
        LENGTH (str): for metric: 'm' | for imperial: 'lbs'
        VOL3 (str): for metric: 'm3' | for imperial: 'ft3'
        VELO (str): for metric: 'm/sec' | for imperial: 'ft/sec'

    Examples
    --------
    >>> ReportUnitConversion('CMS').is_metric()
    True
    >>> ReportUnitConversion('GPM').is_imperial()
    ['CFS', 'GPM', 'MGD']
    >>> ReportUnitConversion('CMS').DEPTH1
    'mm'
    """
    _METRIC_FLOWS = ['CMS', 'LPS', 'MLD']
    _IMPERIAL_FLOWS = ['CFS', 'GPM', 'MGD']

    def __init__(self, flow_unit):
        """
        Unit conversion

        Args:
            flow_unit (str): unit of simulation results in the report file
        """
        self.FLOW = flow_unit
        if self.is_metric():
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

    def is_metric(self):
        """
        Indicator whether unit is metric.

        Returns:
            bool: If unit is metric.

        See Also:
            UNIT.is_imperial : If unit is imperial.
        """
        return self.FLOW in self._METRIC_FLOWS

    def is_imperial(self):
        """
        Indicator whether unit is imperial.

        Returns:
            bool: If unit is imperial.

        See Also:
            UNIT.is_metric : If unit is metric.
        """
        return self.FLOW in self._IMPERIAL_FLOWS


class ContinuityVariables:
    def __init__(self, flow_unit):
        """
        Unit conversion

        Args:
            flow_unit (str): unit of simulation results in the report file
        """
        u = ReportUnitConversion(flow_unit)
        self.VOL_HM3 = f'Volume_{u.VOL1}'
        self.VOL_1e6L = f'Volume_10^6 {u.VOL2}'
        self.DEPTH_MM = f'Depth_{u.DEPTH1}'
