from numpy import NaN
from pandas import DataFrame, Series, Timestamp

from ._identifiers import IDENTIFIERS
from .._type_converter import infer_type, to_bool, str_to_datetime, datetime_to_str, type2str
from ..helpers import BaseSectionObject, split_line_with_quotes
from ..section_abr import SEC


class RainGage(BaseSectionObject):
    """
    Section: [**RAINGAGES**]

    Purpose:
        Identifies each rain gage that provides rainfall data for the study area.

    Formats:
        ::

            Name Form Intvl SCF TIMESERIES Tseries
            Name Form Intvl SCF FILE       Fname   Sta Units

    Format-PCSWMM:
        ``Name Format Interval SCF Source``

    Args:
        Name (str): name assigned to rain gage.
        Format (str): form of recorded rainfall, either INTENSITY, VOLUME or CUMULATIVE.
        Interval (str, Timedelta): time interval between gage readings in decimal hours or hours:minutes format
                                    (e.g., 0:15 for 15-minute readings). ``Intvl``
        SCF (float): snow catch deficiency correction factor (use 1.0 for no adjustment).
        Source (str): one of ``'TIMESERIES'`` ``'FILE'``
        *args: for automatic inp file reading
        Timeseries (str): name of time series in [TIMESERIES] section with rainfall data. ``Tseries``
        Filename (str): name of external file with rainfall data.
                        Rainfall files are discussed in Section 11.3 Rainfall Files. ``Fname``
        Station (str): name of recording station used in the rain file. ``Sta``
        Units (str): rain depth units used in the rain file, either IN (inches) or MM (millimeters).

    Attributes:
        Name (str): name assigned to rain gage.
        Format (str): form of recorded rainfall, either INTENSITY, VOLUME or CUMULATIVE.
        Interval (str, Timedelta): time interval between gage readings in decimal hours or hours:minutes format
                                    (e.g., 0:15 for 15-minute readings). ``Intvl``
        SCF (float): snow catch deficiency correction factor (use 1.0 for no adjustment).
        Source (str): one of ``'TIMESERIES'`` ``'FILE'``
        Timeseries (str): name of time series in [TIMESERIES] section with rainfall data. ``Tseries``
        Filename (str): name of external file with rainfall data.
                        Rainfall files are discussed in Section 11.3 Rainfall Files. ``Fname``
        Station (str): name of recording station used in the rain file. ``Sta``
        Units (str): rain depth units used in the rain file, either IN (inches) or MM (millimeters).
    """
    _identifier = IDENTIFIERS.Name
    _section_label = SEC.RAINGAGES

    class FORMATS:
        INTENSITY = 'INTENSITY'
        VOLUME = 'VOLUME'
        CUMULATIVE = 'CUMULATIVE'

    class SOURCES:
        TIMESERIES = 'TIMESERIES'
        FILE = 'FILE'

    class UNITS:
        IN = 'IN'
        MM = 'MM'

    def __init__(self, Name, Format, Interval, SCF, Source, *args, Timeseries=NaN, Filename=NaN, Station=NaN,
                 Units=NaN):
        self.Name = str(Name)
        self.Format = Format
        self.Interval = Interval
        self.SCF = float(SCF)
        self.Source = Source

        self.Timeseries = Timeseries
        self.Filename = Filename
        self.Station = Station
        self.Units = Units

        if args:
            if (Source == RainGage.SOURCES.TIMESERIES) and (len(args) == 1):
                self.Timeseries = args[0]

            elif Source == RainGage.SOURCES.FILE:
                self.Filename = args[0]
                self.Station = args[1]
                self.Units = args[2]

            else:
                raise NotImplementedError()


class Symbol(BaseSectionObject):
    """
    Section: [**SYMBOLS**]

    Purpose:
        Assigns X,Y coordinates to rain gage symbols.

    Format:
        ::

            Gage Xcoord Ycoord

    Args:
        Gage (str): name of gage.
        x (float): horizontal coordinate relative to origin in lower left of map. ``Xcoord``
        y (float): vertical coordinate relative to origin in lower left of map. ``Ycoord``

    Attributes:
        Gage (str): name of gage.
        x (float): horizontal coordinate relative to origin in lower left of map. ``Xcoord``
        y (float): vertical coordinate relative to origin in lower left of map. ``Ycoord``
    """
    _identifier = IDENTIFIERS.Gage
    _section_label = SEC.SYMBOLS

    def __init__(self, Gage, x, y):
        self.Gage = str(Gage)
        self.x = float(x)
        self.y = float(y)


class Pattern(BaseSectionObject):
    """
    Section: [**PATTERNS**]

    Purpose:
        Specifies time pattern of dry weather flow or quality in the form of adjustment factors
        applied as multipliers to baseline values.


    Format:
        ::

            Name MONTHLY Factor1 Factor2 ... Factor12
            Name DAILY Factor1  Factor2  ...  Factor7
            Name HOURLY Factor1  Factor2  ...  Factor24
            Name WEEKEND Factor1  Factor2  ...  Factor24

    Remarks:
        The MONTHLY format is used to set monthly pattern factors for dry weather flow constituents.

        The DAILY format is used to set dry weather pattern factors for each day of the week, where Sunday is day 1.

        The HOURLY format is used to set dry weather factors for each hour of the day starting from midnight.
        If these factors are different for weekend days than for weekday days then the WEEKEND format can be used
        to specify hourly adjustment factors just for weekends.

        More than one line can be used to enter a pattern’s factors by repeating the pattern’s name
        (but not the pattern type) at the beginning of each additional line.

        The pattern factors are applied as multipliers to any baseline dry weather flows or quality
        concentrations supplied in the [DWF] section.

    Examples:
        ::

            ; Day of week adjustment factors
            D1 DAILY 0.5 1.0 1.0 1.0 1.0 1.0 0.5
            D2 DAILY 0.8 0.9 1.0 1.1 1.0 0.9 0.8

            ; Hourly adjustment factors
            H1 HOURLY 0.5 0.6 0.7 0.8 0.8 0.9
            H1        1.1 1.2 1.3 1.5 1.1 1.0
            H1        0.9 0.8 0.7 0.6 0.5 0.5
            H1        0.5 0.5 0.5 0.5 0.5 0.5

    Args:
        Name (str): name used to identify the pattern.
        Type (str): one of ``MONTHLY``, ``DAILY``, ``HOURLY``, ``WEEKEND``
        Factors (list): multiplier values.
        *factors: for automatic inp file reading

    Attributes:
        Name (str): name used to identify the pattern.
        Type (str): one of ``MONTHLY``, ``DAILY``, ``HOURLY``, ``WEEKEND``
        Factors (list): multiplier values.
    """
    _identifier = IDENTIFIERS.Name
    _section_label = SEC.PATTERNS

    class TYPES:
        __class__ = 'Patter Types'
        MONTHLY = 'MONTHLY'
        DAILY = 'DAILY'
        HOURLY = 'HOURLY'
        WEEKEND = 'WEEKEND'

    def __init__(self, Name, Type, *factors, Factors=None):
        self.Name = str(Name)
        self.Type = Type
        if Factors is not None:
            self.Factors = Factors
        else:
            self.Factors = list(float(f) for f in factors)

    @classmethod
    def _convert_lines(cls, multi_line_args):
        args = list()
        for line in multi_line_args:
            if line[1] in [cls.TYPES.MONTHLY, cls.TYPES.DAILY,
                           cls.TYPES.HOURLY, cls.TYPES.WEEKEND]:
                if args:
                    yield cls(*args)
                args = line
            else:
                args += line[1:]
        # last
        if args:
            yield cls(*args)

    def to_inp_line(self):
        if self.Type in (self.TYPES.MONTHLY, self.TYPES.HOURLY, self.TYPES.WEEKEND):
            s = ''
            import numpy as np

            l = len(self.Type)
            first = True
            for a in np.array_split(self.Factors, int(len(self.Factors) / 6)):
                if first:
                    s += f'{self.Name} {self.Type} '
                    first = False
                else:
                    s += f'\n{self.Name} {" ":<{l}} '
                s += ' '.join([type2str(i) for i in a])
            return s
        else:
            return super().to_inp_line()


