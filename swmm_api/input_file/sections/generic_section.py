from collections import UserString

from .._type_converter import infer_type, type2str
from ..helpers import InpSectionGeneric, CustomDict
from ..section_abr import SEC


def line_iter(lines):
    if isinstance(lines, str):
        lines = lines.split('\n')

    for line in lines:
        line = line.split(';')[0]
        line = line.strip()
        if line == '':  # ignore empty and comment lines
            continue
        else:
            yield line.split()


class TitleSection(UserString):
    """
    abstract class for ``.inp``-file sections without objects

    :term:`dict-like <mapping>`"
    """
    _section_label = SEC.TITLE
    """str: label of the section"""

    def __init__(self, *args, **kwargs):
        UserString.__init__(self, *args, **kwargs)
        self._inp = None

    def set_parent_inp(self, inp):
        self._inp = inp

    def get_parent_inp(self):
        return self._inp

    @classmethod
    def from_inp_lines(cls, lines):
        """
        read ``.inp``-file lines and create an section object

        Args:
            lines (str | list[list[str]]): lines in the section of the ``.inp``-file

        Returns:
            InpSectionGeneric: object of the section
        """
        return cls(lines)

    def to_inp_lines(self, fast=False):
        """
        write ``.inp``-file lines of the section object

        Args:
            fast (bool): speeding up conversion

                - :obj:`True`: if no special formation of the input file is needed
                - :obj:`False`: section is converted into a table to prettify string output (slower)

        Returns:
            str: ``.inp``-file lines of the section object
        """
        return self


