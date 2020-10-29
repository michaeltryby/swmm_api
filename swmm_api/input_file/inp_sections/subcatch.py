from numpy import NaN

from ..inp_helpers import BaseSectionObject
from .indices import Indices


class SubCatchment(BaseSectionObject):
    """
    Section:
        [SUBCATCHMENTS]

    Purpose:
        Identifies each subcatchment within the study area. Subcatchments are land area
        units which generate runoff from rainfall.

    Format:
        Name Rgage OutID Area %Imperv Width Slope Clength (Spack)

    Remarks:
        - Name:
            name assigned to subcatchment.
        - Rgage:
            name of rain gage in [RAINGAGES] section assigned to subcatchment.
        - OutID:
            name of node or subcatchment that receives runoff from subcatchment.
        - Area:
            area of subcatchment (acres or hectares).
        - %Imperv:
            percent imperviousness of subcatchment.
        - Width:
            characteristic width of subcatchment (ft or meters).
        - Slope:
            subcatchment slope (percent).
        - Clength:
            total curb length (any length units). Use 0 if not applicable.
        - Spack:
            optional name of snow pack object (from [SNOWPACKS] section) that characterizes snow accumulation and
            melting over the subcatchment.
    """
    index = Indices.Name

    def __init__(self, Name, RainGage, Outlet, Area, Imperv, Width, Slope, CurbLen, SnowPack=NaN):
        """


        Name RainGage Outlet Area %Imperv Width %Slope CurbLen SnowPack
        """

        self.Name = str(Name)
        self.RainGage = RainGage
        self.Outlet = str(Outlet)
        self.Area = Area
        self.Imperv = Imperv
        self.Width = Width
        self.Slope = Slope
        self.CurbLen = CurbLen
        self.SnowPack = SnowPack


class SubArea(BaseSectionObject):
    index = Indices.Subcatch

    class RoutToOption:
        __class__ = 'RoutTo Option'
        IMPERVIOUS = 'IMPERVIOUS'
        PERVIOUS = 'PERVIOUS'
        OUTLET = 'OUTLET'

    def __init__(self, Subcatch, N_Imperv, N_Perv, S_Imperv, S_Perv, PctZero, RouteTo=RoutToOption.OUTLET,
                 PctRouted=100):
        """
        Section:
            [SUBAREAS]

        Purpose:
            Supplies information about pervious and impervious areas for each subcatchment.
            Each subcatchment can consist of a pervious sub-area, an impervious sub-area with
            depression storage, and an impervious sub-area without depression storage.

        Format:
            Subcat Nimp Nperv Simp Sperv %Zero RouteTo (%Routed)

        Format-PCSWMM:
            Subcatchment N-Imperv N-Perv S-Imperv S-Perv PctZero RouteTo PctRouted

        Remarks:
            Subcat
                subcatchment name.
            Nimp
                Manning's n for overland flow over the impervious sub-area.
            Nperv
                Manning's n for overland flow over the pervious sub-area.
            Simp
                depression storage for impervious sub-area (inches or mm).
            Sperv
                depression storage for pervious sub-area (inches or mm).
            %Zero
                percent of impervious area with no depression storage.
            RouteTo
                IMPERVIOUS if pervious area runoff runs onto impervious area,
                PERVIOUS if impervious runoff runs onto pervious area,
                or OUTLET if both areas drain to the subcatchment's outlet (default = OUTLET).
            %Routed
                percent of runoff routed from one type of area to another (default = 100).

        Args:
            subcatchment (str):
            N_Imperv (float):
            N_Perv (float):
            S_Imperv (float):
            S_Perv (float):
            PctZero (float):
            RouteTo (str):
            PctRouted (float):
        """
        self.Subcatch = str(Subcatch)
        self.N_Imperv = N_Imperv
        self.N_Perv = N_Perv
        self.S_Imperv = S_Imperv
        self.S_Perv = S_Perv
        self.PctZero = PctZero
        self.RouteTo = RouteTo
        self.PctRouted = PctRouted


class Infiltration(BaseSectionObject):
    index = Indices.Subcatch

    def __init__(self, Subcatch):
        self.Subcatch = str(Subcatch)

    @classmethod
    def from_line(cls, Subcatch, *args, **kwargs):
        n_args = len(args) + len(kwargs.keys()) + 1
        if n_args == 6:  # hortn
            subcls = InfiltrationHorton
        elif n_args == 4:
            subcls = InfiltrationGreenAmpt
        else:
            # TODO
            subcls = InfiltrationCurveNumber

        # _____________________________________
        # NEU in swmm 5.1.015
        last_arg = args[-1]
        cls_args = {
            'HORTON': InfiltrationHorton,
            'MODIFIED_HORTON': InfiltrationHorton,
            'GREEN_AMPT': InfiltrationGreenAmpt,
            'MODIFIED_GREEN_AMPT': InfiltrationGreenAmpt,
            'CURVE_NUMBER': InfiltrationCurveNumber
        }
        if last_arg in cls_args:
            subcls = cls_args[last_arg]
            args = args[:-1]

        if subcls != InfiltrationHorton:
            args = args[:3]

        # _____________________________________
        return subcls(Subcatch, *args, **kwargs)


class InfiltrationHorton(Infiltration):

    def __init__(self, Subcatch, MaxRate, MinRate, Decay, DryTime, MaxInf):
        """
        Horton:
            Subcat  MaxRate  MinRate  Decay  DryTime  MaxInf

        PC-SWMM-Format:
            Subcatchment MaxRate MinRate Decay DryTime MaxInfil

        Args:
            line ():

        Returns:

        """
        Infiltration.__init__(self, Subcatch)
        self.MaxRate = MaxRate
        self.MinRate = MinRate
        self.Decay = Decay
        self.DryTime = DryTime
        self.MaxInf = MaxInf


class InfiltrationGreenAmpt(Infiltration):

    def __init__(self, Subcatch, Psi, Ksat, IMD):
        """
        Green-Ampt:
            Subcat  Psi  Ksat  IMD

        PC-SWMM-Format:
            Subcatchment MaxRate MinRate Decay DryTime MaxInfil

        Args:
            line ():

        Returns:

        """
        Infiltration.__init__(self, Subcatch)
        self.Psi = Psi
        self.Ksat = Ksat
        self.IMD = IMD


class InfiltrationCurveNumber(Infiltration):

    def __init__(self, Subcatch, CurveNo, Ksat, DryTime):
        """
        Curve-Number:
            Subcat  CurveNo  Ksat  DryTime

        PC-SWMM-Format:
            Subcatchment MaxRate MinRate Decay DryTime MaxInfil

        Args:
            line ():

        Returns:

        """
        Infiltration.__init__(self, Subcatch)
        self.CurveNo = CurveNo
        self.Ksat = Ksat
        self.DryTime = DryTime


class Polygon(BaseSectionObject):
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
    index = Indices.Subcatch
    table_inp_export = False

    def __init__(self, Subcatch,  vertices):
        self.Subcatch = str(Subcatch)
        self.vertices = vertices

    @classmethod
    def convert_lines(cls, lines):
        """multiple lines for one entry"""
        polygon = list()
        last = None

        for line in lines:
            Subcatch, x, y = line
            x = float(x)
            y = float(y)
            if Subcatch == last:
                polygon.append([x, y])
            else:
                if last is not None:
                    yield cls(last, polygon)
                last = Subcatch
                polygon = list([x, y])
        # last
        yield cls(last, polygon)
