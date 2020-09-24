import re

from pandas import DataFrame, to_datetime

from .helpers.type_converter import infer_type, type2str
from .inp_helpers import InpSectionGeneric, UserDict_, dataframe_to_inp_string, InpSection


# class Title(InpSectionGeneric):
#     """
#     Section:
#         [TITLE]
#
#     Purpose:
#         Attaches a descriptive title to the problem being analyzed.
#
#     Format:
#         Any number of lines may be entered. The first line will be used as a page header in the output report.
#
#     Args:
#         lines (list):
#
#     Returns:
#         str: the title
#     """
#
#     def __init__(self, title=''):
#         self.title = title
#
#     @classmethod
#     def from_lines(cls, lines):
#         title = '\n'.join([' '.join([str(word) for word in line]) for line in lines])
#         return cls(title)
#
#     def __repr__(self):
#         return self.title
#
#     def __str__(self):
#         return self.title
#
#     def to_inp(self, fast=False):
#         return self.title
from .inp_sections import Transect


def _str_to_lines(content):
    lines = list()
    for line in content.split('\n'):
        line = line.strip()
        if line == '' or line.startswith(';'):  # ignore empty and comment lines
            continue
        else:
            lines.append(line.split())
    return lines


def convert_title(lines):
    """
    Section:
        [TITLE]

    Purpose:
        Attaches a descriptive title to the problem being analyzed.

    Format:
        Any number of lines may be entered. The first line will be used as a page header in the output report.

    Args:
        lines (list):

    Returns:
        str: the title
    """
    title = '\n'.join([' '.join([str(word) for word in line]) for line in lines])
    return title


def convert_options(lines):
    """
    Section:
        [OPTIONS]

    Purpose:
        Provides values for various analysis options.

    Format:
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
        lines (list): section lines from input file

    Returns:
        dict: options
    """
    options = dict()
    for line in lines:
        label = line.pop(0)
        assert len(line) == 1
        options[label] = infer_type(line[0])
    return options


def convert_report(lines):
    """
    Section:
        [REPORT]

    Purpose:
        Describes the contents of the report file that is produced.

    Formats:
        INPUT          YES / NO*
        CONTINUITY     YES* / NO
        FLOWSTATS      YES* / NO
        CONTROLS       YES / NO*
        SUBCATCHMENTS  ALL / NONE* / <list of subcatchment names>
        NODES          ALL / NONE* / <list of node names>
        LINKS          ALL / NONE* / <list of link names>
        LID            Name Subcatch Fname

        * .. defaults

    Remarks:
        INPUT specifies whether or not a summary of the input data should be provided in
        the output report. The default is NO.

        CONTINUITY specifies whether continuity checks should be reported or not. The
        default is YES.

        FLOWSTATS specifies whether summary flow statistics should be reported or not. The
        default is YES.

        CONTROLS specifies whether all control actions taken during a simulation should be
        listed or not. The default is NO.

        SUBCATCHMENTS gives a list of subcatchments whose results are to be reported. The
        default is NONE.

        NODES gives a list of nodes whose results are to be reported. The default is NONE.

        LINKS gives a list of links whose results are to be reported. The default is NONE.

        LID specifies that the LID control Name in subcatchment Subcatch should have a
        detailed performance report for it written to file Fname.

        The SUBCATCHMENTS, NODES, LINKS, and LID lines can be repeated multiple times.

    Args:
        lines (list): section lines from input file

    Returns:
        dict: report
    """
    options = {}
    for line in lines:
        label = line.pop(0)
        if len(line) == 1:
            value = infer_type(line[0])

        elif (label == 'LID') and (len(line) == 3):
            value = {'Name': line[0],
                     'Subcatch': line[1],
                     'Fname': line[2]}

        else:
            value = infer_type(line)

        options[label] = value

    return options