class OptionSection(InpSectionGeneric):
    """
    Section: [**OPTIONS**]

    Purpose:
        Provides values for various analysis options.

    Format:
        ::

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

        `* .. defaults`

        FLOW_UNITS makes a choice of flow units. Selecting a US flow unit means that all
        other quantities will be expressed in US units, while choosing a metric flow unit will
        force all quantities to be expressed in metric units. The default is CFS.

        INFILTRATION selects a model for computing infiltration of rainfall into the upper
        soil zone of subcatchments. The default model is HORTON.

        FLOW_ROUTING determines which method is used to route flows through the
        drainage system. STEADY refers to sequential steady state routing (i.e. hydrograph
        translation), KINWAVE to kinematic wave routing, DYNWAVE to dynamic wave routing.
        The default routing method is KINWAVE.

        LINK_OFFSETS determines the convention used to specify the position of a link
        offset above the invert of its connecting node. DEPTH indicates that offsets are
        expressed as the distance between the node invert and the link while ELEVATION
        indicates that the absolute elevation of the offset is used. The default is DEPTH.

        FORCE_MAIN_EQUATION establishes whether the Hazen-Williams (H-W) or the
        Darcy-Weisbach (D-W) equation will be used to compute friction losses for
        pressurized flow in conduits that have been assigned a Circular Force Main cross-
        section shape. The default is H-W.

        IGNORE_RAINFALL is set to YES if all rainfall data and runoff calculations should be
        ignored. In this case SWMM only performs flow and pollutant routing based on user-
        supplied direct and dry weather inflows. The default is NO.

        IGNORE_SNOWMELT is set to YES if snowmelt calculations should be ignored when a
        project file contains snow pack objects. The default is NO.

        IGNORE_GROUNDWATER is set to YES if groundwater calculations should be ignored
        when a project file contains aquifer objects. The default is NO.

        IGNORE_RDII is set to YES if rainfall dependent inflow/infiltration should be ignored
        when RDII unit hydrographs and RDII inflows have been supplied to a project file.
        The default is NO.

        IGNORE_ROUTING is set to YES if only runoff should be computed even if the project
        contains drainage system links and nodes. The default is NO.

        IGNORE_QUALITY is set to YES if pollutant washoff, routing, and treatment should be
        ignored in a project that has pollutants defined. The default is NO.

        ALLOW_PONDING determines whether excess water is allowed to collect atop nodes
        and be re-introduced into the system as conditions permit. The default is NO ponding.

        In order for ponding to actually occur at a particular node, a non-zero value for its
        Ponded Area attribute must be used.

        SKIP_STEADY_STATE should be set to YES if flow routing computations should be
        skipped during steady state periods of a simulation during which the last set of
        computed flows will be used. A time step is considered to be in steady state if the
        percent difference between total system inflow and total system outflow is below the
        SYS_FLOW_TOL and the percent difference between current and previous lateral
        inflows are below the LAT_FLOW_TOL. The default for this option is NO.

        SYS_FLOW_TOL is the maximum percent difference between total system inflow and
        total system outflow which can occur in order for the SKIP_STEADY_STATE option to
        take effect. The default is 5 percent.

        LAT_FLOW_TOL is the maximum percent difference between the current and
        previous lateral inflow at all nodes in the conveyance system in order for the
        SKIP_STEADY_STATE option to take effect. The default is 5 percent.

        START_DATE is the date when the simulation begins. If not supplied, a date of
        1/1/2002 is used.

        START_TIME is the time of day on the starting date when the simulation begins. The
        default is 12 midnight (0:00:00).

        END_DATE is the date when the simulation is to end. The default is the start date.
        END_TIME is the time of day on the ending date when the simulation will end. The
        default is 24:00:00.

        REPORT_START_DATE is the date when reporting of results is to begin. The default is
        the simulation start date.

        REPORT_START_TIME is the time of day on the report starting date when reporting is
        to begin. The default is the simulation start time of day.

        SWEEP_START is the day of the year (month/day) when street sweeping operations
        begin. The default is 1/1.

        SWEEP_END is the day of the year (month/day) when street sweeping operations end.
        The default is 12/31.

        DRY_DAYS is the number of days with no rainfall prior to the start of the simulation.
        The default is 0.

        REPORT_STEP is the time interval for reporting of computed results. The default is
        0:15:00.

        WET_STEP is the time step length used to compute runoff from subcatchments
        during periods of rainfall or when ponded water still remains on the surface. The
        default is 0:05:00.

        DRY_STEP is the time step length used for runoff computations (consisting essentially
        of pollutant buildup) during periods when there is no rainfall and no ponded water.
        The default is 1:00:00.

        ROUTING_STEP is the time step length in seconds used for routing flows and water
        quality constituents through the conveyance system. The default is 600 sec (5
        minutes) which should be reduced if using dynamic wave routing. Fractional values
        (e.g., 2.5) are permissible as are values entered in hours:minutes:seconds format.

        LENGTHENING_STEP is a time step, in seconds, used to lengthen conduits under
        dynamic wave routing, so that they meet the Courant stability criterion under full-flow
        conditions (i.e., the travel time of a wave will not be smaller than the specified conduit
        lengthening time step). As this value is decreased, fewer conduits will require
        lengthening. A value of 0 (the default) means that no conduits will be lengthened.

        VARIABLE_STEP is a safety factor applied to a variable time step computed for
        each time period under dynamic wave flow routing. The variable time step is
        computed so as to satisfy the Courant stability criterion for each conduit and yet not
        exceed the ROUTING_STEP value. If the safety factor is 0 (the default), then no
        variable time step is used.

        MINIMUM_STEP is the smallest time step allowed when variable time steps are used
        for dynamic wave flow routing. The default value is 0.5 seconds.

        INERTIAL_DAMPING indicates how the inertial terms in the Saint Venant
        momentum equation will be handled under dynamic wave flow routing. Choosing
        NONE maintains these terms at their full value under all conditions. Selecting
        PARTIAL will reduce the terms as flow comes closer to being critical (and ignores
        them when flow is supercritical). Choosing FULL will drop the terms altogether.

        NORMAL_FLOW_LIMITED specifies which condition is checked to determine if flow in
        a conduit is supercritical and should thus be limited to the normal flow. Use SLOPE to
        check if the water surface slope is greater than the conduit slope, FROUDE to check if
        the Froude number is greater than 1.0, or BOTH to check both conditions. The default
        is BOTH.

        MIN_SURFAREA is a minimum surface area used at nodes when computing changes
        in water depth under dynamic wave routing. If 0 is entered, then the default value of
        12.566 ft2 (i.e., the area of a 4-ft diameter manhole) is used.

        MIN_SLOPE is the minimum value allowed for a conduit’s slope (%). If zero (the
        default) then no minimum is imposed (although SWMM uses a lower limit on
        elevation drop of 0.001 ft (0.00035 m) when computing a conduit slope).

        MAX_TRIALS is the maximum number of trials allowed during a time step to reach
        convergence when updating hydraulic heads at the conveyance system’s nodes. The
        default value is 8.

        HEAD_TOLERANCE is the difference in computed head at each node between
        successive trials below which the flow solution for the current time step is assumed to
        have converged. The default tolerance is 0.005 ft (0.0015 m).

        THREADS is the number of parallel computing threads to use for dynamic wave flow
        routing on machines equipped with multi-core processors. The default is 1.

        TEMPDIR provides the name of a file directory (or folder) where SWMM writes its
        temporary files. If the directory name contains spaces then it should be placed within
        double quotes. If no directory is specified, then the temporary files are written to the
        current directory that the user is working in.

    Args:
        lines (list): section lines from input file

    Returns:
        dict: options
    """
    _section_label = SEC.OPTIONS

    @classmethod
    def from_inp_lines(cls, lines):
        data = cls()
        for key, *line in line_iter(lines):
            key = key.upper()
            assert len(line) == 1
            data[key] = infer_type(line[0])
        return data


