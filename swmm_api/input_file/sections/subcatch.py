from numpy import NaN
from pandas import DataFrame

from .._type_converter import GIS_FLOAT_FORMAT
from ..helpers import BaseSectionObject, SWMM_VERSION
from ._identifiers import IDENTIFIERS
from ..section_labels import SUBCATCHMENTS, SUBAREAS, INFILTRATION, POLYGONS, LOADINGS, COVERAGES, GWF, GROUNDWATER


class SubCatchment(BaseSectionObject):
    """
    Section: [**SUBCATCHMENTS**]

    Purpose:
        Identifies each sub-catchment within the study area. Subcatchments are land area
        units which generate runoff from rainfall.

    Format:
        ::

            Name Rgage OutID Area %Imperv Width Slope Clength (Spack)

    Format-PCSWMM:
        ``Name RainGage Outlet Area %Imperv Width %Slope CurbLen SnowPack``

    Args:
        Name (str): name assigned to subcatchment.
        RainGage (str): name of rain gage in [RAINGAGES] section assigned to subcatchment. ``Rgage``
        Outlet (str): name of node or subcatchment that receives runoff from subcatchment. ``OutID``
        Area (float): area of subcatchment (acres or hectares).
        Imperv (float): percent imperviousness of subcatchment. ``%Imperv``
        Width (float): characteristic width of subcatchment (ft or meters).
        Slope (float): subcatchment slope (percent).
        CurbLen (float): total curb length (any length units). Use 0 if not applicable. ``Clength``
        SnowPack (str): optional name of snow pack object (from [SNOWPACKS] section) that characterizes snow
        accumulation and melting over the subcatchment. ``Spack``

    Attributes:
        Name (str): name assigned to subcatchment.
        RainGage (str): name of rain gage in [RAINGAGES] section assigned to subcatchment. ``Rgage``
        Outlet (str): name of node or subcatchment that receives runoff from subcatchment. ``OutID``
        Area (float): area of subcatchment (acres or hectares).
        Imperv (float): percent imperviousness of subcatchment. ``%Imperv``
        Width (float): characteristic width of subcatchment (ft or meters).
        Slope (float): subcatchment slope (percent).
        CurbLen (float): total curb length (any length units). Use 0 if not applicable. ``Clength``
        SnowPack (str): optional name of snow pack object (from [SNOWPACKS] section) that characterizes snow
        accumulation and melting over the subcatchment. ``Spack``
    """
    _identifier = IDENTIFIERS.Name
    _section_label = SUBCATCHMENTS

    def __init__(self, Name, RainGage, Outlet, Area, Imperv, Width, Slope, CurbLen=0, SnowPack=NaN):
        self.Name = str(Name)
        self.RainGage = str(RainGage)
        self.Outlet = str(Outlet)
        self.Area = float(Area)
        self.Imperv = float(Imperv)
        self.Width = float(Width)
        self.Slope = float(Slope)
        self.CurbLen = float(CurbLen)
        self.SnowPack = SnowPack