class ReportSection(UserDict_, InpSectionGeneric):
    def __init__(self):
        self.INPUT = False
        self.CONTINUITY = True
        self.FLOWSTATS = True  # False: no max values in summary tables
        self.CONTROLS = False
        self.SUBCATCHMENTS = None
        self.NODES = None
        self.LINKS = None
        self.LID = None
        UserDict_.__init__(self)
        self._data = vars(self)

    @classmethod
    def from_lines(cls, lines):
        rep = cls()

        for line in lines:
            label = line.pop(0)
            if len(line) == 1:
                value = infer_type(line[0])

            elif (label == 'LID') and (len(line) == 3):
                value = {'Name': line[0],
                         'Subcatch': line[1],
                         'Fname': line[2]}

            else:
                value = infer_type(line)

            if label in ['SUBCATCHMENTS', 'NODES', 'LINKS', 'LID']:
                if isinstance(value, str) and (value.upper() == 'ALL'):
                    pass
                elif value is None:
                    pass
                elif not isinstance(value, list):
                    value = [value]

            if isinstance(rep[label], list):
                rep[label] += value
            else:
                rep[label] = value
        return rep

    def to_inp(self, fast=False):
        f = ''
        section = vars(self).copy()
        section.pop('_data')

        max_len = len(max(section.keys(), key=len)) + 2

        def _dict_format(key, value):
            return '{key}{value}'.format(key=key.ljust(max_len),
                                         value=type2str(value) + '\n')

        for sub in section:
            value = section[sub]
            if value is None:
                continue

            if isinstance(value, list) and len(value) > 20:
                size = len(value)
                start = 0
                for end in range(20, size, 20):
                    f += _dict_format(key=sub, value=value[start:end])
                    start = end

            else:
                f += _dict_format(key=sub, value=value)

        return f


def convert_evaporation(lines):
    """
    Section:
        [EVAPORATION]

    Purpose:
        Specifies how daily evaporation rates vary with time for the study area.

    Formats:
        CONSTANT    evap (0)
        MONTHLY     e1 e2 e3 e4 e5 e6 e7 e8 e9 e10 e11 e12
        TIMESERIES  Tseries
        TEMPERATURE
        FILE        (p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12)

        RECOVERY    patternID
        DRY_ONLY    NO / YES

    Remarks:
        evap
             constant evaporation rate (in/day or mm/day).
        e1
             evaporation rate in January (in/day or mm/day).
        ...
        e12
             evaporation rate in December (in/day or mm/day).
        Tseries
             name of time series in [TIMESERIES] section with evaporation data.
        p1
             pan coefficient for January.
        ...
        p12
             pan coefficient for December.
        patID
             name of a monthly time pattern.

        Use only one of the above formats (CONSTANT, MONTHLY, TIMESERIES,
        TEMPERATURE, or FILE). If no [EVAPORATION] section appears, then evaporation is
        assumed to be 0.

        TEMPERATURE indicates that evaporation rates will be computed from the daily air
        temperatures contained in an external climate file whose name is provided in the
        [TEMPERATURE] section (see below). This method also uses the site’s latitude, which
        can also be specified in the [TEMPERATURE] section.

        FILE indicates that evaporation data will be read directly from the same external
        climate file used for air temperatures as specified in the [TEMPERATURE] section
        (see below).

        RECOVERY identifies an optional monthly time pattern of multipliers used to modify
        infiltration recovery rates during dry periods. For example, if the normal infiltration
        recovery rate was 1% during a specific time period and a pattern factor of 0.8 applied
        to this period, then the actual recovery rate would be 0.8%.

        DRY_ONLY determines if evaporation only occurs during periods with no precipitation.
        The default is NO.

    Args:
        lines (list): section lines from input file

    Returns:
        dict: evaporation_options
    """
    options = {}
    for line in lines:

        label = line.pop(0)
        if len(line) == 1:
            value = line[0]

        elif label == 'TEMPERATURE':
            assert len(line) == 0
            value = ''

        elif label == 'MONTHLY':
            assert len(line) == 12
            value = line[1:]

        elif label == 'FILE':
            if len(line) == 12:
                value = line[1:]
            elif len(line) == 0:
                value = ''
            else:
                raise NotImplementedError()

        else:
            value = line

        options[label] = infer_type(value)

    mult_infos = [x in options for x in ['CONSTANT', 'MONTHLY', 'TIMESERIES', 'TEMPERATURE', 'FILE']]

    if sum(mult_infos) != 1:
        if sum(mult_infos) == 0:
            options['CONSTANT'] = 0
        else:
            raise UserWarning('Too much evaporation')

    return options