class ReportSection(InpSectionGeneric):
    """
    Section: [**REPORT**]

    Purpose:
        Describes the contents of the report file that is produced.

    Formats:
        ::

            INPUT          YES / NO*
            CONTINUITY     YES* / NO
            FLOWSTATS      YES* / NO
            CONTROLS       YES / NO*
            SUBCATCHMENTS  ALL / NONE* / <list of subcatchment names>
            NODES          ALL / NONE* / <list of node names>
            LINKS          ALL / NONE* / <list of link names>
            LID            Name Subcatch Fname

        `* .. defaults`

    Remarks:
        INPUT
            specifies whether or not a summary of the input data should be provided in the output report.
            The default is NO.
        CONTINUITY
            specifies whether continuity checks should be reported or not. The default is YES.
        FLOWSTATS
            specifies whether summary flow statistics should be reported or not. The default is YES.
        CONTROLS
            specifies whether all control actions taken during a simulation should be listed or not. The default is NO.
        SUBCATCHMENTS
            gives a list of subcatchments whose results are to be reported. The default is NONE.
        NODES
            gives a list of nodes whose results are to be reported. The default is NONE.
        LINKS
            gives a list of links whose results are to be reported. The default is NONE.
        LID
            specifies that the LID control Name in subcatchment Subcatch should have a
            detailed performance report for it written to file Fname.

        The SUBCATCHMENTS, NODES, LINKS, and LID lines can be repeated multiple times.
    """
    _section_label = SEC.REPORT

    class KEYS:
        INPUT = 'INPUT'
        CONTINUITY = 'CONTINUITY'
        FLOWSTATS = 'FLOWSTATS'
        CONTROLS = 'CONTROLS'
        SUBCATCHMENTS = 'SUBCATCHMENTS'
        NODES = 'NODES'
        LINKS = 'LINKS'
        LID = 'LID'

    @classmethod
    def from_inp_lines(cls, lines):
        data = cls()
        for key, *line in line_iter(lines):
            key = key.upper()
            if len(line) == 1:
                value = infer_type(line[0])

            elif (key == cls.KEYS.LID) and (len(line) == 3):
                value = {'Name': line[0],
                         'Subcatch': line[1],
                         'Fname': line[2]}

            else:
                value = infer_type(line)

            if key in [cls.KEYS.SUBCATCHMENTS,
                       cls.KEYS.NODES,
                       cls.KEYS.LINKS,
                       cls.KEYS.LID]:
                if isinstance(value, str) and (value.upper() == 'ALL'):
                    pass
                elif value is None:
                    pass
                elif not isinstance(value, list):
                    value = [value]
            if key not in data:
                data[key] = value
            elif isinstance(data[key], list):
                data[key] += value
            else:
                data[key] = value
        return data

    def to_inp_lines(self, fast=False):
        f = ''
        max_len = len(max(self.keys(), key=len)) + 2

        def _dict_format(key, value):
            return '{key}{value}'.format(key=key.ljust(max_len),
                                         value=type2str(value) + '\n')

        for sub in self:
            value = self[sub]
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


