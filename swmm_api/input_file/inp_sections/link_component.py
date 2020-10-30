from numpy import NaN
from pandas import DataFrame

from .identifiers import IDENTIFIERS
from ..inp_helpers import BaseSectionObject


class CrossSection(BaseSectionObject):
    identifier =IDENTIFIERS.Link

    class Shapes:
        IRREGULAR = 'IRREGULAR'
        CUSTOM = 'CUSTOM'
        CIRCULAR = 'CIRCULAR'
        FORCE_MAIN = 'FORCE_MAIN'
        FILLED_CIRCULAR = 'FILLED_CIRCULAR'
        RECT_CLOSED = 'RECT_CLOSED'
        RECT_OPEN = 'RECT_OPEN'
        TRAPEZOIDAL = 'TRAPEZOIDAL'
        TRIANGULAR = 'TRIANGULAR'
        HORIZ_ELLIPSE = 'HORIZ_ELLIPSE'
        VERT_ELLIPSE = 'VERT_ELLIPSE'
        ARCH = 'ARCH'
        PARABOLIC = 'PARABOLIC'
        POWER = 'POWER'
        RECT_TRIANGULAR = 'RECT_TRIANGULAR'
        RECT_ROUND = 'RECT_ROUND'
        MODBASKETHANDLE = 'MODBASKETHANDLE'
        EGG = 'EGG'
        HORSESHOE = 'HORSESHOE'
        GOTHIC = 'GOTHIC'
        CATENARY = 'CATENARY'
        SEMIELLIPTICAL = 'SEMIELLIPTICAL'
        BASKETHANDLE = 'BASKETHANDLE'
        SEMICIRCULAR = 'SEMICIRCULAR'

    def __init__(self, Link):
        self.Link = str(Link)

    @classmethod
    def from_line(cls, Link, Shape, *line):
        """

        Link Shape Geom1 Geom2 Geom3 Geom4 Barrels Culvert

        Args:
            line ():

        Returns:

        """
        if Shape == cls.Shapes.IRREGULAR:
            return CrossSectionIrregular(Link, *line)
        elif Shape == cls.Shapes.CUSTOM:
            return CrossSectionCustom(Link, *line)
        else:
            return CrossSectionShape(Link, Shape, *line)


class CrossSectionShape(CrossSection):
    def __init__(self, Link, Shape, Geom1, Geom2=0, Geom3=0, Geom4=0, Barrels=1, Culvert=NaN):
        """
        PC-SWMM-Format:
            Link Shape Geom1 Geom2 Geom3 Geom4 (Barrels Culvert)

        Args:
            Link ():
            Shape ():
            Geom1 ():
            Geom2 ():
            Geom3 ():
            Geom4 ():
            Barrels ():
            Culvert ():
        """
        self.Shape = Shape
        self.Geom1 = Geom1
        self.Curve = NaN
        self.Tsect = NaN
        self.Geom2 = Geom2
        self.Geom3 = Geom3
        self.Geom4 = Geom4
        self.Culvert = Culvert
        self.Barrels = Barrels
        CrossSection.__init__(self, Link)


class CrossSectionIrregular(CrossSection):
    def __init__(self, Link, Tsect, Geom2=0, Geom3=0, Geom4=0, Barrels=1):
        """
        Link IRREGULAR Tsect

        Args:
            Link ():
            Tsect ():
        """
        self.Shape = CrossSection.Shapes.IRREGULAR
        self.Geom1 = NaN
        self.Curve = NaN
        self.Tsect = str(Tsect)
        self.Geom2 = Geom2  # TODO not documentation conform
        self.Geom3 = Geom3  # TODO not documentation conform
        self.Geom4 = Geom4  # TODO not documentation conform
        self.Barrels = Barrels
        CrossSection.__init__(self, Link)


class CrossSectionCustom(CrossSection):
    def __init__(self, Link, Geom1, Curve, Geom3=0, Geom4=0, Barrels=1):
        """
        Link CUSTOM Geom1 Curve (Barrels)

        Args:
            Link ():
            Geom1 ():
            Curve ():
            Geom3 ():
            Geom4 ():
            Barrels ():
        """
        self.Shape = CrossSection.Shapes.CUSTOM
        self.Geom1 = Geom1
        self.Curve = str(Curve)
        self.Tsect = NaN
        self.Geom2 = NaN
        self.Geom3 = Geom3  # TODO not documentation conform
        self.Geom4 = Geom4  # TODO not documentation conform
        self.Barrels = Barrels
        CrossSection.__init__(self, Link)


class Loss(BaseSectionObject):
    identifier =IDENTIFIERS.Link

    def __init__(self, Link, Inlet=0, Outlet=0, Average=0, FlapGate=False, SeepageRate=0):
        """
        Section:
            [LOSSES]

        Purpose:
            Specifies minor head loss coefficients, flap gates, and seepage rates for conduits.

        Formats:
            Conduit Kentry Kexit Kavg (Flap Seepage)

        PC-SWMM-Format:
            Link Inlet Outlet Average FlapGate SeepageRate

        Remarks:
            - Conduit:
                name of conduit.
            - Kentry:
                entrance minor head loss coefficient.
            - Kexit:
                exit minor head loss coefficient.
            - Kavg:
                average minor head loss coefficient across length of conduit.
            - Flap:
                YES if conduit has a flap valve that prevents back flow, NO otherwise. (Default is NO).
            - Seepage:
                Rate of seepage loss into surrounding soil (in/hr or mm/hr). (Default is 0.)

            Minor losses are only computed for the Dynamic Wave flow routing option (see
            [OPTIONS] section). They are computed as Kv 2 /2g where K = minor loss coefficient, v
            = velocity, and g = acceleration of gravity. Entrance losses are based on the velocity
            at the entrance of the conduit, exit losses on the exit velocity, and average losses on
            the average velocity.

            Only enter data for conduits that actually have minor losses, flap valves, or seepage
            losses.

        Args:
            Link (str): name of conduit
            Inlet (float): entrance minor head loss coefficient.
            Outlet (float): exit minor head loss coefficient.
            Average (float): average minor head loss coefficient across length of conduit.
            FlapGate (bool): YES if conduit has a flap valve that prevents back flow, NO otherwise. (Default is NO).
            SeepageRate (float): Rate of seepage loss into surrounding soil (in/hr or mm/hr). (Default is 0.)
        """
        self.Link = str(Link)
        self.Inlet = Inlet
        self.Outlet = Outlet
        self.Average = Average
        self.FlapGate = FlapGate
        self.SeepageRate = SeepageRate


class Vertices(BaseSectionObject):
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

        Include a separate line for each interior vertex of the link, ordered from the inlet node to the outlet
        node.

        Straight-line links have no interior vertices and therefore are not listed in this section.
    """
    identifier =IDENTIFIERS.Link
    table_inp_export = False

    def __init__(self, Link,  vertices):
        self.Link = str(Link)
        self.vertices = vertices

    @classmethod
    def convert_lines(cls, lines):
        """multiple lines for one entry"""
        vertices = list()
        last = None

        for line in lines:
            Link, x, y = line
            x = float(x)
            y = float(y)
            if Link == last:
                vertices.append([x, y])
            else:
                if last is not None:
                    yield cls(last, vertices)
                last = Link
                vertices = [[x, y]]
        # last
        if last is not None:
            yield cls(last, vertices)

    def inp_line(self):
        return '\n'.join(['{}  {} {}'.format(self.Link, x, y) for x, y in self.vertices])

    @property
    def frame(self):
        return DataFrame.from_records(self.vertices, columns=['x', 'y'])