def convert_temperature(lines):
    """
    Section:
        [TEMPERATURE]

    Purpose:
        Specifies daily air temperatures, monthly wind speed, and various snowmelt
        parameters for the study area. Required only when snowmelt is being modeled or
        when evaporation rates are computed from daily temperatures or are read from an
        external climate file.

    Formats:
        TIMESERIES Tseries
        FILE Fname (Start)
        WINDSPEED MONTHLY s1 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 s12
        WINDSPEED FILE
        SNOWMELT Stemp ATIwt RNM Elev Lat DTLong
        ADC IMPERVIOUS f.0 f.1 f.2 f.3 f.4 f.5 f.6 f.7 f.8 f.9
        ADC PERVIOUS f.0 f.1 f.2 f.3 f.4 f.5 f.6 f.7 f.8 f.9

    Remarks:
        Tseries
            name of time series in [TIMESERIES] section with temperature data.
        Fname
            name of external Climate file with temperature data.
        Start
            date to begin reading from the file in month/day/year format (default is the beginning of the file).
        s1
            average wind speed in January (mph or km/hr).
        ...

        s12
            average wind speed in December (mph or km/hr).
        Stemp
            air temperature at which precipitation falls as snow (deg F or C).
        ATIwt
            antecedent temperature index weight (default is 0.5).
        RNM
            negative melt ratio (default is 0.6).
        Elev
            average elevation of study area above mean sea level (ft or m) (default is 0).
        Lat
            latitude of the study area in degrees North (default is 50).
        DTLong
            correction, in minutes of time, between true solar time and the standard clock time (default is 0).
        f.0
            fraction of area covered by snow when ratio of snow depth to depth at 100% cover is 0
        ....
        f.9
            fraction of area covered by snow when ratio of snow depth to depth at 100% cover is 0.9

    Use the TIMESERIES line to read air temperature from a time series or the FILE line
    to read it from an external Climate file. Climate files are discussed in Section 11.4

    Climate Files. If neither format is used, then air temperature remains constant at 70 degrees F.

    Wind speed can be specified either by monthly average values or by the same
    Climate file used for air temperature. If neither option appears, then wind speed is
    assumed to be 0.

    Separate Areal Depletion Curves (ADC) can be defined for impervious and pervious
    sub-areas. The ADC parameters will default to 1.0 (meaning no depletion) if no data
    are supplied for a particular type of sub-area.
    """
    new_lines = dict()
    for line in lines:

        sub_head = line.pop(0)
        n_options = len(line)

        if sub_head == 'TIMESERIES':
            assert n_options == 1
            opt = line[0]

        elif sub_head == 'FILE':
            if n_options == 1:
                opt = line[0]
            else:
                opt = line

        elif sub_head == 'WINDSPEED':
            subsub_head = line[0]
            if subsub_head == 'FILE':
                assert n_options == 1
                opt = line[0]
            elif subsub_head == 'MONTHLY':
                assert n_options == 13
                opt = line
            else:
                raise NotImplementedError()

        elif sub_head == 'SNOWMELT':
            assert n_options == 6
            opt = line

        elif sub_head == 'ADC':
            subsub_head = line.pop(0)
            sub_head += ' ' + subsub_head
            if subsub_head == 'IMPERVIOUS':
                assert n_options == 11
                opt = line
            elif subsub_head == 'PERVIOUS':
                assert n_options == 11
                opt = line
            else:
                raise NotImplementedError()

        else:
            opt = line

        new_lines[sub_head] = opt

    return new_lines