class Pollutant(BaseSectionObject):
    """
    Section: [**POLLUTANTS**]

    Purpose:
        Identifies the pollutants being analyzed.

    Format:
        ::

            Name Units Crain Cgw Cii Kd (Sflag CoPoll CoFract Cdwf Cinit)

    Format-PCSWMM:
        ``Name Units Crain Cgw Crdii Kdecay SnowOnly Co-Pollutant Co-Frac Cdwf Cinit``

    Remarks:
        ``FLOW`` is a reserved word and cannot be used to name a pollutant.

        Parameters Sflag through Cinit can be omitted if they assume their default values.
        If there is no co-pollutant but non-default values for Cdwf or Cinit, then enter an asterisk (``*``)
        for the co-pollutant name.

        When pollutant X has a co-pollutant Y, it means that fraction CoFract of pollutant Y's runoff
        concentration is added to pollutant X's runoff concentration when wash off from a subcatchment is computed.

        The dry weather flow concentration can be overridden for any specific node of the conveyance
        system by editing the node's Inflows property.

    Args:
        Name (str): name assigned to pollutant.
        unit (str): concentration units

                - ``MG/L`` for milligrams per liter
                - ``UG/L`` for micrograms per liter
                - ``#/L`` for direct count per liter

        Crain (float): concentration of pollutant in rainfall (concentration units).
        Cgw (float): concentration of pollutant in groundwater (concentration units).
        Crdii (float): concentration of pollutant in inflow/infiltration (concentration units). ``Cii``
        Kdecay (float): first-order decay coefficient (1/days).
        SnowOnly (bool): ``YES`` if pollutant buildup occurs only when there is snow cover, ``NO`` otherwise (default
        is ``NO``). ``Sflag``
        Co_Pollutant (str): name of co-pollutant (default is no co-pollutant designated by a ``*``). ``CoPoll``
        Co_Frac (float): fraction of co-pollutant concentration (default is 0). ``CoFract``
        Cdwf (float): pollutant concentration in dry weather flow (default is 0).
        Cinit (float): pollutant concentration throughout the conveyance system at the start of the simulation (
        default is 0).

    Attributes:
        Name (str): name assigned to pollutant.
        unit (str): concentration units

                - ``MG/L`` for milligrams per liter
                - ``UG/L`` for micrograms per liter
                - ``#/L`` for direct count per liter

        Crain (float): concentration of pollutant in rainfall (concentration units).
        Cgw (float): concentration of pollutant in groundwater (concentration units).
        Crdii (float): concentration of pollutant in inflow/infiltration (concentration units). ``Cii``
        Kdecay (float): first-order decay coefficient (1/days).
        SnowOnly (bool): ``YES`` if pollutant buildup occurs only when there is snow cover, ``NO`` otherwise (default
        is ``NO``). ``Sflag``
        Co_Pollutant (str): name of co-pollutant (default is no co-pollutant designated by a ``*``). ``CoPoll``
        Co_Frac (float): fraction of co-pollutant concentration (default is 0). ``CoFract``
        Cdwf (float): pollutant concentration in dry weather flow (default is 0).
        Cinit (float): pollutant concentration throughout the conveyance system at the start of the simulation (
        default is 0).
    """
    _identifier = IDENTIFIERS.Name
    _section_label = SEC.POLLUTANTS

    class UNITS:
        MG_PER_L = 'MG/L'
        UG_PER_L = 'UG/L'
        COUNT_PER_L = '#/L'

    def __init__(self, Name, unit, Crain, Cgw, Crdii, Kdecay,
                 SnowOnly=False, Co_Pollutant='*', Co_Frac=0, Cdwf=0, Cinit=0):
        self.Name = str(Name)
        self.unit = str(unit)
        self.Crain = float(Crain)
        self.Cgw = float(Cgw)
        self.Crdii = float(Crdii)
        self.Kdecay = float(Kdecay)
        self.SnowOnly = to_bool(SnowOnly)
        self.Co_Pollutant = str(Co_Pollutant)
        self.Co_Frac = float(Co_Frac)
        self.Cdwf = float(Cdwf)
        self.Cinit = float(Cinit)


