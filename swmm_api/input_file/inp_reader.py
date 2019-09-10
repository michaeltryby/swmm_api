import re

from .inp_sections import *
from .inp_helpers import InpSection, optional_args
from swmm_api.type_converter import infer_type
from pandas import DataFrame, Series, to_datetime
from numpy import NaN
from mp.helpers import timeit


def convert_title(lines):
    title = '\n'.join([' '.join([str(word) for word in line]) for line in lines])
    # print(general_category2string(title))
    return title


def convert_options(lines):
    """
    * .. defaults

    FLOW_UNITS           CFS*/GPM/MGD/CMS/LPS/MLD
    INFILTRATION         HORTON* / MODIFIED_HORTON / GREEN_AMPT / MODIFIED_GREEN_AMPT / CURVE_NUMBER
    FLOW_ROUTING         STEADY / KINWAVE* / DYNWAVE
    LINK_OFFSETS         DEPTH* / ELEVATION
    FORCE_MAIN_EQUATION  H-W* / D-W
    IGNORE_RAINFALL      YES / NO*
    IGNORE_SNOWMELT      YES / NO*
    IGNORE_GROUNDWATER   YES / NO*
    IGNORE_RDII          YES / NO*
    IGNORE_ROUTING       YES / NO*
    IGNORE_QUALITY       YES / NO*
    ALLOW_PONDING        YES / NO*
    SKIP_STEADY_STATE    YES / NO*
    SYS_FLOW_TOL         value (5)
    LAT_FLOW_TOL         value (5)
    START_DATE           month/day/year (1/1/2002)
    START_TIME           hours:minutes (0:00:00)
    END_DATE             month/day/year (START_DATE)
    END_TIME             hours:minutes (24:00:00)
    REPORT_START_DATE    month/day/year (START_DATE)
    REPORT_START_TIME    hours:minutes (START_TIME)
    SWEEP_START          month/day (1/1)
    SWEEP_END            month/day (12/31)
    DRY_DAYS             days (0)
    REPORT_STEP          hours:minutes:seconds (0:15:00)
    WET_STEP             hours:minutes:seconds (0:05:00)
    DRY_STEP             hours:minutes:seconds (1:00:00)
    ROUTING_STEP         seconds (600)
    LENGTHENING_STEP     seconds (0)
    VARIABLE_STEP        value (0)
    MINIMUM_STEP         seconds (0.5)
    INERTIAL_DAMPING     NONE / PARTIAL / FULL
    NORMAL_FLOW_LIMITED  SLOPE / FROUDE / BOTH*

    MIN_SURFAREA        value (12.566 ft2 (i.e., the area of a 4-ft diameter manhole))
    MIN_SLOPE           value (0)
    MAX_TRIALS          value (8)
    HEAD_TOLERANCE      value (0.0015)
    THREADS             value (1)
    TEMPDIR             directory

    Args:
        lines (list):

    Returns:
        pandas.Series: options
    """
    new_lines = {}
    for line in lines:
        sub_head = line[0]
        if len(line) == 2:
            pass
            opt = line[1]

        else:
            raise UserWarning('?')

        new_lines[sub_head] = opt

    series = DataFrame.from_dict(new_lines, 'index')[0]  # .rename_axis('Name', axis='columns')
    # print(general_category2string(series))
    return series


def convert_report(lines):
    """
    * .. defaults
    INPUT          YES / NO*
    CONTINUITY     YES* / NO
    FLOWSTATS      YES* / NO
    CONTROLS       YES / NO*
    SUBCATCHMENTS  ALL / NONE* / <list of subcatchment names>
    NODES          ALL / NONE* / <list of node names>
    LINKS          ALL / NONE* / <list of link names>
    LID            Name Subcatch Fname

    Args:
        lines (list):

    Returns:
        pandas.Series: report
    """
    new_lines = {}
    for line in lines:
        sub_head = line[0]
        if len(line) == 2:
            opt = line[1]

        elif (sub_head == 'LID') and (len(line) == 4):
            opt = {'Name': line[1],
                   'Subcatch': line[2],
                   'Fname': line[3]}

        else:
            opt = line[1:]

        new_lines[sub_head] = opt

    series = DataFrame.from_dict(new_lines, 'index')[0]  # .rename_axis('Name', axis='columns')
    # print(general_category2string(series))
    return series