class SubArea(BaseSectionObject):
    """
    Section: [**SUBAREAS**]

    Purpose:
        Supplies information about pervious and impervious areas for each subcatchment.
        Each subcatchment can consist of a pervious sub-area, an impervious sub-area with
        depression storage, and an impervious sub-area without depression storage.

    Format:
        ::

            Subcat Nimp Nperv Simp Sperv %Zero RouteTo (%Routed)

    Format-PCSWMM:
        ``Subcatchment N-Imperv N-Perv S-Imperv S-Perv PctZero RouteTo PctRouted``

    Args:
        Subcatch (str): subcatchment name. ``Subcat``
        N_Imperv (float): Manning's n for overland flow over the impervious sub-area. ``Nimp``
        N_Perv (float): Manning's n for overland flow over the pervious sub-area. ``Nperv``
        S_Imperv (float): depression storage for impervious sub-area (inches or mm). ``Simp``
        S_Perv (float): depression storage for pervious sub-area (inches or mm). ``Sperv``
        PctZero (float): percent of impervious area with no depression storage. ``%Zero``
        RouteTo (str):

            - ``IMPERVIOUS`` if pervious area runoff runs onto impervious area,
            - ``PERVIOUS`` if impervious runoff runs onto pervious area,
            - ``OUTLET`` if both areas drain to the subcatchment's outlet (default = ``OUTLET``).

        PctRouted (float): percent of runoff routed from one type of area to another (default = 100). ``%Routed``

    Attributes:
        Subcatch (str): subcatchment name. ``Subcat``
        N_Imperv (float): Manning's n for overland flow over the impervious sub-area. ``Nimp``
        N_Perv (float): Manning's n for overland flow over the pervious sub-area. ``Nperv``
        S_Imperv (float): depression storage for impervious sub-area (inches or mm). ``Simp``
        S_Perv (float): depression storage for pervious sub-area (inches or mm). ``Sperv``
        PctZero (float): percent of impervious area with no depression storage. ``%Zero``
        RouteTo (str):

            - ``IMPERVIOUS`` if pervious area runoff runs onto impervious area,
            - ``PERVIOUS`` if impervious runoff runs onto pervious area,
            - ``OUTLET`` if both areas drain to the subcatchment's outlet (default = ``OUTLET``).

        PctRouted (float): percent of runoff routed from one type of area to another (default = 100). ``%Routed``
    """
    _identifier = IDENTIFIERS.Subcatch
    _section_label = SUBAREAS

    class RoutToOption:
        __class__ = 'RoutTo Option'
        IMPERVIOUS = 'IMPERVIOUS'
        PERVIOUS = 'PERVIOUS'
        OUTLET = 'OUTLET'

    def __init__(self, Subcatch, N_Imperv, N_Perv, S_Imperv, S_Perv, PctZero, RouteTo=RoutToOption.OUTLET,
                 PctRouted=100):
        self.Subcatch = str(Subcatch)
        self.N_Imperv = float(N_Imperv)
        self.N_Perv = float(N_Perv)
        self.S_Imperv = float(S_Imperv)
        self.S_Perv = float(S_Perv)
        self.PctZero = float(PctZero)
        self.RouteTo = str(RouteTo)
        self.PctRouted = float(PctRouted)


class Infiltration(BaseSectionObject):
    """
    Section: [**INFILTRATION**]

    Purpose:
        Supplies infiltration parameters for each subcatchment.
        Rainfall lost to infiltration only occurs over the pervious sub-area of a subcatchment.

    Formats:
        ::

            Subcat MaxRate MinRate Decay DryTime MaxInf
            Subcat Psi Ksat IMD
            Subcat CurveNo Ksat DryTime

    Remarks:
        Subcat
            subcatchment name.

        For Horton and Modified Horton Infiltration:
            MaxRate
                maximum infiltration rate on Horton curve (in/hr or mm/hr).
            MinRate
                minimum infiltration rate on Horton curve (in/hr or mm/hr).
            Decay
                decay rate constant of Horton curve (1/hr).
            DryTime
                time it takes for fully saturated soil to dry (days).
            MaxInf
                maximum infiltration volume possible (0 if not applicable) (in or mm).

        For Green-Ampt and Modified Green-Ampt Infiltration:
            Psi
                soil capillary suction (in or mm).
            Ksat
                soil saturated hydraulic conductivity (in/hr or mm/hr).
            IMD
             initial soil moisture deficit (volume of voids / total volume).

        For Curve-Number Infiltration:
            CurveNo
                SCS Curve Number.
            Ksat
                soil saturated hydraulic conductivity (in/hr or mm/hr)
                (This property has been deprecated and is no longer used.)
            DryTime
                time it takes for fully saturated soil to dry (days).

    Args:
        Subcatch (str): subcatchment name. ``Subcat``

    Attributes:
        Subcatch (str): subcatchment name. ``Subcat``
    """
    _identifier = IDENTIFIERS.Subcatch
    _section_label = INFILTRATION

    # _table_inp_export = False

    # jetbrains://clion/navigate/reference?project=Swmm5&path=src/infil.c : 133
    # infil_readParams

    def __init__(self, Subcatch):
        self.Subcatch = str(Subcatch)

    @classmethod
    def from_inp_line(cls, Subcatch, *args, **kwargs):

        subcls = cls

        # n_args = len(args) + len(kwargs.keys()) + 1
        # if n_args == 6:  # hortn
        #     subcls = InfiltrationHorton
        # elif n_args == 4:
        #     subcls = cls

        # _____________________________________
        sub_class_id = None
        if SWMM_VERSION == '5.1.015':
            # NEU in swmm 5.1.015
            last_arg = args[-1]
            if last_arg in INFILTRATION_DICT:
                sub_class_id = last_arg
                subcls = INFILTRATION_DICT[last_arg]
                args = args[:-1]

        if subcls != InfiltrationHorton:
            args = args[:3]

        # _____________________________________
        o = subcls(Subcatch, *args, **kwargs)
        # _____________________________________
        if sub_class_id is not None:
            o.kind = sub_class_id
        return o