class Transect(BaseSectionObject):
    """
    Section: [**TRANSECTS**]

    Purpose:
        Describes the cross-section geometry of natural channels or conduits with irregular shapes
        following the HEC-2 data format.

    Formats:

        ::

            NC Nleft Nright Nchanl
            X1 Name Nsta Xleft Xright 0 0 0 Lfactor Wfactor Eoffset
            GR Elev Station ... Elev Station

    Remarks:
        Transect geometry is described as shown below, assuming that one is looking in a downstream direction:

        The first line in this section must always be a NC line. After that, the NC line is only needed when a
        transect has
        different Manning’s n values than the previous one.

        The Manning’s n values on the NC line will supersede any roughness value entered for the conduit which uses the
        irregular cross-section.

        There should be one X1 line for each transect.
        Any number of GR lines may follow, and each GR line can have any number of Elevation-Station data pairs.
        (In HEC-2 the GR line is limited to 5 stations.)

        The station that defines the left overbank boundary on the X1 line must correspond to one of the station entries
        on the GR lines that follow. The same holds true for the right overbank boundary. If there is no match,
        a warning
        will be issued and the program will assume that no overbank area exists.

        The meander modifier is applied to all conduits that use this particular transect for their cross section.
        It assumes that the length supplied for these conduits is that of the longer main channel.
        SWMM will use the shorter overbank length in its calculations while increasing the main channel roughness to
        account
        for its longer length.

    Args:
        roughness_left (float): Manning’s n of right overbank portion of channel (use 0 if no change from previous NC
        line). ``Nleft``
        roughness_right (float): Manning’s n of right overbank portion of channel (use 0 if no change from previous
        NC line. ``Nright``
        roughness_channel (float): Manning’s n of main channel portion of channel (use 0 if no change from previous
        NC line. ``Nchanl``
        Name (str): name assigned to transect.
        bank_station_left (float): station position which ends the left overbank portion of the channel (ft or m).
        ``Xleft``
        bank_station_right (float): station position which begins the right overbank portion of the channel (ft or
        m). ``Xright``
        modifier_meander (float): meander modifier that represents the ratio of the length of a meandering main
        channel to the length of the overbank area that surrounds it (use 0 if not applicable). ``Lfactor``
        modifier_stations (float): factor by which distances between stations should be multiplied to increase (or
        decrease) the width of the channel (enter 0 if not applicable). ``Wfactor``
        modifier_elevations (float): amount added (or subtracted) from the elevation of each station (ft or m).
        ``Eoffset``
        station_elevations (list[list[float, float]]): of the tuple:

            Elev (float): elevation of the channel bottom at a cross-section station relative to some fixed reference
            (ft or m).
            Station (float): distance of a cross-section station from some fixed reference (ft or m).

    Attributes:
        roughness_left (float): Manning’s n of right overbank portion of channel (use 0 if no change from previous NC
        line). ``Nleft``
        roughness_right (float): Manning’s n of right overbank portion of channel (use 0 if no change from previous
        NC line. ``Nright``
        roughness_channel (float): Manning’s n of main channel portion of channel (use 0 if no change from previous
        NC line. ``Nchanl``
        Name (str): name assigned to transect.
        bank_station_left (float): station position which ends the left overbank portion of the channel (ft or m).
        ``Xleft``
        bank_station_right (float): station position which begins the right overbank portion of the channel (ft or
        m). ``Xright``
        modifier_meander (float): meander modifier that represents the ratio of the length of a meandering main
        channel to the length of the overbank area that surrounds it (use 0 if not applicable). ``Lfactor``
        modifier_stations (float): factor by which distances between stations should be multiplied to increase (or
        decrease) the width of the channel (enter 0 if not applicable). ``Wfactor``
        modifier_elevations (float): amount added (or subtracted) from the elevation of each station (ft or m).
        ``Eoffset``
        station_elevations (list[list[float, float]]): of the tuple:

            Elev (float): elevation of the channel bottom at a cross-section station relative to some fixed reference
            (ft or m).
            Station (float): distance of a cross-section station from some fixed reference (ft or m).
    """
    _identifier = IDENTIFIERS.Name
    _table_inp_export = False
    _section_label = SEC.TRANSECTS

    class KEYS:
        NC = 'NC'
        X1 = 'X1'
        GR = 'GR'

    def __init__(self, Name, station_elevations=None, bank_station_left=0, bank_station_right=0,
                 roughness_left=0, roughness_right=0, roughness_channel=0,
                 modifier_stations=0, modifier_elevations=0, modifier_meander=0):
        self.Name = str(Name)

        self.roughness_left = None
        self.roughness_right = None
        self.roughness_channel = None
        self.set_roughness(roughness_left, roughness_right, roughness_channel)

        self.bank_station_left = None
        self.bank_station_right = None
        self.set_bank_stations(bank_station_left, bank_station_right)

        self.modifier_stations = None
        self.modifier_elevations = None
        self.modifier_meander = None
        self.set_modifiers(modifier_meander, modifier_stations, modifier_elevations)

        self.station_elevations = list()

        if station_elevations is not None:
            for s in station_elevations:
                self.add_station_elevation(*s)

    def add_station_elevation(self, station, elevation):
        self.station_elevations.append([float(station), float(elevation)])

    def set_roughness(self, left=0., right=0., channel=0.):
        self.roughness_left = float(left)
        self.roughness_right = float(right)
        self.roughness_channel = float(channel)

    def set_bank_stations(self, left=0., right=0.):
        self.bank_station_left = float(left)
        self.bank_station_right = float(right)

    def set_modifiers(self, meander=0., stations=0., elevations=0.):
        self.modifier_stations = float(stations)
        self.modifier_elevations = float(elevations)
        self.modifier_meander = float(meander)

    def get_number_stations(self):
        """``Nsta`` number of stations across cross-section at which elevation data is supplied."""
        return len(self.station_elevations)

    @classmethod
    def _convert_lines(cls, multi_line_args):
        last_roughness = [0, 0, 0]
        last = None

        for line in multi_line_args:
            if line[0] == cls.KEYS.NC:
                last_roughness = line[1:]

            elif line[0] == cls.KEYS.X1:
                if last is not None:
                    yield last
                last = cls(Name=line[1])
                last.set_bank_stations(*line[3:5])
                last.set_modifiers(*line[8:])
                last.set_roughness(*last_roughness)

            elif line[0] == cls.KEYS.GR:
                it = iter(line[1:])
                for station in it:
                    elevation = next(it)
                    last.add_station_elevation(station, elevation)
        yield last

    def to_inp_line(self, break_every=1):
        """
        Args:
            break_every: break every x-th GR station, default: after every station
        """
        s = '{} {} {} {}\n'.format(self.KEYS.NC, self.roughness_left, self.roughness_right, self.roughness_channel)
        s += '{} {} {} {} {} 0 0 0 {} {} {}\n'.format(self.KEYS.X1, self.Name, self.get_number_stations(),
                                                      self.bank_station_left, self.bank_station_right,
                                                      self.modifier_meander, self.modifier_stations,
                                                      self.modifier_elevations, )
        if break_every == 1:
            for x, y in self.station_elevations:
                s += '{} {} {}\n'.format(self.KEYS.GR, x, y)
        else:
            s += self.KEYS.GR
            i = 0
            for x, y in self.station_elevations:
                s += ' {} {}'.format(x, y)
                i += 1
                if i == break_every:
                    i = 0
                    s += '\n' + self.KEYS.GR

        if s.endswith(self.KEYS.GR):
            s = s[:-3]
        s += '\n'
        return s