def convert_evaporation(lines):
    """
    CONSTANT    evap (0)
    MONTHLY     e1 e2 e3 e4 e5 e6 e7 e8 e9 e10 e11 e12
    TIMESERIES  Tseries
    TEMPERATURE
    FILE        (p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12)

    RECOVERY    patternID
    DRY_ONLY    NO / YES

    Use only one of the above formats (CONSTANT, MONTHLY, TIMESERIES, TEMPERATURE, or FILE)

    :param lines:
    :return:
    """
    new_lines = {}
    for line in lines:

        sub_head = line[0]
        if len(line) == 2:
            opt = line[1]

        elif sub_head == 'TEMPERATURE':
            if len(line) == 1:
                opt = ''
            else:
                raise NotImplementedError()

        elif sub_head == 'MONTHLY':
            if len(line) == 13:
                opt = line[1:]
            else:
                raise NotImplementedError()

        elif sub_head == 'FILE':
            if len(line) == 13:
                opt = line[1:]
            elif len(line) == 1:
                opt = ''
            else:
                raise NotImplementedError()

        else:
            opt = line[1:]

        new_lines[sub_head] = opt

    mult_infos = [x in new_lines for x in ['CONSTANT', 'MONTHLY', 'TIMESERIES', 'TEMPERATURE', 'FILE']]

    if sum(mult_infos) != 1:
        if sum(mult_infos) == 0:
            new_lines['CONSTANT'] = 0
        else:
            raise UserWarning('Too much evaporation')

    try:
        evaporation = DataFrame.from_dict(new_lines, 'index')[0]  # .rename_axis('Name', axis='columns')
    except:
        evaporation = Series()
        for i in new_lines:
            evaporation.loc[i] = new_lines[i]

    # print(general_category2string(report))
    return evaporation


def line_split(line):
    # but don't split quoted text
    return re.findall(r'[^"\s]\S*|".+?"', line)


def convert_timeseries(lines):
    """
    * .. defaults

    Name ( Date ) Hour Value ...
    Name Time Value ...
    Name FILE Fname

    Name    name assigned to time series.
    Date    date in Month/Day/Year format (e.g., June 15, 2001 would be 6/15/2001).
    Hour    24-hour military time (e.g., 8:40 pm would be 20:40) relative to the last date specified (or to midnight of the starting date of the simulation if no previous date was specified).
    Time    hours since the start of the simulation, expressed as a decimal number or as hours:minutes.
    Value   value corresponding to given date and time.
    Fname   name of a file in which the time series data are stored


    :param lines:
    :return:
    """
    new_lines = {}
    name = None
    for line in lines:

        if line[0] != name:
            # first line of new timeseries
            pass

        name = line[0]
        l = len(line)
        if line[1] == 'FILE':
            line = line_split(' '.join(line))
            l = len(line)
            if l == 3:
                typ = line[1]
                if 'Files' not in new_lines:
                    new_lines['Files'] = {}

                new_lines['Files'][name] = {'Type': typ,
                                            'Fname': line[2]}
            else:
                raise NotImplementedError()
        else:
            it = iter(line[1:])
            for date in it:
                if not '/' in date:
                    time = date
                    date = old_date
                else:
                    time = next(it)
                old_date = date

                if time.count(':') > 1:
                    # 00:00:00 -> 00:00
                    time = time[:5]

                # dt = datetime.datetime.combine(date, to_datetime(time, format='%H:%M').time())
                dt = '{} {}'.format(date, time)

                # value = infer_type(next(it))
                value = next(it)

                if name not in new_lines:
                    new_lines[name] = {'Datetime': [dt],
                                       'Value': [value]}
                else:
                    new_lines[name]['Datetime'].append(dt)
                    new_lines[name]['Value'].append(value)
            # TODO timeseries in .inp file
            # raise NotImplementedError('Only timeseries with FILE are allowed.')

    timeseries = new_lines.copy()

    for n in timeseries:
        if 'Datetime' in timeseries[n]:
            timeseries[n] = DataFrame.from_dict(timeseries[n], 'columns')
            timeseries[n]['Datetime'] = to_datetime(timeseries[n]['Datetime'], format='%m/%d/%Y %H:%M')
            timeseries[n] = timeseries[n].set_index('Datetime')
        else:
            timeseries[n] = DataFrame.from_dict(timeseries[n], 'index')
            timeseries[n].columns.name = 'Files'

        if 'Value' in timeseries[n]:
            timeseries[n]['Value'] = timeseries[n]['Value'].astype(float)

    # print(timeseries2string(timeseries))
    return timeseries


def convert_curves(lines):
    """
    * .. defaults
    Name Type X-value Y-value ...

    Type STORAGE / SHAPE / DIVERSION / TIDAL / PUMP1 / PUMP2 / PUMP3 / PUMP4 / RATING / CONTROL

    Name Type X-Value Y-Value

    :param lines:
    :return:
    """
    new_lines = {}
    kind = ''

    def get_names(shape):
        return {'shape': ['x', 'y'],
                'storage': ['h', 'A']}.get(shape.lower(), ['x', 'y'])

    for line in lines:

        name = line[0]
        l = len(line)

        if (l % 2) == 0:
            kind = line[1].lower()

            if kind not in new_lines:
                new_lines[kind] = {}

            remains = line[2:]
        else:
            remains = line[1:]

        a, b = get_names(kind)

        it = iter(remains)
        for x in it:
            y = next(it)
            if name not in new_lines[kind]:
                new_lines[kind].update({name: {a: [x],
                                               b: [y]}})
            else:
                new_lines[kind][name][a].append(x)
                new_lines[kind][name][b].append(y)

    curves = new_lines.copy()

    for k in curves:
        for n in curves[k]:
            curves[k][n] = DataFrame.from_dict(curves[k][n], 'columns')

    # print(curves2string(curves))
    return curves


