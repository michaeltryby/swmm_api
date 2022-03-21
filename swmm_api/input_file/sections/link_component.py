from typing import NamedTuple

from numpy import NaN, isnan
from pandas import DataFrame

from ._identifiers import IDENTIFIERS
from ..helpers import BaseSectionObject, InpSectionGeo
from .._type_converter import to_bool, GIS_FLOAT_FORMAT
from ..section_labels import XSECTIONS, LOSSES, VERTICES


class CrossSection(BaseSectionObject):
    """
    Section: [**XSECTIONS**]

    Purpose:
        Provides cross-section geometric data for conduit and regulator links of the drainage system.

    Formats:
        ::

            Link Shape      Geom1 Geom2             Geom3 Geom4 (Barrels Culvert)
            Link CUSTOM     Geom1       Curve                   (Barrels)
            Link IRREGULAR                    Tsect

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
    _identifier =IDENTIFIERS.Link
    _section_label = XSECTIONS

    class SHAPES:
        IRREGULAR = 'IRREGULAR'  # TransectCoordinates (Natural Channel)
        CUSTOM = 'CUSTOM'  # Full Height, ShapeCurveCoordinates

        CIRCULAR = 'CIRCULAR'  # Full Height = Diameter
        FORCE_MAIN = 'FORCE_MAIN'  # Full Height = Diameter, Roughness
        FILLED_CIRCULAR = 'FILLED_CIRCULAR'  # Full Height = Diameter, Filled Depth
        RECT_CLOSED = 'RECT_CLOSED'  # Rectangular: Full Height, Top Width
        RECT_OPEN = 'RECT_OPEN'  # Rectangular: Full Height, Top Width
        TRAPEZOIDAL = 'TRAPEZOIDAL'  # Full Height, Base Width, Side Slopes
        TRIANGULAR = 'TRIANGULAR'  # Full Height, Top Width
        HORIZ_ELLIPSE = 'HORIZ_ELLIPSE'  # Full Height, Max. Width
        VERT_ELLIPSE = 'VERT_ELLIPSE'  # Full Height, Max. Width
        ARCH = 'ARCH'  # Size Code or Full Height, Max. Width
        PARABOLIC = 'PARABOLIC'  # Full Height, Top Width
        POWER = 'POWER'  # Full Height, Top Width, Exponent
        RECT_TRIANGULAR = 'RECT_TRIANGULAR'  # Full Height, Top Width, Triangle Height
        RECT_ROUND = 'RECT_ROUND'  # Full Height, Top Width, Bottom Radius
        MODBASKETHANDLE = 'MODBASKETHANDLE'  # Full Height, Bottom Width, Top Radius
        EGG = 'EGG'  # Full Height
        HORSESHOE = 'HORSESHOE'  # Full Height Gothic Full Height
        GOTHIC = 'GOTHIC'  # Full Height
        CATENARY = 'CATENARY'  # Full Height
        SEMIELLIPTICAL = 'SEMIELLIPTICAL'  # Full Height
        BASKETHANDLE = 'BASKETHANDLE'  # Full Height
        SEMICIRCULAR = 'SEMICIRCULAR'  # Full Height

    def __init__(self, Link, Shape, Geom1=0, Geom2=0, Geom3=0, Geom4=0, Barrels=1, Culvert=NaN, Tsect=None, Curve=None):
        # in SWMM C-code function "link_readXsectParams"
        self.Link = str(Link)
        self.Shape = Shape

        self.Geom1 = NaN
        self.Tsect = NaN

        self.Geom2 = NaN
        self.Curve = NaN

        if Shape == self.SHAPES.IRREGULAR:
            if Tsect is None:
                # read inp file
                Tsect = Geom1
            self.Tsect = str(Tsect)  # name of TransectCoordinates
        elif Shape == self.SHAPES.CUSTOM:
            if Curve is None:
                Curve = Geom2
            self.Curve = str(Curve)
            self.Geom1 = float(Geom1)
        else:
            self.Geom1 = float(Geom1)
            self.Geom2 = float(Geom2)

        self.Geom3 = float(Geom3)
        self.Geom4 = float(Geom4)
        self.Barrels = int(Barrels)
        # according to the c code 6 arguments are needed to not raise an error / nonsense, but you have to
        if Barrels != 1 or not isinstance(Barrels, str) and ~isnan(Barrels):
            self.Barrels = int(Barrels)
        self.Culvert = Culvert

    @classmethod
    def Irregular(cls, Link, Tsect):
        """
        ``IRREGULAR`` cross-section is used to model an open channel whose geometry is described by a Transect object.
        """
        return cls(Link, CrossSection.SHAPES.IRREGULAR, Tsect=Tsect)

    @classmethod
    def Custom(cls, Link, Geom1, Curve):
        """
        ``CUSTOM`` shape is a closed conduit whose width versus height is described by a user-supplied Shape Curve.
        """
        return cls(Link, CrossSection.SHAPES.CUSTOM, Geom1=Geom1, Curve=Curve)


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

    Formats-SWMM-GUI:
        ``Link  Kentry  Kexit  Kavg  FlapGate  Seepage``

    Remarks:
        Minor losses are only computed for the Dynamic Wave flow routing option (see
        [OPTIONS] section). They are computed as Kv 2 /2g where K = minor loss coefficient, v
        = velocity, and g = acceleration of gravity. Entrance losses are based on the velocity
        at the entrance of the conduit, exit losses on the exit velocity, and average losses on
        the average velocity.

        Only enter data for conduits that actually have minor losses, flap valves, or seepage
        losses.

    Attributes:
        Link (str): name of conduit ``Conduit``
        Inlet (float): entrance minor head loss coefficient. ``Kentry``
        Outlet (float): exit minor head loss coefficient. ``Kexit``
        Average (float): average minor head loss coefficient across length of conduit. ``Kavg``
        FlapGate (bool): YES if conduit has a flap valve that prevents back flow, NO otherwise. (Default is NO). ``Flap``
        SeepageRate (float): Rate of seepage loss into surrounding soil (in/hr or mm/hr). (Default is 0.) ``Seepage``
    """
    _identifier =IDENTIFIERS.Link
    _section_label = LOSSES

    class TYPES:
        INLET = 'Inlet'
        OUTLET = 'Outlet'
        AVERAGE = 'Average'

    def __init__(self, Link, Inlet=0, Outlet=0, Average=0, FlapGate=False, SeepageRate=0):
        """
        Loss object.

        Args:
            Link (str): name of conduit ``Conduit``
            Inlet (float): entrance minor head loss coefficient. ``Kentry``
            Outlet (float): exit minor head loss coefficient. ``Kexit``
            Average (float): average minor head loss coefficient across length of conduit. ``Kavg``
            FlapGate (bool): YES if conduit has a flap valve that prevents back flow, NO otherwise. (Default is NO). ``Flap``
            SeepageRate (float): Rate of seepage loss into surrounding soil (in/hr or mm/hr). (Default is 0.) ``Seepage``
        """
        self.Link = str(Link)
        self.Inlet = float(Inlet)
        self.Outlet = float(Outlet)
        self.Average = float(Average)
        self.FlapGate = to_bool(FlapGate)
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
    _identifier =IDENTIFIERS.Link
    _table_inp_export = False
    _section_label = VERTICES
    _section_class = InpSectionGeo

    def __init__(self, Link,  vertices):
        self.Link = str(Link)
        self.vertices = vertices

    @classmethod
    def _convert_lines(cls, multi_line_args):
        vertices = []
        last = None

        for line in multi_line_args:
            Link, x, y = line
            x = float(x)
            y = float(y)
            if Link == last:
                vertices.append((x, y))
            else:
                if last is not None:
                    yield cls(last, vertices)
                last = Link
                vertices = [(x, y)]
        # last
        if last is not None:
            yield cls(last, vertices)

    def to_inp_line(self):
        global GIS_FLOAT_FORMAT
        return '\n'.join([f'{self.Link} {x:{GIS_FLOAT_FORMAT}} {y:{GIS_FLOAT_FORMAT}}' for x, y in self.vertices])

    @property
    def frame(self):
        """convert Vertices object to a data-frame

        for debugging purposes

        Returns:
            pandas.DataFrame: section as table
        """
        return DataFrame.from_records(self.vertices, columns=['x', 'y'])

    @property
    def geo(self):
        """
        get the shapely representation for the object (LineString).

        Returns:
            shapely.geometry.LineString: LineString object for the vertices.
        """
        import shapely.geometry as sh
        return sh.LineString(self.vertices)

    @classmethod
    def create_section_from_geoseries(cls, data) :
        """
        create a VERTICES inp-file section for a geopandas.GeoSeries

        Args:
            data (geopandas.GeoSeries): geopandas.GeoSeries of coordinates

        Returns:
            InpSectionGeo: VERTICES inp-file section
        """
        # geometry mit MultiLineString deswegen v[0] mit ersten und einzigen linestring zu verwenden
        s = cls.create_section()
        # s.update({i: Vertices(i, v) for i, v in zip(data.index, map(lambda i: list(i.coords), data.values))})
        # s.add_multiple(cls(i, list(v.coords)) for i, v in data.to_dict().items())
        s.add_multiple(cls.from_shapely(i, v) for i, v in data.items())
        return s

    @classmethod
    def from_shapely(cls, Link, line):
        """
        Create a Vertices object with a shapely LineString

        Args:
            Link (str): label of the link
            line (shapely.geometry.LineString):

        Returns:
            Vertices: Vertices object
        """
        return cls(Link, list(line.coords))