class Control(BaseSectionObject):
    """
    Section: [**CONTROLS**]

    Purpose:
        Determines how pumps and regulators will be adjusted
        based on simulation time or conditions at specific nodes and links.

    Formats:
        Each control rule is a series of statements of the form:
        ::

            RULE    ruleID
            IF      condition_1
            AND     condition_2
            OR      condition_3
            AND     condition_4
            Etc.
            THEN    action_1
            AND     action_2
            Etc.
            ELSE    action_3
            AND     action_4
            Etc.
            PRIORITY value

    Remarks:
        `RuleID`: an ID label assigned to the rule.
        `condition_n`: a condition clause.
        `action_n`: an action clause.
        `value`: a priority value (e.g., a number from 1 to 5).

        A **condition clause** of a Control Rule has the following format:
            `Object Name Attribute Relation Value`

        where:
            - `Object`: is a category of object,
            - `Name`: is the object’s assigned ID name,
            - `Attribute`: is the name of an attribute or property of the object,
            - `Relation`: is a relational operator (=, <>, <, <=, >, >=), and
            - `Value`: is an attribute value.

        for example:
        ::

            NODE N23 DEPTH > 10
            PUMP P45 STATUS = OFF
            SIMULATION TIME = 12:45:00
            NODE  N23  DEPTH  >  10
            NODE  N23  DEPTH  >  NODE 25 DEPTH
            PUMP  P45  STATUS =  OFF
            LINK  P45  TIMEOPEN >= 6:30
            SIMULATION CLOCKTIME = 22:45:00

        TIMEOPEN is the duration a link has been in an OPEN or ON state or have its
        SETTING be greater than zero; TIMECLOSED is the duration it has remained in a
        CLOSED or OFF state or have its SETTING be zero.

        +------------+------------+----------------------------------+
        | Object     | Attributes | Value                            |
        +============+============+==================================+
        | NODE       | DEPTH      | numerical value                  |
        +------------+------------+----------------------------------+
        |            | HEAD       | numerical value                  |
        +------------+------------+----------------------------------+
        |            | VOLUME     | numerical value                  |
        +------------+------------+----------------------------------+
        |            | INFLOW     | numerical value                  |
        +------------+------------+----------------------------------+
        | LINK       | FLOW       | numerical value                  |
        +------------+------------+----------------------------------+
        |            | DEPTH      | numerical value                  |
        +------------+------------+----------------------------------+
        |            | TIMEOPEN   | decimal hours or hr:min          |
        +------------+------------+----------------------------------+
        |            | TIMECLOSED | decimal hours or hr:min          |
        +------------+------------+----------------------------------+
        | CONDUIT    | STATUS     | OPEN or CLOSED                   |
        +------------+------------+----------------------------------+
        |            | TIMEOPEN   | decimal hours or hr:min          |
        +------------+------------+----------------------------------+
        |            | TIMECLOSED | decimal hours or hr:min          |
        +------------+------------+----------------------------------+
        | PUMP       | STATUS     | ON or OFF                        |
        +------------+------------+----------------------------------+
        |            | SETTING    | pump curve multiplier            |
        +------------+------------+----------------------------------+
        |            | FLOW       | numerical value                  |
        +------------+------------+----------------------------------+
        |            | TIMEOPEN   | decimal hours or hr:min          |
        +------------+------------+----------------------------------+
        |            | TIMECLOSED | decimal hours or hr:min          |
        +------------+------------+----------------------------------+
        | ORIFICE    | SETTING    | fraction open                    |
        +------------+------------+----------------------------------+
        |            | TIMEOPEN   | decimal hours or hr:min          |
        +------------+------------+----------------------------------+
        |            | TIMECLOSED | decimal hours or hr:min          |
        +------------+------------+----------------------------------+
        | WEIR       | SETTING    | fraction open                    |
        +------------+------------+----------------------------------+
        |            | TIMEOPEN   | decimal hours or hr:min          |
        +------------+------------+----------------------------------+
        |            | TIMECLOSED | decimal hours or hr:min          |
        +------------+------------+----------------------------------+
        | OUTLET     | SETTING    | rating curve multiplier          |
        +------------+------------+----------------------------------+
        |            | TIMEOPEN   | decimal hours or hr:min          |
        +------------+------------+----------------------------------+
        |            | TIMECLOSED | decimal hours or hr:min          |
        +------------+------------+----------------------------------+
        | SIMULATION | TIME       | elapsed time in decimal hours or |
        +------------+------------+----------------------------------+
        |            |            | hr:min:sec                       |
        +------------+------------+----------------------------------+
        | SIMULATION | DATE       | month/day/year                   |
        +------------+------------+----------------------------------+
        |            | MONTH      | month of year (January = 1)      |
        +------------+------------+----------------------------------+
        |            | DAY        | day of week (Sunday = 1)         |
        +------------+------------+----------------------------------+
        |            | CLOCKTIME  | time of day in hr:min:sec        |
        +------------+------------+----------------------------------+

        An **Action Clause** of a Control Rule has the following format:
            `Object Name Action = Value`
            `PUMP id STATUS = ON/OFF`
            `PUMP/ORIFICE/WEIR/OUTLET id SETTING = value`

        where:
            - `Object`: is a category of object,
            - `Name`: is the object’s assigned ID name,
            - `Action`: is the type of action
            - `Value`: is the action value/setting/status.

        where the meaning of SETTING depends on the object being controlled:
            - for Pumps it is a multiplier applied to the flow computed from the pump curve,
            - for Orifices it is the fractional amount that the orifice is fully open,
            - for Weirs it is the fractional amount of the original freeboard that exists (i.e., weir control is accomplished by moving the crest height up or down),
            - for Outlets it is a multiplier applied to the flow computed from the outlet's rating curve.

        Modulated controls are control rules that provide for a continuous degree of control
        applied to a pump or flow regulator as determined by the value of some controller
        variable, such as water depth at a node, or by time. The functional relation between
        the control setting and the controller variable is specified by using a control curve, a
        time series, or a PID controller. To model these types of controls, the value entry on
        the right-hand side of the action clause is replaced by the keyword CURVE,
        TIMESERIES, or PID and followed by the id name of the respective control curve or
        time series or by the gain, integral time (in minutes), and derivative time (in minutes)
        of a PID controller. For direct action control the gain is a positive number while for
        reverse action control it must be a negative number. By convention, the controller
        variable used in a control curve or PID control will always be the object and attribute
        named in the last condition clause of the rule. The value specified for this clause will
        be the setpoint used in a PID controller.


        for example:
        ::

            PUMP P67 STATUS = OFF
            ORIFICE O212 SETTING = 0.5
            WEIR W25 SETTING = CURVE C25
            ORIFICE ORI_23 SETTING = PID 0.1 0.1 0.0

        Only the RULE, IF and THEN portions of a rule are required; the other portions are optional.
        When mixing AND and OR clauses, the OR operator has higher precedence than AND, i.e., `IF A or B and C`
        is equivalent to `IF (A or B) and C.`
        If the interpretation was meant to be `IF A or (B and C)`
        then this can be expressed using two rules as in `IF A THEN ... IF B and C THEN ...`

        The PRIORITY value is used to determine which rule applies when two or more rules
        require that conflicting actions be taken on a link. A conflicting rule with a higher
        priority value has precedence over one with a lower value (e.g., PRIORITY 5
        outranks PRIORITY 1). A rule without a priority value always has a lower priority
        than one with a value. For two rules with the same priority value, the rule that
        appears first is given the higher priority.


    Examples:
        ::

            ; Simple time-based pump control
            RULE R1
            IF SIMULATION TIME > 8
            THEN PUMP 12 STATUS = ON
            ELSE PUMP 12 STATUS = OFF

            ; Multi-condition orifice gate control
            RULE R2A
            IF NODE 23 DEPTH > 12
            AND LINK 165 FLOW > 100
            THEN ORIFICE R55 SETTING = 0.5

            RULE R2B
            IF NODE 23 DEPTH > 12
            AND LINK 165 FLOW > 200
            THEN ORIFICE R55 SETTING = 1.0

            RULE R2C
            IF NODE 23 DEPTH <= 12
            OR LINK 165 FLOW <= 100
            THEN ORIFICE R55 SETTING = 0

            ; PID controller that attempts to keep Node 23’s depth at 12:
            RULE PID_1
            IF NODE 23 DEPTH <> 12
            THEN ORIFICE R55 SETTING = PID 0.5 0.1 0.0

            ; Pump station operation with a main (N1A) and lag (N1B) pump
            RULE R3A
            IF NODE N1 DEPTH > 5
            THEN PUMP N1A STATUS = ON

            RULE R3B
            IF PUMP N1A TIMEOPEN > 2:30
            THEN PUMP N1B STATUS = ON
            ELSE PUMP N1B STATUS = OFF

            RULE R3C
            IF NODE N1 DEPTH <= 0.5
            THEN PUMP N1A STATUS = OFF
            AND PUMP N1B STATUS = OFF

    """
    _identifier = IDENTIFIERS.Name
    _table_inp_export = False
    _section_label = SEC.CONTROLS

    class Clauses:
        __class__ = 'Clauses'
        RULE = 'RULE'
        IF = 'IF'
        THEN = 'THEN'
        PRIORITY = 'PRIORITY'
        AND = 'AND'
        OR = 'OR'

    def __init__(self, Name, conditions, actions, priority=0):
        self.Name = str(Name)
        self.conditions = conditions
        self.actions = actions
        self.priority = int(priority)

    @classmethod
    def _convert_lines(cls, multi_line_args):
        args = list()
        is_condition = False
        is_action = False
        for line in multi_line_args:
            if line[0] == cls.Clauses.RULE:
                if args:
                    yield cls(*args)
                    args = list()
                args.append(line[1])
                is_action = False

            elif line[0] == cls.Clauses.IF:
                args.append([line[1:]])
                is_condition = True

            elif line[0] == cls.Clauses.THEN:
                args.append([line[1:]])
                is_condition = False
                is_action = True

            elif line[0] == cls.Clauses.PRIORITY:
                args.append(line[1])
                is_action = False

            elif is_condition:
                args[-1].append(line)

            elif is_action:
                args[-1].append(line)

        # last
        yield cls(*args)

    def to_inp_line(self):
        s = '{} {}\n'.format(self.Clauses.RULE, self.Name)
        s += '{} {}\n'.format(self.Clauses.IF, '\n'.join([' '.join(c) for c in self.conditions]))
        s += '{} {}\n'.format(self.Clauses.THEN, '\n'.join([' '.join(a) for a in self.actions]))
        s += '{} {}\n'.format(self.Clauses.PRIORITY, self.priority)
        return s