class EvaporationSection(InpSectionGeneric):
    """
    Section: [**EVAPORATION**]

    Purpose:
        Specifies how daily evaporation rates vary with time for the study area.

    Formats:
        ::

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
        `...`
            `...`
        e12
             evaporation rate in December (in/day or mm/day).
        Tseries
             name of time series in [TIMESERIES] section with evaporation data.
        p1
             pan coefficient for January.
        `...`
            `...`
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
    """
    _section_label = SEC.EVAPORATION

    class KEYS:
        CONSTANT = 'CONSTANT'
        MONTHLY = 'MONTHLY'
        TIMESERIES = 'TIMESERIES'
        TEMPERATURE = 'TEMPERATURE'
        FILE = 'FILE'
        RECOVERY = 'RECOVERY'
        DRY_ONLY = 'DRY_ONLY'

        _possible = [CONSTANT, MONTHLY, TIMESERIES, TEMPERATURE, FILE, RECOVERY, DRY_ONLY]

    @classmethod
    def from_inp_lines(cls, lines):
        """
        read ``.inp``-file lines and create an section object

        Args:
            lines (str | list[list[str]]): lines in the section of the ``.inp``-file

        Returns:
            InpSectionGeneric: object of the Evaporation-section
        """
        data = cls()
        for key, *line in line_iter(lines):
            key = key.upper()
            if len(line) == 1:
                value = line[0]

            elif key == cls.KEYS.TEMPERATURE:
                assert len(line) == 0
                value = ''

            elif key == cls.KEYS.MONTHLY:
                assert len(line) == 12
                value = line

            elif key == cls.KEYS.FILE:
                if len(line) == 12:
                    value = line
                elif len(line) == 0:
                    value = ''
                else:
                    raise NotImplementedError()

            else:
                value = line

            data[key] = infer_type(value)

        mult_infos = [x in data for x in [cls.KEYS.CONSTANT, cls.KEYS.MONTHLY, cls.KEYS.TIMESERIES,
                                          cls.KEYS.TEMPERATURE, cls.KEYS.FILE]]

        if sum(mult_infos) != 1:
            if sum(mult_infos) == 0:
                data[cls.KEYS.CONSTANT] = 0
            else:
                raise UserWarning('Too much evaporation')

        return data


class TemperatureSection(InpSectionGeneric):
    """
    Section: [**TEMPERATURE**]

    Purpose:
        Specifies daily air temperatures, monthly wind speed, and various snowmelt
        parameters for the study area. Required only when snowmelt is being modeled or
        when evaporation rates are computed from daily temperatures or are read from an
        external climate file.

    Formats:
        ::

            TIMESERIES Tseries
            FILE Fname (Start)
            WINDSPEED MONTHLY s1 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 s12
            WINDSPEED FILE
            SNOWMELT Stemp ATIwt RNM Elev Lat DTLong
            ADC IMPERVIOUS f.0 f.1 f.2 f.3 f.4 f.5 f.6 f.7 f.8 f.9
            ADC PERVIOUS f.0 f.1 f.2 f.3 f.4 f.5 f.6 f.7 f.8 f.9

    Remarks:
        Tseries
            name of time series in ``[TIMESERIES]`` section with temperature data.
        Fname
            name of external Climate file with temperature data.
        Start
            date to begin reading from the file in month/day/year format (default is the beginning of the file).
        s1
            average wind speed in January (mph or km/hr).
        `...`
            `...`
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
        `...`
            `...`
        f.9
            fraction of area covered by snow when ratio of snow depth to depth at 100% cover is 0.9

    Use the ``TIMESERIES`` line to read air temperature from a time series or the ``FILE`` line
    to read it from an external Climate file.
    Climate files are discussed in Section 11.4 Climate Files.
    If neither format is used, then air temperature remains constant at 70 degrees F (=21.11111 °C).

    Wind speed can be specified either by monthly average values or by the same
    Climate file used for air temperature. If neither option appears, then wind speed is
    assumed to be 0.

    Separate Areal Depletion Curves (ADC) can be defined for impervious and pervious
    sub-areas. The ADC parameters will default to 1.0 (meaning no depletion) if no data
    are supplied for a particular type of sub-area.
    """
    _section_label = SEC.TEMPERATURE

    class KEYS:
        TIMESERIES = 'TIMESERIES'
        FILE = 'FILE'

        _WINDSPEED = 'WINDSPEED'
        WINDSPEED_MONTHLY = _WINDSPEED + ' MONTHLY'
        WINDSPEED_FILE = _WINDSPEED + ' FILE'

        SNOWMELT = 'SNOWMELT'

        _ADC = 'ADC'
        ADC_IMPERVIOUS = _ADC + ' IMPERVIOUS'
        ADC_PERVIOUS = _ADC + ' PERVIOUS'

    @classmethod
    def from_inp_lines(cls, lines):
        """
        read ``.inp``-file lines and create an section object

        Args:
            lines (str | list[list[str]]): lines in the section of the ``.inp``-file

        Returns:
            InpSectionGeneric: object of the Temperature-section
        """
        data = cls()
        for key, *line in line_iter(lines):
            key = key.upper()
            n_options = len(line)

            if key == cls.KEYS.TIMESERIES:
                assert n_options == 1
                value = line[0]

            elif key == cls.KEYS.FILE:
                if n_options == 1:
                    value = line[0]
                else:
                    value = line

            elif key == cls.KEYS._WINDSPEED:
                key += ' ' + line.pop(0)
                if key == cls.KEYS.WINDSPEED_FILE:
                    assert n_options == 1
                    value = ''
                elif key == cls.KEYS.WINDSPEED_MONTHLY:
                    assert n_options == 13
                    value = line
                else:
                    raise NotImplementedError()

            elif key == cls.KEYS.SNOWMELT:
                assert n_options == 6
                value = line

            elif key == cls.KEYS._ADC:
                key += ' ' + line.pop(0)
                assert n_options == 11
                value = line
                if key not in [cls.KEYS.ADC_IMPERVIOUS, cls.KEYS.ADC_PERVIOUS]:
                    raise NotImplementedError()

            else:
                raise NotImplementedError()

            data[key] = value

        return data