class InfiltrationHorton(Infiltration):
    """
    Section: [**INFILTRATION**]

    For Horton and Modified Horton Infiltration

    Purpose:
        Supplies infiltration parameters for each subcatchment.
        Rainfall lost to infiltration only occurs over the pervious sub-area of a subcatchment.

    Formats:
        ::

            Subcat MaxRate MinRate Decay DryTime MaxInf

    Format-PCSWMM:
        ``Subcatchment MaxRate MinRate Decay DryTime MaxInfil``

    Args:
        Subcatch (str): subcatchment name. ``Subcat``
        MaxRate (float): maximum infiltration rate on Horton curve (in/hr or mm/hr).
        MinRate (float): minimum infiltration rate on Horton curve (in/hr or mm/hr).
        Decay (float): decay rate constant of Horton curve (1/hr).
        DryTime (float): time it takes for fully saturated soil to dry (days).
        MaxInf (float): maximum infiltration volume possible (0 if not applicable) (in or mm).

    Attributes:
        Subcatch (str): subcatchment name. ``Subcat``
        MaxRate (float): maximum infiltration rate on Horton curve (in/hr or mm/hr).
        MinRate (float): minimum infiltration rate on Horton curve (in/hr or mm/hr).
        Decay (float): decay rate constant of Horton curve (1/hr).
        DryTime (float): time it takes for fully saturated soil to dry (days).
        MaxInf (float): maximum infiltration volume possible (0 if not applicable) (in or mm).
    """

    def __init__(self, Subcatch, MaxRate, MinRate, Decay, DryTime, MaxInf, kind=None):
        Infiltration.__init__(self, Subcatch)
        self.MaxRate = float(MaxRate)
        self.MinRate = float(MinRate)
        self.Decay = float(Decay)
        self.DryTime = float(DryTime)
        self.MaxInf = float(MaxInf)
        self.kind = NaN


class InfiltrationGreenAmpt(Infiltration):
    """
    Section: [**INFILTRATION**]

    For Green-Ampt and Modified Green-Ampt Infiltration

    Purpose:
        Supplies infiltration parameters for each subcatchment.
        Rainfall lost to infiltration only occurs over the pervious sub-area of a subcatchment.

    Formats:
        ::

            Subcat Psi Ksat IMD

    Args:
        Subcatch (str): subcatchment name. ``Subcat``
        Psi (float): soil capillary suction (in or mm).
        Ksat (float): soil saturated hydraulic conductivity (in/hr or mm/hr).
        IMD (float): initial soil moisture deficit (volume of voids / total volume).

    Attributes:
        Subcatch (str): subcatchment name. ``Subcat``
        Psi (float): soil capillary suction (in or mm).
        Ksat (float): soil saturated hydraulic conductivity (in/hr or mm/hr).
        IMD (float): initial soil moisture deficit (volume of voids / total volume).
    """

    def __init__(self, Subcatch, Psi, Ksat, IMD, kind=None):
        Infiltration.__init__(self, Subcatch)
        self.Psi = float(Psi)
        self.Ksat = float(Ksat)
        self.IMD = float(IMD)
        self.kind = NaN