class Curve(BaseSectionObject):
    """
    Section: [**CURVES**]

    Purpose:
        Describes a relationship between two variables in tabular format.

    Format:
        ::

            Name Type X-value Y-value ...

    Format-PCSWMM:
            ``Name Type X-Value Y-Value``

    Remarks:
        Name
            name assigned to table
        Type
            ``STORAGE`` / ``SHAPE`` / ``DIVERSION`` / ``TIDAL`` / ``PUMP1`` / ``PUMP2`` / ``PUMP3`` / ``PUMP4`` /
            ``RATING`` / ``CONTROL``
        X-value
            an x (independent variable) value
        Y-value
            the y (dependent variable) value corresponding to x

        Multiple pairs of x-y values can appear on a line. If more than one line is needed,
        repeat the curve's name (but not the type) on subsequent lines. The x-values must
        be entered in increasing order.

        Choices for curve type have the following meanings (flows are expressed in the
        user’s choice of flow units set in the [``OPTIONS``] section):

            ``STORAGE``
                surface area in ft2 (m2) v. depth in ft (m) for a storage unit node
            ``SHAPE``
                width v. depth for a custom closed cross-section, both normalized with respect to full depth
            ``DIVERSION``
                diverted outflow v. total inflow for a flow divider node
            ``TIDAL``
                water surface elevation in ft (m) v. hour of the day for an outfall node
            ``PUMP1``
                pump outflow v. increment of inlet node volume in ft3 (m3)
            ``PUMP2``
                pump outflow v. increment of inlet node depth in ft (m)
            ``PUMP3``
                pump outflow v. head difference between outlet and inlet nodes in ft (m)
            ``PUMP4``
                pump outflow v. continuous depth in ft (m)
            ``RATING``
                outlet flow v. head in ft (m)
            ``CONTROL``
                control setting v. controller variable

    Examples:
        ::

            ;Storage curve (x = depth, y = surface area)
            AC1 STORAGE 0 1000 2 2000 4 3500 6 4200 8 5000
            ;Type1 pump curve (x = inlet wet well volume, y = flow )
            PC1 PUMP1
            PC1 100 5 300 10 500 20

    Args:
        Name (str): name assigned to table
        Type (str): one of ``STORAGE`` / ``SHAPE`` / ``DIVERSION`` / ``TIDAL`` / ``PUMP1`` / ``PUMP2`` / ``PUMP3`` /
        ``PUMP4`` / ``RATING`` / ``CONTROL``
        points (list[list[float, float]]): tuple of X-value (an independent variable) and  Y-value (an dependent
        variable)

    Attributes:
        Name (str): name assigned to table
        Type (str): one of ``STORAGE`` / ``SHAPE`` / ``DIVERSION`` / ``TIDAL`` / ``PUMP1`` / ``PUMP2`` / ``PUMP3`` /
        ``PUMP4`` / ``RATING`` / ``CONTROL``
        points (list[list[float, float]]): tuple of X-value (an independent variable) and  Y-value (an dependent
        variable)
    """
    _identifier = IDENTIFIERS.Name
    _table_inp_export = False
    _section_label = SEC.CURVES

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

    @classmethod
    def _get_names(cls, Type):
        TYPES = cls.TYPES
        if Type == TYPES.STORAGE:
            return ['depth', 'area']
        elif Type == TYPES.SHAPE:
            return ['depth', 'width']
        elif Type == TYPES.DIVERSION:
            return ['inflow', 'outflow']
        elif Type == TYPES.TIDAL:
            return ['hour', 'elevation']
        elif Type == TYPES.PUMP1:
            return ['volume', 'outflow']
        elif Type == TYPES.PUMP2:
            return ['depth', 'outflow']
        elif Type == TYPES.PUMP3:
            return ['head diff', 'outflow']
        elif Type == TYPES.PUMP4:
            return ['depth', 'outflow']
        elif Type == TYPES.RATING:
            return ['head', 'flow']
        elif Type == TYPES.CONTROL:
            return ['variable', 'setting']

    def __init__(self, Name, Type, points):
        self.Name = str(Name)
        self.Type = Type.upper()
        self.points = points

    @classmethod
    def _convert_lines(cls, multi_line_args):
        last = None
        Type = None
        points = list()
        for name, *line in multi_line_args:
            remains = iter(line)

            if name != last:
                # new curve line
                if last is not None:
                    # first return previous curve
                    yield cls(last, Type, points)
                # reset variables
                points = list()
                last = name
                Type = next(remains)

            # points in current line
            for a in remains:
                b = next(remains)
                points.append(infer_type([a, b]))

        # last
        if last is not None:
            yield cls(last, Type, points)

    @property
    def frame(self):
        return DataFrame.from_records(self.points, columns=self._get_names(self.Type))

    def to_inp_line(self):
        points = iter(self.points)
        x, y = next(points)
        f = '{}  {} {:7.4f} {:7.4f}\n'.format(self.Name, self.Type, x, y)
        Type = ' ' * len(self.Type)
        for x, y in points:  # [(x,y), (x,y), ...]
            f += '{}  {} {:7.4f} {:7.4f}\n'.format(self.Name, Type, x, y)
        return f


class Timeseries(BaseSectionObject):
    """
    Section: [**TIMESERIES**]

    Purpose:
        Describes how a quantity varies over time.

    Formats:
        ::

            Name ( Date ) Hour Value ...
            Name Time Value ...
            Name FILE Fname

    Remarks:
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
        ::

            ;Rainfall time series with dates specified
            TS1 6-15-2001 7:00 0.1 8:00 0.2 9:00 0.05 10:00 0
            TS1 6-21-2001 4:00 0.2 5:00 0 14:00 0.1 15:00 0

            ;Inflow hydrograph - time relative to start of simulation
            HY1 0 0 1.25 100 2:30 150 3.0 120 4.5 0
            HY1 32:10 0 34.0 57 35.33 85 48.67 24 50 0

    Args:
        Name (str): name assigned to time series.
    """
    _identifier = IDENTIFIERS.Name
    _table_inp_export = False
    _section_label = SEC.TIMESERIES

    class TYPES:
        FILE = 'FILE'

    def __init__(self, Name):
        self.Name = str(Name)

    @classmethod
    def _convert_lines(cls, multi_line_args):
        data = list()
        last = None
        last_date = None

        for name, *line in multi_line_args:
            # ---------------------------------
            if line[0].upper() == cls.TYPES.FILE:
                yield TimeseriesFile(name, ' '.join(line[1:]))
                last = name

            # ---------------------------------
            else:
                if name != last:
                    if last is not None:
                        yield TimeseriesData(last, data)
                    data = list()
                    last = name
                    last_date = None

                # -------------
                iterator = iter(line)
                for part in iterator:
                    if ('/' in part) or (('-' in part) and not part.startswith('-')):
                        # MM-DD-YYYY or MM/DD/YYYY or MMM-DD-YYYY MMM/DD/YYYY
                        last_date = part

                        # HH:MM or HH:MM:SS or H (as float)
                        time = next(iterator)
                    else:
                        # HH:MM or HH:MM:SS or H (as float)
                        time = part

                    if last_date is not None:
                        index = ' '.join([last_date, time])
                    else:
                        index = time

                    value = float(next(iterator))

                    data.append([index, value])

        # add last timeseries
        if data and (line[0].upper() != cls.TYPES.FILE):
            yield TimeseriesData(last, data)


class TimeseriesFile(Timeseries):
    """
    Section: [**TIMESERIES**]

    Purpose:
        Describes how a quantity varies over time.

    Formats:
        ::

            Name FILE Fname

    Args:
        Name (str): name assigned to time series.
        filename (str): name of a file in which the time series data are stored ``Fname``
    """

    def __init__(self, Name, filename, kind=None):
        Timeseries.__init__(self, Name)
        self.kind = self.TYPES.FILE
        self.filename = filename

    def to_inp_line(self):
        fn = self.filename.strip('"')
        return f'{self.Name} {self.kind} "{fn}"'


