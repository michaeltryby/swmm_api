import re

from pandas import DataFrame, to_datetime

from .helpers.type_converter import infer_type
# from .inp_helpers import InpSectionGeneric


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
    options = {}
    for line in lines:
        label = line.pop(0)
        assert len(line) == 1
        options[label] = infer_type(line[0])
    return options


# class Report(InpSectionGeneric):
#     def __init__(self):
#         pass
#
#     @classmethod
#     def from_lines(cls, lines):
#         pass
#
#     def __repr__(self):
#         pass
#
#     def __str__(self):
#         pass
#
#     def to_inp(self, fast=False):
#         pass


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
    new_lines = {}
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


def _line_split(line):
    # but don't split quoted text
    # for convert_timeseries
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
            line = _line_split(' '.join(line))
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

    Args:
        lines (list):

    Returns:
        dict[pandas.DataFrame]:
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

    # from dict to pandas dataframe
    for k in curves:
        for n in curves[k]:
            curves[k][n] = DataFrame.from_dict(curves[k][n], 'columns')

    return curves


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


def convert_coordinates(lines):
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

    Args:
        lines (list):

    Returns:
        pandas.DataFrame:
    """
    new_lines = {}
    for line in lines:
        name = line[0]
        new_lines[name] = {'x': line[1],
                           'y': line[2]}

    frame = DataFrame.from_dict(new_lines, 'index').rename_axis('Name', axis='columns')
    # print(general_category2string(frame))
    return frame


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


def convert_tags(lines):
    """PC-SWMM ?"""
    # TAGS AS DATAFRAME
    # tags = DataFrame.from_records(lines, columns=['type', 'name', 'tags'])

    tags = dict()
    for line in lines:
        type_, name, tag = line
        if type_ not in tags:
            tags[type_] = dict()

        tags[type_][name] = tag

    # ---------------------------------------
    # MAKE TAGS TO SERIES
    # tags_df = dict()
    # for type_ in tags:
    #     tags_df[type_] = DataFrame.from_dict(tags[type_], orient='index')

    # df[0].unique()
    # ['Subcatch', 'Node', 'Link']
    return tags