class TimeseriesSection(UserDict_, InpSectionGeneric):
    """
    Section:
        [TIMESERIES]

    Purpose:
        Describes how a quantity varies over time.

    Formats:
        - Name ( Date ) Hour Value ...
        - Name Time Value ...
        - Name FILE Fname

    Remarks:
        - Name: name assigned to time series.
        - Date: date in Month/Day/Year format (e.g., June 15, 2001 would be 6/15/2001).
        - Hour: 24-hour military time (e.g., 8:40 pm would be 20:40) relative to the last date specified
               (or to midnight of the starting date of the simulation if no previous date was specified).
        - Time: hours since the start of the simulation, expressed as a decimal number or as hours:minutes.
        - Value: value corresponding to given date and time.
        - Fname: name of a file in which the time series data are stored

        There are two options for supplying the data for a time series:
        i.: directly within this input file section as described by the first two formats
        ii.: through an external data file named with the third format.

        When direct data entry is used, multiple date-time-value or time-value entries can
        appear on a line. If more than one line is needed, the table's name must be repeated
        as the first entry on subsequent lines.

        When an external file is used, each line in the file must use the same formats listed
        above, except that only one date-time-value (or time-value) entry is allowed per line.
        Any line that begins with a semicolon is considered a comment line and is ignored.
        Blank lines are not allowed.

        Note that there are two methods for describing the occurrence time of time series data:

        - as calendar date/time of day (which requires that at least one date, at the start of the series, be entered)
        - as elapsed hours since the start of the simulation.

        For the first method, dates need only be entered at points in time when a new day occurs.

    Examples:
        ;Rainfall time series with dates specified
        TS1 6-15-2001 7:00 0.1 8:00 0.2 9:00 0.05 10:00 0
        TS1 6-21-2001 4:00 0.2 5:00 0 14:00 0.1 15:00 0 335

        ;Inflow hydrograph - time relative to start of simulation
        HY1 0 0 1.25 100 2:30 150 3.0 120 4.5 0
        HY1 32:10 0 34.0 57 35.33 85 48.67 24 50 0
    """

    def __init__(self):
        UserDict_.__init__(self)

    @staticmethod
    def _line_split(line):
        # but don't split quoted text
        # for convert_timeseries
        return re.findall(r'[^"\s]\S*|".+?"', line)

    class TYPES:
        FILE = 'FILE'

    class INDEX:
        DATETIME = 'Datetime'
        TIME = 'relTime'
        HOURS = 'Hours'
        VALUE = 'Value'

    @classmethod
    def from_lines(cls, lines):
        new = cls()
        old_date = None
        new_lines = new._data
        for name, *line in lines:
            # ---------------------------------
            if line[0].upper() == cls.TYPES.FILE:
                kind, *fn = line
                new_lines[name] = {'Type': kind,
                                   'Fname': ' '.join(fn)}

            # ---------------------------------
            else:
                date = None
                time = None
                hours = None

                if name not in new_lines:
                    new_lines[name] = {cls.INDEX.VALUE: list()}

                iterator = iter(line)
                for part in iterator:
                    if '/' in part:
                        date = part

                    elif ':' in part:
                        time = part

                    elif date is None and time is None and hours is None and '.' in part:
                        hours = part

                    else:
                        value = part
                        new_lines[name][cls.INDEX.VALUE].append(value)

                        if date is not None:
                            if cls.INDEX.DATETIME not in new_lines[name]:
                                new_lines[name][cls.INDEX.DATETIME] = list()
                            new_lines[name][cls.INDEX.DATETIME].append('{} {}'.format(date, time))

                        elif time is not None:
                            if cls.INDEX.TIME not in new_lines[name]:
                                new_lines[name][cls.INDEX.TIME] = list()
                            new_lines[name][cls.INDEX.TIME].append(time)

                        else:
                            if cls.INDEX.HOURS not in new_lines[name]:
                                new_lines[name][cls.INDEX.HOURS] = list()
                            new_lines[name][cls.INDEX.HOURS].append(hours)

        return new

    def _get_index(self, d):
        if self.INDEX.DATETIME in d:
            return self.INDEX.DATETIME
        elif self.INDEX.HOURS in d:
            return self.INDEX.HOURS
        elif self.INDEX.TIME in d:
            return self.INDEX.TIME

    @property
    def to_pandas(self):
        timeseries = dict()

        for n, series in self._data.items():
            if 'Type' in series:
                timeseries[n] = self._data[n]

            else:
                timeseries[n] = DataFrame.from_dict(self._data[n], 'columns').set_index(self._get_index(series))[
                    self.INDEX.VALUE].astype(float).copy()

                if self.INDEX.HOURS in series:
                    timeseries[n].index = timeseries[n].index.astype(float)

                elif self.INDEX.TIME in series:
                    pass

                elif self.INDEX.DATETIME in series:
                    timeseries[n].index = to_datetime(timeseries[n].index)

        return timeseries

    def from_pandas(self, label, series):
        self._data[label] = {self.INDEX.DATETIME: series.index.strftime('%m/%d/%Y %H:%M').to_list(),
                             self.INDEX.VALUE: series.to_list()}

    def to_inp(self, fast=False):
        if fast:
            cat = self._data
        else:
            cat = self.to_pandas

        f = ''

        max_len = len(max(cat.keys(), key=len)) + 2

        for n, series in self._data.items():
            if 'Type' in series:
                f += '{} {} {}\n'.format(n.ljust(max_len), series['Type'], series['Fname'])

            else:
                index_label = self._get_index(series)

                if fast:
                    for datetime, value in zip(series[index_label], series[self.INDEX.VALUE]):
                        f += '{} {} {}\n'.format(n, datetime, value)

                else:
                    if self.INDEX.DATETIME in series:
                        df = cat[n].to_frame().copy()
                        df['Date  Time'] = df.index.strftime('%m/%d/%Y %H:%M')
                        df.columns.name = ';Name'
                        df['<'] = n
                        df = df.set_index('<')[['Date  Time', self.INDEX.VALUE]].copy()
                        df.index.name = None
                        f += df.to_string()
                        f += '\n'
                    else:
                        df = cat[n].to_frame().copy()
                        df.columns.name = ';Name'
                        df[index_label] = df.index
                        df['<'] = n
                        df = df.set_index('<')[[index_label, self.INDEX.VALUE]].copy()
                        df.index.name = None
                        # if df.index.name:
                        #     df.index.name = ';' + df.index.name
                        f += df.to_string()
                        f += '\n'
        return f