class TimeseriesData(Timeseries):
    """
    Section: [**TIMESERIES**]

    Purpose:
        Describes how a quantity varies over time.

    Formats:
        ::

            Name ( Date ) Hour Value ...
            Name Time Value ...

    Args:
        Name (str): name assigned to time series.
        data (list[tuple]): list of index/value tuple with:

            - Date: date in Month/Day/Year format (e.g., June 15, 2001 would be 6/15/2001).
            - Hour: 24-hour military time (e.g., 8:40 pm would be 20:40) relative to the last date specified
                   (or to midnight of the starting date of the simulation if no previous date was specified).
            - Time: hours since the start of the simulation, expressed as a decimal number or as hours:minutes.
            - Value: value corresponding to given date and time.
    """

    def __init__(self, Name, data):
        Timeseries.__init__(self, Name)
        self.data = data
        self._fix_index()

    def _fix_index(self):
        """
        convert string index to pandas.Timestamp (datetime like) or float

        index format supported by SWMM:
        - '%m/%d/%Y %H:%M'
        - '%b/%d/%Y %H:%M'
        - '%m-%d-%Y %H:%M'
        - '%b-%d-%Y %H:%M'
        - '%m/%d/%Y %H:%M:%S'
        - '%b/%d/%Y %H:%M:%S'
        - '%m-%d-%Y %H:%M:%S'
        - '%b-%d-%Y %H:%M:%S'
        - Hours as float relative to simulation start time
        """
        date_time, values = zip(*self.data)
        date_time_new = list()
        last_date = None
        if len(date_time) > 10000 * 2:  # 10000 it/s
            str_only = True
        else:
            str_only = False

        for dt in date_time:
            if isinstance(dt, Timestamp):
                date_time_new.append(dt)
            elif isinstance(dt, float):
                date_time_new.append(dt)
            else:
                parts = dt.split()
                if len(parts) == 1:
                    time = parts[0]
                else:
                    last_date, time = parts

                date_time_new.append(str_to_datetime(last_date, time, str_only=str_only))
        if str_only:
            import pandas as pd
            date_time_new = pd.to_datetime(date_time_new, format='%m/%d/%Y %H:%M:%S')
        self.data = list(zip(date_time_new, values))

    @property
    def frame(self):
        """
        convert object to pandas Series

        Returns:
            pandas.Series: Timeseries
        """
        datetime, values = zip(*self.data)
        return Series(index=datetime, data=values, name=self.Name)

    def to_inp_line(self):
        f = ''
        for date_time, value in self.data:
            f += f'{self.Name} {datetime_to_str(date_time)} {value}\n'
        return f

    @classmethod
    def from_pandas(cls, series, label=None):
        """
        convert pandas Series to TimeseriesData object

        Args:
            series (pandas.Series): timeseries with DateTimeIndex
                or index with correct formatted for SWMM:
                - '%m/%d/%Y %H:%M'
                - '%b/%d/%Y %H:%M'
                - '%m-%d-%Y %H:%M'
                - '%b-%d-%Y %H:%M'
                - '%m/%d/%Y %H:%M:%S'
                - '%b/%d/%Y %H:%M:%S'
                - '%m-%d-%Y %H:%M:%S'
                - '%b-%d-%Y %H:%M:%S'
                - Hours as float relative to simulation start time
            label (str): optional: label of the series. default: take series.name

        Returns:
            TimeseriesData: object for inp file
        """
        if label is None:
            label = series.name
        return cls(label, list(zip(series.index, series.values)))


class Tag(BaseSectionObject):
    """Section: [**TAGS**]"""
    _identifier = ['kind', IDENTIFIERS.Name]
    _section_label = SEC.TAGS

    class TYPES:
        Node = IDENTIFIERS.Node
        Subcatch = IDENTIFIERS.Subcatch
        Link = IDENTIFIERS.Link

    def __init__(self, kind, Name, tag, *tags):
        self.kind = kind.lower().capitalize()
        self.Name = Name
        self.tag = tag
        if tags:
            self.tag += '_' + '_'.join(tags)


class Label(BaseSectionObject):
    """
    Section: [**LABELS**]

    Purpose:
        Assigns X,Y coordinates to user-defined map labels.

    Format:
        ::

            Xcoord Ycoord Label (Anchor Font Size Bold Italic)

    Args:
        x (float):
            horizontal coordinate relative to origin in lower left of map.
        y (float):
            vertical coordinate relative to origin in lower left of map.
        label (str):
            text of label surrounded by double quotes.
        anchor (str):
            name of node or subcatchment that anchors the label on zoom-ins (use an empty pair of double quotes if
            there is no anchor).
        font (str):
            name of label’s font (surround by double quotes if the font name includes spaces).
        size (float):
            font size in points.
        bold (bool):
            YES for bold font, NO otherwise.
        italic (bool):
            YES for italic font, NO otherwise.
    """
    _identifier = ['x', 'y', 'label']
    _section_label = SEC.LABELS

    def __init__(self, x, y, label, anchor=NaN, font=NaN, size=NaN, bold=NaN, italic=NaN):
        self.x = float(x)
        self.y = float(y)
        self.label = label
        self.anchor = anchor
        self.font = font
        self.size = size
        self.bold = bold
        self.italic = italic

    @classmethod
    def from_inp_line(cls, *line):
        return cls(*split_line_with_quotes(line))


class Hydrograph(BaseSectionObject):
    """
    Section: [**HYDROGRAPHS**]

    Purpose:
        Specifies the shapes of the triangular unit hydrographs that determine the amount of
        rainfall-dependent infiltration/inflow (RDII) entering the drainage system.

    Formats:
        ::

            Name Raingage
            Name Month SHORT/MEDIUM/LONG R T K (Dmax Drec D0)

    Remarks:
        Name
            name assigned to a unit hydrograph group.
        Raingage
            name of the rain gage used by the unit hydrograph group.
        Month
            month of the year (e.g., JAN, FEB, etc. or ALL for all months).
        R
            response ratio for the unit hydrograph.
        T
            time to peak (hours) for the unit hydrograph.
        K
            recession limb ratio for the unit hydrograph.
        Dmax
            maximum initial abstraction depth available (in rain depth units).
        Drec
            initial abstraction recovery rate (in rain depth units per day)
        D0
            initial abstraction depth already filled at the start of the simulation (in rain depth units).

        For each group of unit hydrographs, use one line to specify its rain gage followed by
        as many lines as are needed to define each unit hydrograph used by the group
        throughout the year. Three separate unit hydrographs, that represent the short-term,
        medium-term, and long-term RDII responses, can be defined for each month (or all
        months taken together). Months not listed are assumed to have no RDII.

        The response ratio (R) is the fraction of a unit of rainfall depth that becomes RDII.
        The sum of the ratios for a set of three hydrographs does not have to equal 1.0.

        The recession limb ratio (K) is the ratio of the duration of the hydrograph’s recession
        limb to the time to peak (T) making the hydrograph time base equal to T*(1+K) hours.
        The area under each unit hydrograph is 1 inch (or mm).

        The optional initial abstraction parameters determine how much rainfall is lost at the
        start of a storm to interception and depression storage. If not supplied then the
        default is no initial abstraction.

    Examples:
        ::

            ; All three unit hydrographs in this group have the same shapes except those in July,
            ; which have only a short- and medium-term response and a different shape.
            UH101 RG1
            UH101 ALL SHORT 0.033 1.0 2.0
            UH101 ALL MEDIUM 0.300 3.0 2.0
            UH101 ALL LONG 0.033 10.0 2.0
            UH101 JUL SHORT 0.033 0.5 2.0
            UH101 JUL MEDIUM 0.011 2.0 2.0

    Args:
        Name (str): name assigned to time series.
    """
    _identifier = IDENTIFIERS.Name
    _table_inp_export = False
    _section_label = SEC.HYDROGRAPHS

    class TYPES:
        SHORT = 'SHORT'
        MEDIUM = 'MEDIUM'
        LONG = 'LONG'

    class MONTHS:
        JAN = 'JAN'
        FEB = 'FEB'
        MAR = 'MAR'
        APR = 'APR'
        MAI = 'MAI'
        JUN = 'JUN'
        JUL = 'JUL'
        AUG = 'AUG'
        SEP = 'SEP'
        OCT = 'OCT'
        NOV = 'NOV'
        DEC = 'DEC'

        ALL = 'ALL'

        _possible = [JAN, FEB, MAR, APR, MAI, JUN, JUL, AUG, SEP, OCT, NOV, DEC, ALL]

    def __init__(self, Name, rain_gage):
        self.Name = str(Name)
        self.rain_gage = rain_gage
        self.monthly_definitions = list()

    @classmethod
    def _convert_lines(cls, multi_line_args):
        last = None

        for name, *line in multi_line_args:
            # ---------------------------------
            if line[0].upper() not in cls.MONTHS._possible:
                if last is not None:
                    yield last
                last = cls(name, rain_gage=line[0])
            elif name == last.Name:
                last.monthly_definitions.append(cls.HydrographMonth(name, *line))
        yield last

    class HydrographMonth(BaseSectionObject):
        _identifier = IDENTIFIERS.Name

        def __init__(self, Name, month, response, response_ratio, time_to_peak, recession_limb_ratio,
                     depth_max=NaN, depth_recovery=NaN, depth_init=NaN):
            """

            Args:
                Name (str): name assigned to a unit hydrograph group.
                month (str):
                response (str):
                response_ratio (float):
                time_to_peak (float):
                recession_limb_ratio (float):
                depth_max (str):
                depth_recovery (str):
                depth_init (str):
            """
            self.Name = str(Name)
            self.month = month
            self.response = response
            self.response_ratio = float(response_ratio)
            self.time_to_peak = float(time_to_peak)
            self.recession_limb_ratio = float(recession_limb_ratio)
            self.depth_max = depth_max
            self.depth_recovery = depth_recovery
            self.depth_init = depth_init

    def to_inp_line(self):
        s = '{} {}\n'.format(self.Name, self.rain_gage)
        for hyd in self.monthly_definitions:
            s += hyd.to_inp_line() + '\n'
        return s