class MapSection(InpSectionGeneric):
    """
    Section: [**MAP**]

    Purpose:
        Provides dimensions and distance units for the map.

    Formats:
        ::

            DIMENSIONS X1 Y1 X2 Y2
            UNITS FEET / METERS / DEGREES / NONE

    Args:
        dimensions (list[float, float, float, float]): lower-left and upper-right coordinates of the full map extent

            - lower_left_x (:obj:`float`): lower-left X coordinate ``X1``
            - lower_left_y (:obj:`float`): lower-left Y coordinate ``Y1``
            - upper_right_x (:obj:`float`): upper-right X coordinate ``X2``
            - upper_right_y (:obj:`float`): upper-right Y coordinate ``Y2``
        units (str): one of FEET / METERS / DEGREES / NONE see :py:attr:`~MapSection.UNITS`

    Attributes:
        lower_left_x (float): lower-left X coordinate ``X1``
        lower_left_y (float): lower-left Y coordinate ``Y1``
        upper_right_x (float): upper-right X coordinate ``X2``
        upper_right_y (float): upper-right Y coordinate ``Y2``
        units (str): one of FEET / METERS / DEGREES / NONE see :py:attr:`~MapSection.UNITS`
    """
    _section_label = SEC.MAP

    class KEYS:
        DIMENSIONS = 'DIMENSIONS'
        UNITS = 'UNITS'

    class UNIT_OPTIONS:
        FEET = 'FEET'
        METERS = 'METERS'
        DEGREES = 'DEGREES'
        NONE = None

    @classmethod
    def from_inp_lines(cls, lines):
        """
        read ``.inp``-file lines and create an section object

        Args:
            lines (str | list[list[str]]): lines in the section of the ``.inp``-file

        Returns:
            InpSectionGeneric: object of the Map-section
        """
        data = cls()
        for key, *line in line_iter(lines):
            key = key.upper()
            if key == cls.KEYS.DIMENSIONS:
                data[key] = [float(i) for i in line]

            elif key == cls.KEYS.UNITS:
                data[key] = line[0]
            else:
                raise NotImplementedError()
        return data


class FilesSection(InpSectionGeneric):
    """
    Section: [**FILES**]

    Purpose:
        Identifies optional interface files used or saved by a run.

    Format:
        ::

            USE / SAVE RAINFALL Fname
            USE / SAVE RUNOFF Fname
            USE / SAVE HOTSTART Fname
            USE / SAVE RDII Fname
            USE INFLOWS Fname
            SAVE OUTFLOWS Fname

    Remarks:
        Fname
            is the name of an interface file.

        Refer to Section 11.7 Interface Files for a description of interface files. Rainfall, Runoff, and
        RDII files can either be used or saved in a run, but not both. A run can both use and save a Hot
        Start file (with different names).
    """
    _section_label = SEC.FILES

    class KEYS:
        USE = 'USE'
        SAVE = 'SAVE'

        _use_or_save = [USE, SAVE]

        RAINFALL = 'RAINFALL'
        RUNOFF = 'RUNOFF'
        HOTSTART = 'HOTSTART'
        RDII = 'RDII'
        INFLOWS = 'INFLOWS'
        OUTFLOWS = 'OUTFLOWS'

        _possible = [RAINFALL, RUNOFF, HOTSTART, RDII, INFLOWS, OUTFLOWS]

    def __setitem__(self, key, item):
        InpSectionGeneric.__setitem__(self, key, item)

    def __delitem__(self, key):
        InpSectionGeneric.__delitem__(self, key)

    @classmethod
    def from_inp_lines(cls, lines):
        """
        read ``.inp``-file lines and create an section object

        Args:
            lines (str | list[list[str]]): lines in the section of the ``.inp``-file

        Returns:
            InpSectionGeneric: object of the Files-section
        """
        data = cls()
        for use_save, kind, *fn in line_iter(lines):
            use_save = use_save.upper()
            kind = kind.upper()
            assert use_save in cls.KEYS._use_or_save
            assert kind in cls.KEYS._possible
            data[f'{use_save} {kind}'] = ' '.join(fn).strip('"')
        return data

    def use(self, kind, filename):
        self[f'{self.KEYS.USE} {kind}'] = filename

    def save(self, kind, filename):
        self[f'{self.KEYS.SAVE} {kind}'] = filename


