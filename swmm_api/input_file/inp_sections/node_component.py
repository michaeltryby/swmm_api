from numpy import NaN

from .identifiers import IDENTIFIERS
from ..inp_helpers import BaseSectionObject


class DryWeatherFlow(BaseSectionObject):
    """
    Section: [**DWF**]

    Purpose:
        Specifies dry weather flow and its quality entering the drainage system at specific nodes.

    Format:
        ::

            Node Type Base (Pat1 Pat2 Pat3 Pat4)

    Formats-PCSWMM:
        ``Node Parameter AverageValue TimePatterns``

    Formats-SWMM-GUI:
        ``Node Constituent Baseline Patterns``

    Remarks:
        Pat1, Pat2, etc.
            names of up to four time patterns appearing in the [``PATTERNS``] section.

        The actual dry weather input will equal the product of the baseline value and any adjustment factors
        supplied by the specified patterns. (If not supplied, an adjustment factor defaults to 1.0.)
        The patterns can be any combination of monthly, daily, hourly and weekend hourly
        patterns, listed in any order. See the [PATTERNS] section for more details.

    Args:
        Node (str): name of node where dry weather flow enters.
        Constituent (str): keyword ``FLOW`` for flow or pollutant name for quality constituent. ``Type``
        Base (float): average baseline value for corresponding constituent (flow or concentration units).
        pattern1 (str, Optional): i.e.: monthly-pattern ``Pat1``
        pattern2 (str, Optional): i.e.: daily-pattern ``Pat2``
        pattern3 (str, Optional): i.e.: hourly-pattern
        pattern4 (str, Optional): i.e.: weekend-hourly-pattern
    """
    _identifier = [IDENTIFIERS.Node, IDENTIFIERS.Constituent]

    class TYPES:
        FLOW = 'FLOW'

    def __init__(self, Node, Constituent, Base, pattern1=NaN, pattern2=NaN, pattern3=NaN, pattern4=NaN, *patternx):
        self.Node: str = str(Node)
        """name of node where dry weather flow enters."""

        self.Constituent: str = Constituent
        """keyword ``FLOW`` for flow or pollutant name for quality constituent. ``Type``"""

        self.Base: float = Base
        """average baseline value for corresponding constituent (flow or concentration units)."""

        self.pattern1: str = pattern1
        """i.e.: monthly-pattern ``Pat1``"""

        self.pattern2: str = pattern2
        """i.e.: daily-pattern ``Pat2``"""

        self.pattern3: str = pattern3
        """i.e.: hourly-pattern"""

        self.pattern4: str = pattern4
        """i.e. weekend-hourly-pattern"""