class LandUse(BaseSectionObject):
    """
    Section: [**LANDUSES**]

    Purpose:
        Identifies the various categories of land uses within the drainage area. Each
        subcatchment area can be assigned a different mix of land uses. Each land use can
        be subjected to a different street sweeping schedule.

    Formats:
        ::

            Name (SweepInterval Availability LastSweep)

    Args:
        Name:
            land use name.
        sweep_interval:
            days between street sweeping.
        availability:
            fraction of pollutant buildup available for removal by street sweeping.
        last_sweep:
            days since last sweeping at start of the simulation.
    """
    _identifier = IDENTIFIERS.Name
    _section_label = SEC.LANDUSES

    def __init__(self, Name, sweep_interval=NaN, availability=NaN, last_sweep=NaN):
        self.Name = str(Name)
        self.sweep_interval = float(sweep_interval)
        self.availability = float(availability)
        self.last_sweep = float(last_sweep)


class WashOff(BaseSectionObject):
    """
    Section: [**WASHOFF**]

    Purpose:
        Specifies the rate at which pollutants are washed off from different land uses during rain events.

    Formats:
        ::

            Landuse Pollutant FuncType C1 C2 SweepRmvl BmpRmvl

    Args:
        landuse:
            land use name.
        pollutant:
            pollutant name.
        func_type:
            washoff function type: ``EXP`` / ``RC`` / ``EMC``.
        C1 (float):
            washoff function coefficients(see Table D-3).
        C2 (float):
            washoff function coefficients(see Table D-3).
        sweeping_removal (float):
            street sweeping removal efficiency (percent) .
        BMP_removal (float):
            BMP removal efficiency (percent).

    Remarks:
        Table D-3 Pollutant wash off functions

        +------+--------------------------+--------------------------+------------+
        | Name | Function                 | Equation                 | Units      |
        +------+--------------------------+--------------------------+------------+
        | EXP  | Exponential              | C1 (runoff) C2 (buildup) | Mass/hour  |
        +------+--------------------------+--------------------------+------------+
        | RC   | Rating Curve             | C1 (runoff) C2           | Mass/sec   |
        +------+--------------------------+--------------------------+------------+
        | EMC  | Event Mean Concentration | C1                       | Mass/Liter |
        +------+--------------------------+--------------------------+------------+

        Each washoff function expresses its results in different units.

        For the Exponential function the runoff variable is expressed in catchment depth
        per unit of time (inches per hour or millimeters per hour), while for the Rating Curve
        function it is in whatever flow units were specified in the [``OPTIONS``] section of the
        input file (e.g., ``CFS``, ``CMS``, etc.).

        The buildup parameter in the Exponential function is the current total buildup over
        the subcatchment’s land use area in mass units. The units of C1 in the Exponential
        function are (in/hr)
        -C2 per hour (or (mm/hr) -C2 per hour). For the Rating Curve
        function, the units of ``C1`` depend on the flow units employed. For the EMC (event
        mean concentration) function, ``C1`` is always in concentration units.

    """
    _identifier = [IDENTIFIERS.Landuse, IDENTIFIERS.Pollutant]
    _section_label = SEC.WASHOFF

    class FUNCTIONS:
        EXP = 'EXP'
        RC = 'RC'
        EMC = 'EMC'

    def __init__(self, landuse, pollutant, func_type, C1, C2, sweeping_removal, BMP_removal):
        self.landuse = landuse
        self.pollutant = pollutant
        self.func_type = func_type
        self.C1 = float(C1)
        self.C2 = float(C2)
        self.sweeping_removal = float(sweeping_removal)
        self.BMP_removal = float(BMP_removal)


class BuildUp(BaseSectionObject):
    """
    Section: [**BUILDUP**]

    Purpose:
        Specifies the rate at which pollutants build up over different land uses between rain events.

    Formats:
        ::

            Landuse Pollutant FuncType C1 C2 C3 PerUnit

    Args:
        landuse:
            land use name.
        pollutant:
            pollutant name.
        func_type:
            buildup function type: ( ``POW`` / ``EXP`` / ``SAT`` / ``EXT`` ).
        C1 (float):
            buildup function parameters (see Table).
        C2 (float):
            buildup function parameters (see Table).
        C3 (float):
            buildup function parameters (see Table).
        per_unit (str):
            ``AREA`` if buildup is per unit area, ``CURBLENGTH`` if per length of curb.

    Remarks:
        Buildup is measured in pounds (kilograms) per unit of area (or curb length) for
        pollutants whose concentration units are either mg/L or ug/L. If the concentration
        units are counts/L, then the buildup is expressed as counts per unit of area (or curb
        length).

        Table: Pollutant buildup functions (t is antecedent dry days)

        +------+-------------+---------------------+
        | Name | Function    | Equation            |
        +------+-------------+---------------------+
        | POW  | Power       | Min (C1, C2*t^C3 )  |
        +------+-------------+---------------------+
        | EXP  | Exponential | C1*(1 – exp(-C2*t)) |
        +------+-------------+---------------------+
        | SAT  | Saturation  | C1*t / (C3 + t)     |
        +------+-------------+---------------------+
        | EXT  | External    | See below           |
        +------+-------------+---------------------+

        For the EXT buildup function, C1 is the maximum possible buildup (mass per area or
        curb length), C2 is a scaling factor, and C3 is the name of a Time Series that
        contains buildup rates (as mass per area or curb length per day) as a function of
        time.
    """
    _identifier = [IDENTIFIERS.Landuse, IDENTIFIERS.Pollutant]
    _section_label = SEC.BUILDUP

    class FUNCTIONS:
        EXP = 'EXP'
        RC = 'RC'
        EMC = 'EMC'

    class UNIT:
        AREA = 'AREA'
        CURBLENGTH = 'CURBLENGTH'
        CURB = 'CURB'

    def __init__(self, landuse, pollutant, func_type, C1, C2, C3, per_unit):
        self.landuse = landuse
        self.pollutant = pollutant
        self.func_type = func_type
        self.C1 = float(C1)
        self.C2 = float(C2)
        self.C3 = float(C3)
        self.per_unit = per_unit