class InfiltrationCurveNumber(Infiltration):
    """
    Section: [**INFILTRATION**]

    For Curve-Number Infiltration:

    Purpose:
        Supplies infiltration parameters for each subcatchment.
        Rainfall lost to infiltration only occurs over the pervious sub-area of a subcatchment.

    Formats:
        ::

            Subcat CurveNo Ksat DryTime

    Args:
        Subcatch (str): subcatchment name. ``Subcat``
        CurveNo: SCS Curve Number.
        Ksat (float): soil saturated hydraulic conductivity (in/hr or mm/hr)
            (This property has been deprecated and is no longer used.)
        DryTime (float): time it takes for fully saturated soil to dry (days).

    Attributes:
        Subcatch (str): subcatchment name. ``Subcat``
        CurveNo: SCS Curve Number.
        Ksat (float): soil saturated hydraulic conductivity (in/hr or mm/hr)
            (This property has been deprecated and is no longer used.)
        DryTime (float): time it takes for fully saturated soil to dry (days).
    """

    def __init__(self, Subcatch, CurveNo, Ksat, DryTime, kind=None):
        Infiltration.__init__(self, Subcatch)
        self.CurveNo = CurveNo
        self.Ksat = float(Ksat)
        self.DryTime = float(DryTime)
        self.kind = NaN


INFILTRATION_DICT = {
    'HORTON'             : InfiltrationHorton,
    'MODIFIED_HORTON'    : InfiltrationHorton,
    'GREEN_AMPT'         : InfiltrationGreenAmpt,
    'MODIFIED_GREEN_AMPT': InfiltrationGreenAmpt,
    'CURVE_NUMBER'       : InfiltrationCurveNumber
}


class Polygon(BaseSectionObject):
    """
    Section: [**POLYGONS**]

    Purpose:
        Assigns X,Y coordinates to vertex points of polygons that define a subcatchment boundary.

    Format:
        ::

            Link Xcoord Ycoord

    Remarks:
        Include a separate line for each vertex of the subcatchment polygon, ordered in a
        consistent clockwise or counter-clockwise sequence.

    Args:
        Subcatch (str): name of subcatchment. ``Subcat``
        polygon (list[list[float,float]]): coordinate of the polygon relative to origin in lower left of map.
            - Xcoord: horizontal coordinate of vertex
            - Ycoord: vertical coordinate of vertex

    Attributes:
        Subcatch (str): name of subcatchment. ``Subcat``
        polygon (list[list[float,float]]): coordinate of the polygon relative to origin in lower left of map.
            - Xcoord: horizontal coordinate of vertex
            - Ycoord: vertical coordinate of vertex
    """
    _identifier = IDENTIFIERS.Subcatch
    _table_inp_export = False
    _section_label = POLYGONS

    def __init__(self, Subcatch, polygon):
        self.Subcatch = str(Subcatch)
        self.polygon = polygon

    @classmethod
    def _convert_lines(cls, multi_line_args):
        polygon = list()
        last = None

        for line in multi_line_args:
            Subcatch, x, y = line
            x = float(x)
            y = float(y)
            if Subcatch == last:
                polygon.append([x, y])
            else:
                if last is not None:
                    yield cls(last, polygon)
                last = Subcatch
                polygon = [[x, y]]
        # last
        if last is not None:
            yield cls(last, polygon)

    @property
    def frame(self):
        return DataFrame.from_records(self.polygon, columns=['x', 'y'])

    def to_inp_line(self):
        return '\n'.join([f'{self.Subcatch}  {x:{GIS_FLOAT_FORMAT}} {y:{GIS_FLOAT_FORMAT}}' for x, y in self.polygon])