class Inflow(BaseSectionObject):
    """
    Section: [**INFLOWS**]

    Purpose:
        Specifies external hydrographs and pollutographs that enter the drainage system at specific nodes.

    Formats:
        ::

            Node FLOW   Tseries  (FLOW (1.0     Sfactor Base Pat))
            Node Pollut Tseries  (Type (Mfactor Sfactor Base Pat))

    Formats-PCSWMM:
        ``Node Parameter TimeSeries ParamType UnitsFactor ScaleFactor BaselineValue BaselinePattern``

    Formats-SWMM-GUI:
        ``Node Constituent TimeSeries Type Mfactor Sfactor Baseline Pattern``

    Remarks:
        External inflows are represented by both a constant and time varying component as follows:
        | Inflow = (Baseline value)*(Pattern factor) + (Scaling factor)*(Time series value)

        If an external inflow of a pollutant concentration is specified for a node,
        then there must also be an external inflow of FLOW provided for the same node, unless the node is an Outfall.
        In that case a pollutant can enter the system during periods
        when the outfall is submerged and reverse flow occurs.

    Examples:
        ::

            NODE2  FLOW N2FLOW
            NODE33 TSS  N33TSS CONCEN

            ;Mass inflow of BOD in time series N65BOD given in lbs/hr ;(126 converts lbs/hr to mg/sec)
            NODE65 BOD N65BOD MASS 126
            ;Flow inflow with baseline and scaling factor
            N176 FLOW FLOW_176 FLOW 1.0 0.5 12.7 FlowPat

    Args:
        Node (str): name of node where external inflow enters.
        Constituent (str): ``'FLOW'`` or name of pollutant. ``Pollut``
        TimeSeries (str): name of time series in [``TIMESERIES``] section describing how external flow or pollutant loading varies with time. ``Tseries``
        Type (str): ``'FLOW'`` or ``CONCEN`` if pollutant inflow is described as a concentration, ``MASS`` if it is described as a mass flow rate (default is ``CONCEN``).
        Mfactor (float): the factor that converts the inflow’s mass flow rate units into the project’s mass units per second, where the project’s mass units are those specified for the pollutant in the [POLLUTANTS] section (default is 1.0 - see example below).
        Sfactor (float): scaling factor that multiplies the recorded time series values (default is 1.0).
        Baseline (float): constant baseline value added to the time series value (default is 0.0). ``Base``
        Pattern (str): name of optional time pattern in [PATTERNS] section used to adjust the baseline value on a periodic basis. ``Pat``

    Attributes:
        Node (str): name of node where external inflow enters.
        Constituent (str): ``'FLOW'`` or name of pollutant. ``Pollut``
        TimeSeries (str): name of time series in [``TIMESERIES``] section describing how external flow or pollutant loading varies with time. ``Tseries``
        Type (str): ``'FLOW'`` or ``CONCEN`` if pollutant inflow is described as a concentration, ``MASS`` if it is described as a mass flow rate (default is ``CONCEN``).
        Mfactor (float): the factor that converts the inflow’s mass flow rate units into the project’s mass units per second, where the project’s mass units are those specified for the pollutant in the [POLLUTANTS] section (default is 1.0 - see example below).
        Sfactor (float): scaling factor that multiplies the recorded time series values (default is 1.0).
        Baseline (float): constant baseline value added to the time series value (default is 0.0). ``Base``
        Pattern (str): name of optional time pattern in [PATTERNS] section used to adjust the baseline value on a periodic basis. ``Pat``
    """
    _identifier = [IDENTIFIERS.Node, IDENTIFIERS.Constituent]

    class TYPES:
        FLOW = 'FLOW'
        CONCEN = 'CONCEN'
        MASS = 'MASS'

    def __init__(self, Node, Constituent, TimeSeries=None, Type=TYPES.FLOW, Mfactor=1.0, Sfactor=1.0, Baseline=0.,
                 Pattern=NaN):
        self.Node = str(Node)
        self.Constituent = str(Constituent)
        self.TimeSeries = TimeSeries
        self.Type = str(Type)
        self.Mfactor = float(Mfactor)
        self.Sfactor = float(Sfactor)
        self.Baseline = float(Baseline)
        self.Pattern = Pattern

        if (TimeSeries is None) or (TimeSeries == ''):
            self.TimeSeries = '""'


class Coordinate(BaseSectionObject):
    """
    Section: [**COORDINATES**]

    Purpose:
        Assigns X,Y coordinates to drainage system nodes.

    Format:
        ::

            Node Xcoord Ycoord

    Args:
        Node (str): name of node.
        x (float): horizontal coordinate relative to origin in lower left of map. ``Xcoord``
        y (float): vertical coordinate relative to origin in lower left of map. ``Ycoord``

    Attributes:
        Node (str): name of node.
        x (float): horizontal coordinate relative to origin in lower left of map. ``Xcoord``
        y (float): vertical coordinate relative to origin in lower left of map. ``Ycoord``
    """
    _identifier = IDENTIFIERS.Node

    def __init__(self, Node, x, y):
        self.Node = str(Node)
        self.x = float(x)
        self.y = float(y)

    @property
    def point(self):
        return self.x, self.y

    def to_inp_line(self):
        # separate function to keep accuracy
        return f'{self.Node} {self.x} {self.y}'
