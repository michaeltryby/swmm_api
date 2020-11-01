from numpy import NaN
from pandas import DataFrame

from .identifiers import IDENTIFIERS
from ..inp_helpers import BaseSectionObject


class CrossSection(BaseSectionObject):
    """
    Section: [**XSECTIONS**]

    Purpose:
        Provides cross-section geometric data for conduit and regulator links of the drainage system.

    Formats:
        ::

            Link Shape      Geom1 Geom2 Geom3 Geom4 (Barrels Culvert)
            Link CUSTOM     Geom1 Curve (Barrels)
            Link IRREGULAR  Tsect

    Format-PCSWMM:
        ``Link Shape Geom1 Geom2 Geom3 Geom4 (Barrels Culvert)``

    Remarks:
        The Culvert code number is used only for conduits that act as culverts
        and should be analyzed for inlet control conditions using the FHWA HDS-5 method.

        The ``CUSTOM`` shape is a closed conduit whose width versus height is described by a user-supplied Shape Curve.

        An ``IRREGULAR`` cross-section is used to model an open channel whose geometry is described by a Transect object.

    Attributes:
        Link (str): name of the conduit, orifice, or weir.
        Shape (str): cross-section shape (see Tables D-1 below or 3-1 for available shapes).
        Geom1 (float): full height of the cross-section (ft or m).
        Geom2-4: auxiliary parameters (width, side slopes, etc.) as listed in Table D-1.
        Barrels (int): number of barrels (i.e., number of parallel pipes of equal size, slope, and roughness) associated with a conduit (default is 1).
        Culvert (int): code number from Table A.10 for the conduit’s inlet geometry if it is a culvert subject to possible inlet flow control (leave blank otherwise).
        Curve (str): name of a Shape Curve in the [``CURVES``] section that defines how width varies with depth.
        Tsect (str): name of an entry in the [``TRANSECTS``] section that describes the crosssection geometry of an irregular channel.
    """
    identifier =IDENTIFIERS.Link

    class SHAPES:
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
        self.Shape = None
        self.Geom1 = NaN
        self.Curve = NaN
        self.Tsect = NaN
        self.Geom2 = NaN  # 0
        self.Geom3 = NaN  # 0
        self.Geom4 = NaN  # 0
        self.Barrels = NaN  # 1
        self.Culvert = NaN

    @classmethod
    def from_inp_line(cls, Link, Shape, *line):
        if Shape == cls.SHAPES.IRREGULAR:
            return CrossSectionIrregular(Link, *line)
        elif Shape == cls.SHAPES.CUSTOM:
            return CrossSectionCustom(Link, *line)
        else:
            return CrossSectionShape(Link, Shape, *line)


class CrossSectionShape(CrossSection):
    def __init__(self, Link, Shape, Geom1, Geom2=0, Geom3=0, Geom4=0, Barrels=1, Culvert=NaN):
        CrossSection.__init__(self, Link)
        self.Shape = str(Shape)
        self.Geom1 = float(Geom1)
        self.Geom2 = float(Geom2)
        self.Geom3 = float(Geom3)
        self.Geom4 = float(Geom4)
        self.Barrels = int(Barrels)
        self.Culvert = Culvert


class CrossSectionIrregular(CrossSection):
    """An ``IRREGULAR`` cross-section is used to model an open channel whose geometry is described by a Transect object."""
    def __init__(self, Link, Tsect, *args):
        CrossSection.__init__(self, Link)
        self.Shape = CrossSection.SHAPES.IRREGULAR
        self.Tsect = str(Tsect)


class CrossSectionCustom(CrossSection):
    """The ``CUSTOM`` shape is a closed conduit whose width versus height is described by a user-supplied Shape Curve."""
    def __init__(self, Link, Geom1, Curve, Geom3=0, Geom4=0, Barrels=1):
        CrossSection.__init__(self, Link)
        self.Shape = CrossSection.SHAPES.CUSTOM
        self.Geom1 = float(Geom1)
        self.Curve = str(Curve)
        if Barrels != 1:
            self.Geom3 = float(Geom3)
            self.Geom4 = float(Geom4)
            self.Barrels = int(Barrels)


class Loss(BaseSectionObject):
    """
    Section: [**LOSSES**]

    Purpose:
        Specifies minor head loss coefficients, flap gates, and seepage rates for conduits.

    Formats:
        ::

            Conduit Kentry Kexit Kavg (Flap Seepage)

    Format-PCSWMM:
        ``Link Inlet Outlet Average FlapGate SeepageRate``

    Remarks:
        Minor losses are only computed for the Dynamic Wave flow routing option (see
        [OPTIONS] section). They are computed as Kv 2 /2g where K = minor loss coefficient, v
        = velocity, and g = acceleration of gravity. Entrance losses are based on the velocity
        at the entrance of the conduit, exit losses on the exit velocity, and average losses on
        the average velocity.

        Only enter data for conduits that actually have minor losses, flap valves, or seepage
        losses.

    Args:
        Link (str): name of conduit ``Conduit``
        Inlet (float): entrance minor head loss coefficient. ``Kentry``
        Outlet (float): exit minor head loss coefficient. ``Kexit``
        Average (float): average minor head loss coefficient across length of conduit. ``Kavg``
        FlapGate (bool): YES if conduit has a flap valve that prevents back flow, NO otherwise. (Default is NO). ``Flap``
        SeepageRate (float): Rate of seepage loss into surrounding soil (in/hr or mm/hr). (Default is 0.) ``Seepage``

    Attributes:
        Link (str): name of conduit ``Conduit``
        Inlet (float): entrance minor head loss coefficient. ``Kentry``
        Outlet (float): exit minor head loss coefficient. ``Kexit``
        Average (float): average minor head loss coefficient across length of conduit. ``Kavg``
        FlapGate (bool): YES if conduit has a flap valve that prevents back flow, NO otherwise. (Default is NO). ``Flap``
        SeepageRate (float): Rate of seepage loss into surrounding soil (in/hr or mm/hr). (Default is 0.) ``Seepage``
    """
    identifier =IDENTIFIERS.Link

    def __init__(self, Link, Inlet=0, Outlet=0, Average=0, FlapGate=False, SeepageRate=0):
        self.Link = str(Link)
        self.Inlet = float(Inlet)
        self.Outlet = float(Outlet)
        self.Average = float(Average)
        self.FlapGate = bool(FlapGate)
        self.SeepageRate = float(SeepageRate)


class Vertices(BaseSectionObject):
    """
    Section: [**VERTICES**]

    Purpose:
        Assigns X,Y coordinates to interior vertex points of curved drainage system links.

    Format:
        ::

            Link Xcoord Ycoord

    Remarks:
        Straight-line links have no interior vertices and therefore are not listed in this section.

        Include a separate line for each interior vertex of the link, ordered from the inlet node to the outlet
        node.

    Args:
        Link (str): name of link.
        vertices (list[list[float, float]]): vertices relative to origin in lower left of map.

            - Xcoord: horizontal coordinate
            - Ycoord: vertical coordinate

    Attributes:
        Link (str): name of link.
        vertices (list[list[float, float]]): vertices relative to origin in lower left of map.

            - Xcoord: horizontal coordinate
            - Ycoord: vertical coordinate
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

    def to_inp_line(self):
        return '\n'.join(['{}  {} {}'.format(self.Link, x, y) for x, y in self.vertices])

    @property
    def frame(self):
        """convert Vertices object to a data-frame

        for debugging purposes

        Returns:
            pandas.DataFrame: section as table
        """
        return DataFrame.from_records(self.vertices, columns=['x', 'y'])