class Loading(BaseSectionObject):
    """
    Section: [**LOADINGS**]

    Purpose:
        Specifies the pollutant buildup that exists on each subcatchment at the start of a simulation.

    Format:
        ::

            Subcat Pollut InitBuildup Pollut InitBuildup ...

    Format-PCSWMM:
        ``Subcatchment Pollutant Buildup``

    Remarks:
        More than one pair of pollutant - buildup values can be entered per line. If more than
        one line is needed, then the subcatchment name must still be entered first on the
        succeeding lines.

        If an initial buildup is not specified for a pollutant, then its initial buildup is computed
        by applying the DRY_DAYS option (specified in the [OPTIONS] section) to the
        pollutant’s buildup function for each land use in the subcatchment.

    Args:
        Subcatch (str): name of a subcatchment.
        pollutant_buildup (list[list[str, float]]): tuple of

            - Pollut: name of a pollutant.
            - InitBuildup: initial buildup of pollutant (lbs/acre or kg/hectare).

    Attributes:
        Subcatch (str): name of a subcatchment.
        pollutant_buildup (list[list[str, float]]): tuple of

            - Pollut: name of a pollutant.
            - InitBuildup: initial buildup of pollutant (lbs/acre or kg/hectare).

    """
    _identifier = IDENTIFIERS.Subcatch
    _table_inp_export = False
    _section_label = LOADINGS

    def __init__(self, Subcatch, pollutant_buildup_dict=None):
        self.Subcatch = str(Subcatch)
        self.pollutant_buildup_dict = dict()
        if pollutant_buildup_dict:
            self.pollutant_buildup_dict = pollutant_buildup_dict

    def _add_buildup(self, pollutant, buildup):
        self.pollutant_buildup_dict[pollutant] = float(buildup)

    @classmethod
    def _convert_lines(cls, multi_line_args):
        last = None
        for Subcatch, *line in multi_line_args:

            if last is None:
                # first line of section
                last = cls(Subcatch)

            elif last.Subcatch != Subcatch:
                # new Coverage
                yield last
                last = cls(Subcatch)

            # Coverage definitions
            remains = iter(line)
            for pollutant in remains:
                buildup = next(remains)
                last._add_buildup(pollutant, buildup)

        # last
        if last is not None:
            yield last

    @property
    def frame(self):
        return DataFrame.from_dict(self.pollutant_buildup_dict, columns=['pollutant', 'initial buildup'])

    def to_inp_line(self):
        return '\n'.join(['{}  {} {}'.format(self.Subcatch, p, b) for p, b in self.pollutant_buildup_dict.items()])