class AdjustmentsSection(InpSectionGeneric):
    """
    Section: [**ADJUSTMENTS**]

    Purpose:
        Specifies optional monthly adjustments to be made to temperature, evaporation rate,
        rainfall intensity and hydraulic conductivity in each time period of a simulation.

    Format:
        ::

            TEMPERATURE  t1 t2 t3 t4 t5 t6 t7 t8 t9 t10 t11 t12
            EVAPORATION  e1 e2 e3 e4 e5 e6 e7 e8 e9 e10 e11 e12
            RAINFALL     r1 r2 r3 r4 r5 r6 r7 r8 r9 r10 r11 r12
            CONDUCTIVITY c1 c2 c3 c4 c5 c6 c7 c8 c9 c10 c11 c12

    Remarks:
        t1..t12
            adjustments to temperature in January, February, etc., as plus or minus degrees F (degrees C).
        e1..e12
            adjustments to evaporation rate in January, February, etc., as plus or minus in/day (mm/day).
        r1..r12
            multipliers applied to precipitation rate in January, February, etc.
        c1..c12
            multipliers applied to soil hydraulic conductivity in January, February, etc. used in either Horton or
            Green-Ampt infiltration.

        The same adjustment is applied for each time period within a given month and is repeated for that
        month in each subsequent year being simulated.
    """
    _section_label = SEC.ADJUSTMENTS

    class KEYS:
        TEMPERATURE = 'TEMPERATURE'
        EVAPORATION = 'EVAPORATION'
        RAINFALL = 'RAINFALL'
        CONDUCTIVITY = 'CONDUCTIVITY'

        _possible = [TEMPERATURE, EVAPORATION, RAINFALL, CONDUCTIVITY]

    @classmethod
    def from_inp_lines(cls, lines):
        """
        read ``.inp``-file lines and create an section object

        Args:
            lines (str | list[list[str]]): lines in the section of the ``.inp``-file

        Returns:
            InpSectionGeneric: object of the Adjustments-section
        """
        data = cls()
        for key, *factors in line_iter(lines):
            key = key.upper()
            assert len(factors) == 12
            assert key in cls.KEYS._possible
            data[key] = [float(i) for i in factors]
        return data


class BackdropSection(InpSectionGeneric):
    """
    Section: [**BACKDROP**]

    Purpose:
        Specifies file name and coordinates of map’s backdrop image.

    Format:
        ::

            TFILE        Fname
            DIMENSIONS   X1 Y1 X2 Y2

    Remarks:
        Fname
            name of file containing backdrop image
        X1
            lower-left X coordinate of backdrop image
        Y1
            lower-left Y coordinate of backdrop image
        X2
            upper-right X coordinate of backdrop image
        Y2
            upper-right Y coordinate of backdrop image
    """
    _section_label = SEC.BACKDROP

    class KEYS:
        FILE = 'FILE'
        DIMENSIONS = 'DIMENSIONS'
        UNITS = 'UNITS'  # not in documentation
        OFFSET = 'OFFSET'  # not in documentation
        SCALING = 'SCALING'  # not in documentation

    @classmethod
    def from_inp_lines(cls, lines):
        """
        read ``.inp``-file lines and create an section object

        Args:
            lines (str | list[list[str]]): lines in the section of the ``.inp``-file

        Returns:
            InpSectionGeneric: object of the Backdrop-section
        """
        data = cls()
        for key, *line in line_iter(lines):
            key = key.upper()
            if key == cls.KEYS.FILE:
                data[key] = ' '.join(line)
            elif key == cls.KEYS.DIMENSIONS:
                assert len(line) == 4
                data[key] = [float(i) for i in line]
            elif key in [cls.KEYS.UNITS, cls.KEYS.OFFSET, cls.KEYS.SCALING]:
                # unknown behavior not in documentation
                data[key] = ' '.join(line)
            else:
                raise NotImplementedError()
        return data
