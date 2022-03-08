from numpy import NaN, isnan

from ._identifiers import IDENTIFIERS
from .._type_converter import convert_string, GIS_FLOAT_FORMAT
from ..helpers import BaseSectionObject, InpSectionGeo
from ..section_labels import DWF, INFLOWS, COORDINATES, RDII, TREATMENT


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
    _identifier = (IDENTIFIERS.Node, IDENTIFIERS.Constituent)
    _section_label = DWF

    class TYPES:
        FLOW = 'FLOW'

    def __init__(self, Node, Constituent, Base, pattern1=NaN, pattern2=NaN, pattern3=NaN, pattern4=NaN, *patternx):
        self.Node: str = str(Node)
        """name of node where dry weather flow enters."""

        self.Constituent: str = Constituent
        """keyword ``FLOW`` for flow or pollutant name for quality constituent. ``Type``"""

        self.Base: float = float(Base)
        """average baseline value for corresponding constituent (flow or concentration units)."""

        self.pattern1: str = convert_string(pattern1)
        """i.e.: monthly-pattern ``Pat1``"""

        self.pattern2: str = convert_string(pattern2)
        """i.e.: daily-pattern ``Pat2``"""

        self.pattern3: str = convert_string(pattern3)
        """i.e.: hourly-pattern"""

        self.pattern4: str = convert_string(pattern4)
        """i.e. weekend-hourly-pattern"""

    def get_pattern_list(self):
        return [self[p] for p in ['pattern1', 'pattern2', 'pattern3', 'pattern4'] if isinstance(self[p], str)]


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
        TimeSeries (str): name of time series in [``TIMESERIES``] section describing how external flow or pollutant
            loading varies with time. ``Tseries``
        Type (str): ``'FLOW'`` or ``CONCEN`` if pollutant inflow is described as a concentration, ``MASS`` if it is
            described as a mass flow rate (default is ``CONCEN``).
        Mfactor (float): the factor that converts the inflow’s mass flow rate units into the project’s mass units per
            second, where the project’s mass units are those specified for the pollutant in the [POLLUTANTS] section (
            default is 1.0 - see example below).
        Sfactor (float): scaling factor that multiplies the recorded time series values (default is 1.0).
        Baseline (float): constant baseline value added to the time series value (default is 0.0). ``Base``
        Pattern (str): name of optional time pattern in [PATTERNS] section used to adjust the baseline value on a
            periodic basis. ``Pat``

    Attributes:
        Node (str): name of node where external inflow enters.
        Constituent (str): ``'FLOW'`` or name of pollutant. ``Pollut``
        TimeSeries (str): name of time series in [``TIMESERIES``] section describing how external flow or pollutant
            loading varies with time. ``Tseries``
        Type (str): ``'FLOW'`` or ``CONCEN`` if pollutant inflow is described as a concentration, ``MASS`` if it is
            described as a mass flow rate (default is ``CONCEN``).
        Mfactor (float): the factor that converts the inflow’s mass flow rate units into the project’s mass units per
            second, where the project’s mass units are those specified for the pollutant in the [POLLUTANTS] section (
            default is 1.0 - see example below).
        Sfactor (float): scaling factor that multiplies the recorded time series values (default is 1.0).
        Baseline (float): constant baseline value added to the time series value (default is 0.0). ``Base``
        Pattern (str): name of optional time pattern in [PATTERNS] section used to adjust the baseline value on a
            periodic basis. ``Pat``
    """
    _identifier = (IDENTIFIERS.Node, IDENTIFIERS.Constituent)
    _section_label = INFLOWS

    class TYPES:
        FLOW = 'FLOW'
        CONCEN = 'CONCEN'
        MASS = 'MASS'

    def __init__(self, Node, Constituent=TYPES.FLOW, TimeSeries=None, Type=TYPES.FLOW, Mfactor=1.0, Sfactor=1.0,
                 Baseline=0., Pattern=NaN):
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
    _section_label = COORDINATES
    _section_class = InpSectionGeo

    def __init__(self, Node, x, y):
        self.Node = str(Node)
        self.x = float(x)
        self.y = float(y)

    @property
    def point(self):
        return self.x, self.y

    def to_inp_line(self):
        # separate function to keep accuracy
        global GIS_FLOAT_FORMAT
        return f'{self.Node} {self.x:{GIS_FLOAT_FORMAT}} {self.y:{GIS_FLOAT_FORMAT}}'

    @property
    def geo(self):
        """
        get the shapely representation for the object (Point).

        Returns:
            shapely.geometry.Point: point object for the coordinates.
        """
        import shapely.geometry as sh
        return sh.Point(self.point)

    @classmethod
    def create_section_from_geoseries(cls, data):
        """
        create a COORDINATES inp-file section for a geopandas.GeoSeries

        Args:
            data (geopandas.GeoSeries): geopandas.GeoSeries of coordinates

        Returns:
            InpSectionGeo: COORDINATES inp-file section
        """
        return cls.create_section(zip(data.index, data.x, data.y))

    @classmethod
    def from_shapely(cls, Node, point):
        """
        Create a Coordinate object with a shapely Point

        Args:
            Node (str): label of the node
            point (shapely.geometry.Point):

        Returns:
            Coordinate: Coordinate object
        """
        return cls(Node, point.x, point.y)


class RainfallDependentInfiltrationInflow(BaseSectionObject):
    """
    Section: [**RDII**]

    Purpose:
        Specifies the parameters that describe rainfall-dependent infiltration/inflow (RDII)
        entering the drainage system at specific nodes.

    Format:
        ::

            Node UHgroup SewerArea

    Args:
        Node (str): name of node.
        hydrograph (str): name of an RDII unit hydrograph group specified in the [``HYDROGRAPHS``] section.
        sewer_area (float): area of the sewershed which contributes RDII to the node (acres or hectares).

    Attributes:
        Node (str): name of node.
        hydrograph (str): name of an RDII unit hydrograph group specified in the [``HYDROGRAPHS``] section.
        sewer_area (float): area of the sewershed which contributes RDII to the node (acres or hectares).
    """
    _identifier = IDENTIFIERS.Node
    _section_label = RDII

    def __init__(self, Node, hydrograph, sewer_area):
        self.Node = str(Node)
        self.hydrograph = str(hydrograph)
        self.sewer_area = float(sewer_area)


class Treatment(BaseSectionObject):
    """
    Section: [**TREATMENT**]

    Purpose:
        Specifies the degree of treatment received by pollutants at specific nodes of the drainage system.

    Format:
        ::

            Node Pollut Result = Func

    Args:
        Node (str): Name of node where treatment occurs.
        pollutant (str): Name of pollutant receiving treatment.
        result (str): Result computed by treatment function. Choices are C (function computes effluent concentration) R (function computes fractional removal).
        function (str): mathematical function expressing treatment result in terms of pollutant concentrations, pollutant removals, and other standard variables (see below).

    Attributes:
        Node (str): Name of node where treatment occurs.
        pollutant (str): Name of pollutant receiving treatment.
        result (str): Result computed by treatment function. Choices are C (function computes effluent concentration) R (function computes fractional removal).
        function (str): mathematical function expressing treatment result in terms of pollutant concentrations, pollutant removals, and other standard variables (see below).

    Remarks:
        Treatment functions can be any well-formed mathematical expression involving:
            - inlet pollutant concentrations (use the pollutant name to represent a concentration)
            - removal of other pollutants (use R\_ pre-pended to the pollutant name to represent removal)
            - process variables which include:
                - FLOW for flow rate into node (user’s flow units)
                - DEPTH for water depth above node invert (ft or m)
                - AREA for node surface area (ft2 or m2)
                - DT for routing time step (seconds)
                - HRT for hydraulic residence time (hours)

        Any of the following math functions can be used in a treatment function:
            - abs(x) for absolute value of x
            - sgn(x) which is +1 for x >= 0 or -1 otherwise
            - step(x) which is 0 for x <= 0 and 1 otherwise
            - sqrt(x) for the square root of x
            - log(x) for logarithm base e of x
            - log10(x) for logarithm base 10 of x
            - exp(x) for e raised to the x power
            - the standard trig functions (sin, cos, tan, and cot)
            - the inverse trig functions (asin, acos, atan, and acot)
            - the hyperbolic trig functions (sinh, cosh, tanh, and coth)

        along with the standard operators +, -, \*, /, ^ (for exponentiation ) and any level of nested parentheses.

    Examples:
        ::

            ; 1-st order decay of BOD
            Node23 BOD C = BOD * exp(-0.05*HRT)
            ; lead removal is 20% of TSS removal
            Node23 Lead R = 0.2 * R_TSS
    """
    _identifier = (IDENTIFIERS.Node, IDENTIFIERS.Pollutant)
    _section_label = TREATMENT

    def __init__(self, Node, pollutant, result, function):
        self.Node = str(Node)
        self.pollutant = str(pollutant)
        self.result = str(result)
        self.function = str(function)

    @classmethod
    def _convert_lines(cls, multi_line_args):
        for name, pollutant, *line in multi_line_args:
            result, function = ' '.join(line).split('=')
            yield cls(name, pollutant, result, function)

    def to_inp_line(self):
        """
        convert object to one line of the ``.inp``-file

        for ``.inp``-file writing

        Returns:
            str: SWMM .inp file compatible string
        """
        return f'{self.Node} {self.pollutant} {self.result} = {self.function}'