def convert_loadings(lines):
    """
    * .. defaults

    Subcat  Pollut  InitBuildup  Pollut  InitBuildup ...

    Subcatchment Pollutant Buildup

    :param lines:
    :return:
    """
    new_lines = {}
    for line in lines:

        subcat = line[0]

        it = iter(line[1:])
        for a in it:
            b = next(it)
            if subcat not in new_lines:
                new_lines[subcat] = {'Pollutant': [a],
                                     'InitBuildup': [b]}
            else:
                new_lines[subcat]['Pollutant'].append(a)
                new_lines[subcat]['InitBuildup'].append(b)

    frame = DataFrame.from_dict(new_lines, 'index').rename_axis('Name', axis='columns')
    # print(general_category2string(frame))
    return frame


def convert_coordinates(lines):
    new_lines = {}
    for line in lines:
        name = line[0]
        new_lines[name] = {'x': line[1],
                           'y': line[2]}

    frame = DataFrame.from_dict(new_lines, 'index').rename_axis('Name', axis='columns')
    # print(general_category2string(frame))
    return frame


def convert_map(lines):
    new_lines = {}
    for line in lines:
        name = line[0]
        if name == 'DIMENSIONS':
            new_lines[name] = {'lower-left X': line[1],
                               'lower-left Y': line[2],
                               'upper-right X': line[3],
                               'upper-right Y': line[4]}
        else:
            new_lines[name] = line[1]
    return new_lines


class InpReader:
    def __init__(self, drop_gui_part=True):
        self.inp_data = None
        self.drop_gui_part = drop_gui_part
        self.gui_part = None

    convert_handler = {
        'REPORT': convert_report,
        'TITLE': convert_title,
        'OPTIONS': convert_options,
        'EVAPORATION': convert_evaporation,

        'CURVES': convert_curves,
        'TIMESERIES': convert_timeseries,

        'LOADINGS': convert_loadings,

        'COORDINATES': convert_coordinates,
        'MAP': convert_map,
    }
    new_convert_handler = {
        'CONDUITS': Conduit,
        'ORIFICES': Orifice,
        'JUNCTIONS': Junction,
        'SUBCATCHMENTS': SubCatchment,
        'SUBAREAS': SubArea,
        'DWF': DryWeatherFlow,
        'XSECTIONS': CrossSection,
        'INFILTRATION': Infiltration,
        'OUTFALLS': Outfall,
        'WEIRS': Weir,
        'STORAGE': Storage,
        'OUTLETS': Outlet,
        'LOSSES': Loss,
        'INFLOWS': Inflow,
        'RAINGAGES': RainGauge,
        'PUMPS': Pump,
        'PATTERNS': Pattern,
        'POLLUTANTS': Pollutant,
    }

    @staticmethod
    def new_convert_handler_func(lines, head):
        return InpSection.from_lines(lines, InpReader.new_convert_handler[head])  # .to_frame_()

    GUI_SECTIONS = [
                       'MAP', 'POLYGONS', 'VERTICES', 'LABELS', 'SYMBOLS', 'BACKDROP'
                   ] + ['TAGS', 'PROFILES'] + ['COORDINATES']

    # @timeit
    def read_inp(self, filename):
        if isinstance(filename, str):
            inp_file = open(filename, 'r', encoding='iso-8859-1')
        else:
            inp_file = filename

        inp_data = {}

        head = None
        for line in inp_file:
            line = line.strip()
            if line == '' or line.startswith(';'):
                continue

            elif line.startswith('[') and line.endswith(']'):
                head = line.replace('[', '').replace(']', '').upper()
                inp_data[head] = list()

            else:
                if (head == 'TIMESERIES') or (self.drop_gui_part and head in InpReader.GUI_SECTIONS):
                    # to much data
                    # saves time
                    # type conversion in "convert_timeseries"
                    inp_data[head].append(line.split())
                else:
                    inp_data[head].append([infer_type(i) for i in line.split() if i != ''])

        self.inp_data = inp_data

    # @timeit
    def convert_sections(self):
        # very slowly, i still make somethink wrong
        # from dask import delayed

        # @delayed
        def convert_head(head, lines):
            if head in InpReader.convert_handler:
                return InpReader.convert_handler[head](lines)
            elif head in InpReader.new_convert_handler:
                return InpReader.new_convert_handler_func(lines, head)

        # ----------------------------------------------------------------------
        inp_data = self.inp_data

        for head in inp_data:
            if (head in InpReader.new_convert_handler) or (head in InpReader.convert_handler):
                inp_data[head] = convert_head(head, inp_data[head])

        return inp_data
        # return delayed(inp_data).compute()

    def del_not_important(self):
        if self.drop_gui_part:
            self.gui_part = dict()
            for head in InpReader.GUI_SECTIONS:
                if head in self.inp_data:
                    self.gui_part[head] = self.inp_data.pop(head)


# @timeit
def read_inp_file(filename, drop_gui_part=True):
    reader = InpReader(drop_gui_part=drop_gui_part)
    reader.read_inp(filename)
    reader.del_not_important()
    reader.convert_sections()
    return reader.inp_data