class Coverage(BaseSectionObject):
    """
    Section: [**COVERAGES**]

    Purpose:
        Specifies the percentage of a subcatchment’s area that is covered by each category of land use.

    Format:
        ::

            Subcat Landuse Percent Landuse Percent . . .

    Args:
        Subcatch (str):
            subcatchment name.

        land_use_dict (dict):
            key: Landuse (str): land use name.
            value: Percent (float): percent of subcatchment area.

    Remarks:
        More than one pair of land use - percentage values can be entered per line. If more
        than one line is needed, then the subcatchment name must still be entered first on
        the succeeding lines.

        If a land use does not pertain to a subcatchment, then it does not have to be entered.

        If no land uses are associated with a subcatchment then no contaminants will appear
        in the runoff from the subcatchment.
    """
    _identifier = IDENTIFIERS.Subcatch
    _section_label = COVERAGES

    def __init__(self, Subcatch, land_use_dict=None):
        self.Subcatch = str(Subcatch)
        self.land_use_dict = dict()
        if land_use_dict:
            self.land_use_dict = land_use_dict

    def _add_land_use(self, land_use, percent):
        self.land_use_dict[land_use] = float(percent)

    @classmethod
    def _convert_lines(cls, multi_line_args):
        last = None
        for Subcatch, *line in multi_line_args:

            if last is None:
                # first line of section
                last = cls(Subcatch)

            elif last.Subcatch != Subcatch:
                # new Coverage
                yield last
                last = cls(Subcatch)

            # Coverage definitions
            remains = iter(line)
            for land_use in remains:
                percent = next(remains)
                last._add_land_use(land_use, percent)

        # last
        if last is not None:
            yield last

    @property
    def frame(self):
        return DataFrame.from_dict(self.land_use_dict, columns=['land_use', 'percent'])

    def to_inp_line(self):
        return '\n'.join(['{}  {} {}'.format(self.Subcatch, p, b) for p, b in self.land_use_dict.items()])


class GroundwaterFlow(BaseSectionObject):
    """
    Section: [**GWF**]

    Purpose:
        Defines custom groundwater flow equations for specific subcatchments.

    Format:
        ::

            Subcat LATERAL/DEEP Expr

    Args:
        Subcatch (str): subcatchment name.
        expression (str): math formula expressing the rate of groundwater flow (in cfs per acre or cms per hectare for lateral flow or in/hr or mm/hr for deep flow) as a function of the following variables:

            - ``Hgw`` (for height of the groundwater table)
            - ``Hsw`` (for height of the surface water)
            - ``Hcb`` (for height of the channel bottom)
            - ``Hgs`` (for height of ground surface) where all heights are relative to the aquifer bottom and have units of either feet or meters;
            - ``Ks`` (for saturated hydraulic conductivity in in/hr or mm/hr)
            - ``K`` (for unsaturated hydraulic conductivity in in/hr or mm/hr)
            - ``Theta`` (for moisture content of unsaturated zone)
            - ``Phi`` (for aquifer soil porosity)
            - ``Fi`` (for infiltration rate from the ground surface in in/hr or mm/hr)
            - ``Fu`` (for percolation rate from the upper unsaturated zone in in/hr or mm/hr)
            - ``A`` (for subcatchment area in acres or hectares)

    Remarks:
        Use ``LATERAL`` to designate an expression for lateral groundwater flow (to a node of
        the conveyance network) and ``DEEP`` for vertical loss to deep groundwater.

        See the [``TREATMENT``] section for a list of built-in math functions that can be used in
        ``Expr``. In particular, the ``STEP(x)`` function is 1 when ``x > 0`` and is 0 otherwise.

    Examples:
        ::

            ;Two-stage linear reservoir for lateral flow
            Subcatch1 LATERAL 0.001*Hgw + 0.05*(Hgw–5)*STEP(Hgw–5)

            ;Constant seepage rate to deep aquifer
            Subactch1 DEEP 0.002
    """
    _identifier = (IDENTIFIERS.Subcatch, 'kind')
    _section_label = GWF

    class TYPES:
        LATERAL = 'LATERAL'
        DEEP = 'DEEP'

    def __init__(self, Subcatch, kind, expression, *expression_):
        self.Subcatch = str(Subcatch)
        self.kind = kind
        self.expression = expression + ' '.join(expression_)