class CurvesSection(UserDict_, InpSectionGeneric):
    """
    Section:
        [CURVES]

    Purpose:
        Describes a relationship between two variables in tabular format.

    Format:
        Name Type X-value Y-value ...

    Format-PCSWMM:
            Name Type X-Value Y-Value

    Remarks:
        Name
            name assigned to table
        Type
            STORAGE / SHAPE / DIVERSION / TIDAL / PUMP1 / PUMP2 / PUMP3 / PUMP4 / RATING / CONTROL
        X-value
            an x (independent variable) value

        Y-value
            the y (dependent variable) value corresponding to x

        Multiple pairs of x-y values can appear on a line. If more than one line is needed,
        repeat the curve's name (but not the type) on subsequent lines. The x-values must
        be entered in increasing order.

        Choices for curve type have the following meanings (flows are expressed in the
        user’s choice of flow units set in the [OPTIONS] section):

        STORAGE
            surface area in ft2 (m2) v. depth in ft (m) for a storage unit node
        SHAPE
            width v. depth for a custom closed cross-section, both normalized with respect to full depth
        DIVERSION
            diverted outflow v. total inflow for a flow divider node
        TIDAL
            water surface elevation in ft (m) v. hour of the day for an outfall node
        PUMP1
            pump outflow v. increment of inlet node volume in ft3 (m3)
        PUMP2
            pump outflow v. increment of inlet node depth in ft (m)
        PUMP3
            pump outflow v. head difference between outlet and inlet nodes in ft (m)
        PUMP4
            pump outflow v. continuous depth in ft (m)
        RATING
            outlet flow v. head in ft (m)
        CONTROL
            control setting v. controller variable

    Examples:
        ;Storage curve (x = depth, y = surface area)
        AC1 STORAGE 0 1000 2 2000 4 3500 6 4200
         8
         5000
        ;Type1 pump curve (x = inlet wet well volume, y = flow )
        PC1 PUMP1
        PC1 100 5 300 10 500 20

    """

    def __init__(self):
        UserDict_.__init__(self)

    def copy(self):
        new = CurvesSection()
        new._data = self._data.copy()
        return new

    class TYPES:
        STORAGE = 'STORAGE'
        SHAPE = 'SHAPE'
        DIVERSION = 'DIVERSION'
        TIDAL = 'TIDAL'
        PUMP1 = 'PUMP1'
        PUMP2 = 'PUMP2'
        PUMP3 = 'PUMP3'
        PUMP4 = 'PUMP4'
        RATING = 'RATING'
        CONTROL = 'CONTROL'

    def append_lines(self, lines):
        kind = ''
        for line in lines:
            name = line[0]
            l = len(line)

            if (l % 2) == 0:
                kind = line[1].upper()

                if kind not in self._data:
                    self._data[kind] = dict()

                remains = line[2:]
            else:
                remains = line[1:]

            it = iter(remains)
            for a in it:
                b = next(it)
                if name not in self._data[kind]:
                    self._data[kind][name] = list()

                self._data[kind][name].append(infer_type([a, b]))

    @classmethod
    def from_lines(cls, lines):
        new_curves = cls()
        new_curves.append_lines(lines)
        return new_curves

    @classmethod
    def _get_names(cls, kind):
        TYPES = cls.TYPES
        if kind == TYPES.STORAGE:
            return ['depth', 'area']
        elif kind == TYPES.SHAPE:
            return ['depth', 'width']
        elif kind == TYPES.DIVERSION:
            return ['inflow', 'outflow']
        elif kind == TYPES.TIDAL:
            return ['hour', 'elevation']
        elif kind == TYPES.PUMP1:
            return ['volume', 'outflow']
        elif kind == TYPES.PUMP2:
            return ['depth', 'outflow']
        elif kind == TYPES.PUMP3:
            return ['head diff', 'outflow']
        elif kind == TYPES.PUMP4:
            return ['depth', 'outflow']
        elif kind == TYPES.RATING:
            return ['head', 'flow']
        elif kind == TYPES.CONTROL:
            return ['variable', 'setting']

    @property
    def to_pandas(self):
        # from dict to pandas dataframe
        frame_di = dict()
        for kind in self._data:
            frame_di[kind] = dict()
            columns = self._get_names(kind)
            for name in self._data[kind]:
                frame_di[kind][name] = DataFrame.from_records(self._data[kind][name], columns=columns)

        return frame_di

    def to_inp(self, fast=False):
        f = ''

        if fast:
            cat = self._data
            for k in cat:
                for n in cat[k]:
                    values = cat[k][n]  # [(x,y), (x,y), ...]
                    k_len = len(k)
                    for i, (x, y) in enumerate(values):
                        if i == 0:
                            f += '{} {} {}\n'.format(n, k, type2str([x, y]))
                        else:
                            f += '{} {} {}\n'.format(n, ' ' * k_len, type2str([x, y]))

        else:
            cat = self.to_pandas
            for k in cat:
                for n in cat[k]:
                    a, b = self._get_names(k)
                    df = cat[k][n].copy()
                    if k == self.TYPES.SHAPE:
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