class SnowPack(BaseSectionObject):
    """
    Section: [**SNOWPACKS**]

    Purpose:
        Specifies parameters that govern how snowfall accumulates and melts on the
        plowable, impervious and pervious surfaces of subcatchments.

    Formats:
        ::

            Name PLOWABLE Cmin Cmax Tbase FWF SD0 FW0 SNN0
            Name IMPERVIOUS Cmin Cmax Tbase FWF SD0 FW0 SD100
            Name PERVIOUS Cmin Cmax Tbase FWF SD0 FW0 SD100
            Name REMOVAL Dplow Fout Fimp Fperv Fimelt (Fsub Scatch)

    Args:
        Name (str):
            name assigned to snowpack parameter set.
        Cmin (float):
            minimum melt coefficient (in/hr-deg F or mm/hr-deg C).
        Cmax (float):
            maximum melt coefficient (in/hr-deg F or mm/hr-deg C).
        Tbase (float):
            snow melt base temperature (deg F or deg C).
        FWF (float):
            ratio of free water holding capacity to snow depth (fraction).
        SD0 (float):
            initial snow depth (in or mm water equivalent).
        FW0 (float):
            initial free water in pack (in or mm).
        SNN0 (float):
            fraction of impervious area that can be plowed.
        SD100 (float):
            snow depth above which there is 100% cover (in or mm water equivalent).
        Dplow (float):
            depth of snow on plowable areas at which snow removal begins (in or mm).
        Fout (float):
            fraction of snow on plowable area transferred out of watershed.
        Fimp (float):
            fraction of snow on plowable area transferred to impervious area by plowing.
        Fperv (float):
            fraction of snow on plowable area transferred to pervious area by plowing.
        Fimelt (float):
            fraction of snow on plowable area converted into immediate melt.
        Fsub (float):
            fraction of snow on plowable area transferred to pervious area in another subcatchment.
        Scatch (str):
            name of subcatchment receiving the Fsub fraction of transferred snow.

    Remarks:
        Use one set of PLOWABLE, IMPERVIOUS, and PERVIOUS lines for each snow pack
        parameter set created. Snow pack parameter sets are associated with specific
        subcatchments in the [SUBCATCHMENTS] section. Multiple subcatchments can share
        the same set of snow pack parameters.

        The PLOWABLE line contains parameters for the impervious area of a subcatchment
        that is subject to snow removal by plowing but not to areal depletion. This area is the
        fraction SNN0 of the total impervious area. The IMPERVIOUS line contains parameter
        values for the remaining impervious area and the PERVIOUS line does the same for
        the entire pervious area. Both of the latter two areas are subject to areal depletion.

        The REMOVAL line describes how snow removed from the plowable area is
        transferred onto other areas. The various transfer fractions should sum to no more
        than 1.0. If the line is omitted then no snow removal takes place.
    """
    _identifier = IDENTIFIERS.Name
    _section_label = SEC.SNOWPACKS
    _table_inp_export = False

    def __init__(self, Name, packs=None):
        self.Name = str(Name)
        self.PLOWABLE = None
        self.IMPERVIOUS = None
        self.PERVIOUS = None
        self.REMOVAL = None

        if isinstance(packs, dict):
            for p in packs:
                if p in self:
                    self[p] = packs[p]
        elif isinstance(packs, list):
            for p in packs:
                self.add_pack(p)
        elif packs is None:
            pass
        else:
            raise NotImplementedError(f'SnowPack packs tpye "{type(packs)}" not implemented!')

    def add_pack(self, p):
        if type(p) in self.TYPES._type2_dict:
            self[self.TYPES._type2_dict[type(p)]] = p

    @classmethod
    def _convert_lines(cls, multi_line_args):
        last = None

        for name, kind, *line in multi_line_args:
            # ---------------------------------
            if last is None:
                last = cls(name)

            elif name != last.Name:
                yield last
                last = cls(name)

            kind = kind.upper()
            last[kind] = cls.TYPES._type_dict[kind](*line)
        yield last

    class TYPES:
        class _Base(BaseSectionObject):
            _table_inp_export = False
            _identifier = IDENTIFIERS.Name
            _section_label = SEC.SNOWPACKS

            def __init__(self, Cmin, Cmax, Tbase, FWF, SD0, FW0):
                self.Cmin = float(Cmin)
                self.Cmax = float(Cmax)
                self.Tbase = float(Tbase)
                self.FWF = float(FWF)
                self.SD0 = float(SD0)
                self.FW0 = float(FW0)

        class Plowable(_Base):
            _LABEL = 'PLOWABLE'

            def __init__(self, Cmin, Cmax, Tbase, FWF, SD0, FW0, SNN0):
                SnowPack.TYPES._Base.__init__(self, Cmin, Cmax, Tbase, FWF, SD0, FW0)
                self.SNN0 = float(SNN0)

        class Pervious(_Base):
            _LABEL = 'PERVIOUS'

            def __init__(self, Cmin, Cmax, Tbase, FWF, SD0, FW0, SD100):
                SnowPack.TYPES._Base.__init__(self, Cmin, Cmax, Tbase, FWF, SD0, FW0)
                self.SD100 = float(SD100)

        class Impervious(Pervious):
            _LABEL = 'IMPERVIOUS'

        class Removal(BaseSectionObject):
            _LABEL = 'REMOVAL'

            def __init__(self, Dplow, Fout, Fimp, Fperv, Fimelt, Fsub=NaN, Scatch=NaN):
                self.Dplow = float(Dplow)
                self.Fout = float(Fout)
                self.Fimp = float(Fimp)
                self.Fperv = float(Fperv)
                self.Fimelt = float(Fimelt)
                self.Fsub = float(Fsub)
                self.Scatch = Scatch

        PLOWABLE = Plowable._LABEL
        IMPERVIOUS = Pervious._LABEL
        PERVIOUS = Impervious._LABEL
        REMOVAL = Removal._LABEL

        _possible = [PLOWABLE, IMPERVIOUS, PERVIOUS, REMOVAL]

        _type_dict = {PLOWABLE: Plowable,
                      IMPERVIOUS: Pervious,
                      PERVIOUS: Impervious,
                      REMOVAL: Removal}
        _type2_dict = {Plowable: PLOWABLE,
                       Pervious: IMPERVIOUS,
                       Impervious: PERVIOUS,
                       Removal: REMOVAL}

    def to_inp_line(self):
        s = ''
        for pack in self.TYPES._possible:
            if self[pack] is not None:
                s += f'{self.Name} {pack:<8} {self[pack].to_inp_line()}\n'
        return s


class Aquifer(BaseSectionObject):
    """
    Section: [**AQUIFERS**]

    Purpose:
        Supplies parameters for each unconfined groundwater aquifer in the study area.
        Aquifers consist of two zones – a lower saturated zone and an upper unsaturated
        zone with a moving boundary between the two.

    Formats:
        ::

            Name Por WP FC Ks Kslp Tslp ETu ETs Seep Ebot Egw Umc (Epat)

    Args:
        Name (str):
            name assigned to aquifer.
        Por (float):
            soil porosity (volumetric fraction).
        WP (float):
            soil wilting point (volumetric fraction).
        FC (float):
            soil field capacity (volumetric fraction).
        Ks (float):
            saturated hydraulic conductivity (in/hr or mm/hr).
        Kslp (float):
            slope of the logarithm of hydraulic conductivity versus moisture deficit (i.e., porosity minus moisture
            content) curve (in/hr or mm/hr).
        Tslp (float):
            slope of soil tension versus moisture content curve (inches or mm).
        ETu (float):
            fraction of total evaporation available for evapotranspiration in the upper unsaturated zone.
        ETs (float):
            maximum depth into the lower saturated zone over which evapotranspiration can occur (ft or m).
        Seep (float):
            seepage rate from saturated zone to deep groundwater when water table is at ground surface (in/hr or mm/hr).
        Ebot (float):
            elevation of the bottom of the aquifer (ft or m).
        Egw (float):
            groundwater table elevation at start of simulation (ft or m).
        Umc (float):
            unsaturated zone moisture content at start of simulation (volumetric fraction).
        Epat (float):
            name of optional monthly time pattern used to adjust the upper zone evaporation fraction for different
            months of the year.

    Remarks:
        Local values for ``Ebot``, ``Egw``, and ``Umc`` can be assigned to specific subcatchments in
        the [``GROUNDWATER``] section described below.
    """
    _identifier = IDENTIFIERS.Name
    _section_label = SEC.AQUIFERS

    def __init__(self, Name, Por, WP, FC, Ks, Kslp, Tslp, ETu, ETs, Seep, Ebot, Egw, Umc, Epat=NaN):
        self.Name = str(Name)
        self.Por = float(Por)
        self.WP = float(WP)
        self.FC = float(FC)
        self.Ks = float(Ks)
        self.Kslp = float(Kslp)
        self.Tslp = float(Tslp)
        self.ETu = float(ETu)
        self.ETs = float(ETs)
        self.Seep = float(Seep)
        self.Ebot = float(Ebot)
        self.Egw = float(Egw)
        self.Umc = float(Umc)
        self.Epat = float(Epat)