class Groundwater(BaseSectionObject):
    """
    Section: [**GROUNDWATER**]

    Purpose:
        Supplies parameters that determine the rate of groundwater flow between the aquifer
        underneath a subcatchment and a node of the conveyance system.

    Format:
        ::

            Subcat Aquifer Node Esurf A1 B1 A2 B2 A3 Dsw (Egwt Ebot Egw Umc)

    Attributes:
        Subcat (float): subcatchment name.
        Aquifer (float): name of groundwater aquifer underneath the subcatchment.
        Node (float): name of node in conveyance system exchanging groundwater with aquifer.
        Esurf (float): surface elevation of subcatchment (ft or m).
        A1 (float): groundwater flow coefficient (see below).
        B1 (float): groundwater flow exponent (see below).
        A2 (float): surface water flow coefficient (see below).
        B2 (float): surface water flow exponent (see below).
        A3 (float): surface water – groundwater interaction coefficient (see below).
        Dsw (float): fixed depth of surface water at receiving node (ft or m)
                    (set to zero if surface water depth will vary as computed by flow routing).
        Egwt (float): threshold groundwater table elevation which must be reached before any flow occurs (ft or m).
                    Leave blank (or enter \\*) to use the elevation of the receiving node's invert.
        Ebot (float): elevation of the bottom of the aquifer (ft or m).
        Egw (float): groundwater table elevation at the start of the simulation (ft or m).
        Umc (float): unsaturated zone moisture content at start of simulation (volumetric fraction).


    Remarks:
        The optional parameters (Ebot, Egw, Umc) can be used to override the values supplied for the subcatchment’s aquifer.

        The flow coefficients are used in the following equation that determines the lateral groundwater
        flow rate based on groundwater and surface water elevations:

        .. math::

            Q_L = A1 * (H_{gw} – H_{cb} ) ^ {B1} – A2 * (H_{sw} – H_{cb} ) ^ {B2} + A3 * H_{gw} * H_{sw}

        where:
            - Q_L = lateral groundwater flow (cfs per acre or cms per hectare),
            - H_gw = height of saturated zone above bottom of aquifer (ft or m),
            - H_sw = height of surface water at receiving node above aquifer bottom (ft or m),
            - H_cb = height of channel bottom above aquifer bottom (ft or m).
    """
    _identifier = (IDENTIFIERS.Subcatch, 'Aquifer', IDENTIFIERS.Node)
    _section_label = GROUNDWATER

    def __init__(self, Subcatch, Aquifer, Node, Esurf, A1, B1, A2, B2, A3, Dsw, Egwt=NaN, Ebot=NaN, Egw=NaN, Umc=NaN):
        """
        Groundwater object.

        Args:
            Subcat (float): subcatchment name.
            Aquifer (float): name of groundwater aquifer underneath the subcatchment.
            Node (float): name of node in conveyance system exchanging groundwater with aquifer.
            Esurf (float): surface elevation of subcatchment (ft or m).
            A1 (float): groundwater flow coefficient (see below).
            B1 (float): groundwater flow exponent (see below).
            A2 (float): surface water flow coefficient (see below).
            B2 (float): surface water flow exponent (see below).
            A3 (float): surface water – groundwater interaction coefficient (see below).
            Dsw (float): fixed depth of surface water at receiving node (ft or m)
                        (set to zero if surface water depth will vary as computed by flow routing).
            Egwt (float | optional): threshold groundwater table elevation which must be reached before any flow occurs (ft or m).
                        Leave blank (or enter \\*) to use the elevation of the receiving node's invert.
            Ebot (float | optional): elevation of the bottom of the aquifer (ft or m).
            Egw (float | optional): groundwater table elevation at the start of the simulation (ft or m).
            Umc (float | optional): unsaturated zone moisture content at start of simulation (volumetric fraction).
        """
        self.Subcatch = str(Subcatch)
        self.Aquifer = str(Aquifer)
        self.Node = str(Node)
        self.Esurf = float(Esurf)
        self.A1 = float(A1)
        self.B1 = float(B1)
        self.A2 = float(A2)
        self.B2 = float(B2)
        self.A3 = float(A3)
        self.Dsw = float(Dsw)
        self.Egwt = Egwt
        self.Ebot = float(Ebot)
        self.Egw = float(Egw)
        self.Umc = float(Umc)