def convert_loadings(lines):
    """
    Section:
        [LOADINGS]

    Purpose:
        Specifies the pollutant buildup that exists on each subcatchment at the start of a simulation.

    Format:
        Subcat Pollut InitBuildup Pollut InitBuildup ...

    Format-PCSWMM:
        Subcatchment Pollutant Buildup

    Remarks:
        Subcat
            name of a subcatchment.
        Pollut
            name of a pollutant.
        InitBuildup
            initial buildup of pollutant (lbs/acre or kg/hectare).

        More than one pair of pollutant - buildup values can be entered per line. If more than
        one line is needed, then the subcatchment name must still be entered first on the
        succeeding lines.

        If an initial buildup is not specified for a pollutant, then its initial buildup is computed
        by applying the DRY_DAYS option (specified in the [OPTIONS] section) to the
        pollutant’s buildup function for each land use in the subcatchment.

    Args:
        lines (list):

    Returns:
        pandas.DataFrame:
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


class CoordinatesSection(UserDict_, InpSectionGeneric):
    """
    Section:
        [COORDINATES]

    Purpose:
        Assigns X,Y coordinates to drainage system nodes.

    Format:
        Node Xcoord Ycoord

    Remarks:
        Node
            name of node.
        Xcoord
            horizontal coordinate relative to origin in lower left of map.
        Ycoord
            vertical coordinate relative to origin in lower left of map.
    """

    @classmethod
    def from_lines(cls, lines):
        new = cls()
        for line in lines:
            node, x, y = line
            new._data[node] = {'x': float(x), 'y': float(y)}
        return new

    def __repr__(self):
        return self.to_pandas.__repr__()

    def __str__(self):
        return self.to_inp()

    def to_inp(self, fast=False):
        if self.empty:
            return '; NO data'
        if fast:
            f = ''
            max_len_name = len(max(self._data.keys(), key=len)) + 2
            f += '{name} {x} {y}\n'.format(name='; Node'.ljust(max_len_name), x='x', y='y')
            for node, coords in self._data.items():
                f += '{name} {x} {y}\n'.format(name=node.ljust(max_len_name), **coords)
        else:
            f = dataframe_to_inp_string(self.to_pandas)
        return f

    @property
    def to_pandas(self):
        return DataFrame.from_dict(self._data, orient='index')

    @classmethod
    def from_pandas(cls, data, x_name='x', y_name='y'):
        new = cls()
        df = data[[x_name, y_name]].rename({x_name: 'x', y_name: 'y'})
        new._data = df[['x', 'y']].to_dict(orient='index')
        return new


class VerticesSection(UserDict_, InpSectionGeneric):
    """
    Section:
        [VERTICES]

    Purpose:
        Assigns X,Y coordinates to interior vertex points of curved drainage system links.

    Format:
        Link Xcoord Ycoord

    Remarks:
        Node
            name of link.
        Xcoord
            horizontal coordinate of vertex relative to origin in lower left of map.
        Ycoord
            vertical coordinate of vertex relative to origin in lower left of map.

        Include a separate line for each interior vertex of the link, ordered from the inlet node to the outlet node.

        Straight-line links have no interior vertices and therefore are not listed in this section.
    """

    @classmethod
    def from_lines(cls, lines):
        new = cls()
        for line in lines:
            link, x, y = line
            if link not in new._data:
                new._data[link] = list()

            new._data[link].append({'x': float(x), 'y': float(y)})
        return new

    def __repr__(self):
        return self.to_pandas.__repr__()

    def __str__(self):
        return self.to_inp()

    def to_inp(self, fast=False):
        if self.empty:
            return '; NO data'

        if fast:
            f = ''
            max_len_name = len(max(self._data.keys(), key=len)) + 2
            f += '{name} {x} {y}\n'.format(name='; Link'.ljust(max_len_name), x='x', y='y')
            for link, vertices in self._data.items():
                for v in vertices:
                    f += '{name} {x} {y}\n'.format(name=link.ljust(max_len_name), **v)
        else:
            f = dataframe_to_inp_string(self.to_pandas)
        return f

    @property
    def to_pandas(self):
        rec = list()
        for link, vertices in self._data.items():
            for v in vertices:
                rec.append([link, v['x'], v['y']])

        return DataFrame.from_records(rec).rename(columns={0: 'Link',
                                                           1: 'x',
                                                           2: 'y'}).set_index('Link', drop=True)

    @classmethod
    def from_pandas(cls, data, x_name='x', y_name='y'):
        new = cls()
        df = data[[x_name, y_name]].rename({x_name: 'x', y_name: 'y'})
        new._data = df[['x', 'y']].groupby(df.index).apply(lambda x: x.to_dict('records')).to_dict()
        return new


def convert_map(lines):
    """
    Section:
        [MAP]

    Purpose:
        Provides dimensions and distance units for the map.

    Formats:
        DIMENSIONS X1 Y1 X2 Y2
        UNITS FEET / METERS / DEGREES / NONE

    Remarks:
    X1
        lower-left X coordinate of full map extent
    Y1
        lower-left Y coordinate of full map extent
    X2
        upper-right X coordinate of full map extent
    Y2
         upper-right Y coordinate of full map extent

    Args:
        lines (list):

    Returns:
        dict:
    """
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


class TagsSection(UserDict_, InpSectionGeneric):
    """PC-SWMM ?"""

    def __init__(self):
        UserDict_.__init__(self)

    class Types:
        Node = 'Node'
        Subcatch = 'Subcatch'
        Link = 'Link'

    @classmethod
    def from_lines(cls, lines):
        # TAGS AS DATAFRAME
        # tags = DataFrame.from_records(lines, columns=['type', 'name', 'tags'])
        new = cls()
        for line in lines:
            kind, name, tag = line
            if kind not in new._data:
                new._data[kind] = dict()

            new._data[kind][name] = tag
        return new

    @property
    def to_pandas(self):
        # MAKE TAGS TO SERIES
        tags_df = dict()
        for type_ in self._data:
            tags_df[type_] = DataFrame.from_dict(self._data[type_], orient='index')

        # df[0].unique()
        # ['Subcatch', 'Node', 'Link']
        return tags_df

    def to_inp(self, fast=False):
        if self.empty:
            return '; NO data'
        f = ''
        max_len_type = len(max(self._data.keys(), key=len)) + 2
        for type_, tags in self._data.items():
            max_len_name = len(max(tags.keys(), key=len)) + 2
            for name, tag in tags.items():
                f += '{{:<{len1}}} {{:<{len2}}} {{}}\n'.format(len1=max_len_type, len2=max_len_name).format(type_, name,
                                                                                                            tag)
        return f


class TransectSection(InpSection):
    def __init__(self):
        InpSection.__init__(self, Transect)

    @classmethod
    def from_lines(cls, lines, section_class=None):
        inp_section = cls()
        for section_class_line in Transect.convert_lines(lines):
            inp_section.append(section_class_line)
        return inp_section

    def to_inp(self, fast=None):
        return InpSection.to_inp(self, fast=True)
