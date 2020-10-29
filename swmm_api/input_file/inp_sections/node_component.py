from numpy import NaN

from ..inp_helpers import BaseSectionObject
from.indices import Indices

class DryWeatherFlow(BaseSectionObject):
    """
    Section:
        [DWF]

    Purpose:
        Specifies dry weather flow and its quality entering the drainage system at specific nodes.

    Format:
        Node Type Base (Pat1 Pat2 Pat3 Pat4)

    Remarks:
        - Node:
            name of node where dry weather flow enters.
        - Type:
            keyword FLOW for flow or pollutant name for quality constituent.
        - Base:
            average baseline value for corresponding constituent (flow or concentration units).
        - Pat1, Pat2, etc.:
            names of up to four time patterns appearing in the [PATTERNS] section.

    The actual dry weather input will equal the product of the baseline value and any adjustment factors
    supplied by the specified patterns. (If not supplied, an adjustment factor defaults to 1.0.)
    The patterns can be any combination of monthly, daily, hourly and weekend hourly
    patterns, listed in any order. See the [PATTERNS] section for more details.
    """
    index = [Indices.Node, 'kind']

    def __init__(self, Node, kind, Base, pattern1=NaN, pattern2=NaN, pattern3=NaN, pattern4=NaN,
                 pattern5=NaN, pattern6=NaN, pattern7=NaN):
        """Specifies dry weather flow and its quality entering the drainage system at specific nodes.

        The actual dry weather input will equal the product of the baseline value and any adjustment factors
        supplied by the specified patterns. (If not supplied, an adjustment factor defaults to 1.0.)
        The patterns can be any combination of monthly, daily, hourly and weekend hourly
        patterns, listed in any order. See the [PATTERNS] section for more details.

        Args:
            Node (str): name of node where dry weather flow enters.
            kind (str): keyword FLOW for flow or pollutant name for quality constituent.
            Base (float): average baseline value for corresponding constituent (flow or concentration units).
            pattern1 (str, Optional): monthly-pattern
            pattern2 (str, Optional): daily-pattern
            pattern3 (str, Optional): hourly-pattern
            pattern4 (str, Optional): weekend-hourly-pattern
            pattern5 (str, Optional): ???
        """
        self.Node = str(Node)
        self.kind = kind
        self.Base = Base
        self.pattern1 = pattern1
        self.pattern2 = pattern2
        self.pattern3 = pattern3
        self.pattern4 = pattern4


class Inflow(BaseSectionObject):
    index = [Indices.Node, 'Constituent']

    class TypeOption:
        __class__ = 'Type Option'
        FLOW = 'FLOW'

    def __init__(self, Node, Constituent, TimeSeries=None, Type=TypeOption.FLOW, Mfactor=1.0, Sfactor=1.0, Baseline=0.,
                 Pattern=NaN):
        """
        Node FLOW   Tseries (FLOW (1.0     Sfactor Base Pat))
        Node Pollut Tseries (Type (Mfactor Sfactor Base Pat))

        Node
        Pollut
        Tseries
        Type        CONCEN* / MASS / FLOW
        Mfactor     (1.0)
        Sfactor     (1.0)
        Base        (0.0)
        Pat


        Node Constituent TimeSeries Type Mfactor Sfactor Baseline Pattern
        """
        self.Node = str(Node)
        self.Constituent = Constituent
        self.TimeSeries = TimeSeries
        self.Type = Type
        self.Mfactor = Mfactor
        self.Sfactor = Sfactor
        self.Baseline = Baseline
        self.Pattern = Pattern

        if (TimeSeries is None) or (TimeSeries == ''):
            self.TimeSeries = '""'


class Coordinate(BaseSectionObject):
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
    index = Indices.Node

    def __init__(self, Node, x, y):
        """Assigns X,Y coordinates to drainage system nodes.

        Args:
            Node (str): name of node.
            x (float): horizontal coordinate relative to origin in lower left of map.
            y (float): vertical coordinate relative to origin in lower left of map.
        """
        self.Node = str(Node)
        self.x = x
        self.y = y
