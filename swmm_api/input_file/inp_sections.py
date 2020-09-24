from numpy import NaN, isnan

from .inp_helpers import BaseSectionObject


class Storage(BaseSectionObject):
    """
    Section:
        [STORAGE]

    Purpose:
        Identifies each storage node of the drainage system.
        Storage nodes can have any shape as specified by a surface area versus water depth relation.

    Format:
        Name Elev Ymax Y0 TABULAR    Acurve   (Apond Fevap Psi Ksat IMD)
        Name Elev Ymax Y0 FUNCTIONAL A1 A2 A0 (Apond Fevap Psi Ksat IMD)

    PC-SWMM-Format:
        Name Elev. MaxDepth InitDepth Shape Curve-Name/Params N/A Fevap Psi Ksat IMD

    Remarks:
        A1, A2, and A0 are used in the following expression that relates surface area (ft2 or m2) to water depth
        (ft or m) for a storage unit with FUNCTIONAL geometry:

        𝐴rea = 𝐴0 + 𝐴1 * Depth ^ A2

        For TABULAR geometry, the surface area curve will be extrapolated outwards to meet the unit's maximum depth
        if need be.

        The parameters Psi, Ksat, and IMD need only be supplied if seepage loss through the soil at the bottom and
        sloped sides of the storage unit should be considered.
        They are the same Green-Ampt infiltration parameters described in the [INFILTRATION] section.
        If Ksat is zero then no seepage occurs while if IMD is zero then seepage occurs at a constant rate equal to Ksat.
        Otherwise seepage rate will vary with storage depth.
    """
    index = 'Name'

    class Types:
        TABULAR = 'TABULAR'
        FUNCTIONAL = 'FUNCTIONAL'

    def __init__(self, Name, Elevation, MaxDepth, InitDepth, Type, *args, Curve=None,
                 Apond=0, Fevap=0, Psi=NaN, Ksat=NaN, IMD=NaN):
        """

        Args:
            Name (str): name assigned to storage node.
            Elevation (float): invert elevation (ft or m).
            MaxDepth (float): maximum water depth possible (ft or m).
            InitDepth (float): water depth at the start of the simulation (ft or m).
            Type (str): TABULAR | FUNCTIONAL
            *args (): -Arguments below-
            Curve (str | list): name of curve in [CURVES] section with surface area (ft2 or m2)
                as a function of depth (ft or m) for TABULAR geometry.
                -OR- list with:
                    A1 (float): coefficient of FUNCTIONAL relation between surface area and depth.
                    A2 (float): exponent of FUNCTIONAL relation between surface area and depth.
                    A0 (float): constant of FUNCTIONAL relation between surface area and depth.

            Apond (float): this parameter has been deprecated – use 0.
            Fevap (float): fraction of potential evaporation from surface realized (default is 0).
            Psi (float): soil suction head (inches or mm).
            Ksat (float): soil saturated hydraulic conductivity (in/hr or mm/hr).
            IMD (float): soil initial moisture deficit (fraction).
        """
        self.Name = str(Name)
        self.Elevation = Elevation
        self.MaxDepth = MaxDepth
        self.InitDepth = InitDepth
        self.Type = Type

        if args:
            if Type == Storage.Types.TABULAR:
                self._tabular_init(*args)

            elif Type == Storage.Types.FUNCTIONAL:
                self._functional_init(*args)

            else:
                raise NotImplementedError()
        else:
            self.Curve = Curve
            self._optional_args(Apond, Fevap, Psi, Ksat, IMD)

    def _functional_init(self, A1, A2, A0, Apond=0, Fevap=0, Psi=NaN, Ksat=NaN, IMD=NaN):
        """

        Args:
            A1 (float): coefficient of FUNCTIONAL relation between surface area and depth.
            A2 (float): exponent of FUNCTIONAL relation between surface area and depth.
            A0 (float): constant of FUNCTIONAL relation between surface area and depth.

            Apond (float): this parameter has been deprecated – use 0.
            Fevap (float): fraction of potential evaporation from surface realized (default is 0).
            Psi (float): soil suction head (inches or mm).
            Ksat (float): soil saturated hydraulic conductivity (in/hr or mm/hr).
            IMD (float): soil initial moisture deficit (fraction).
        """
        self.Curve = [A1, A2, A0]
        self._optional_args(Apond, Fevap, Psi, Ksat, IMD)

    def _tabular_init(self, Acurve, Apond=0, Fevap=0, Psi=NaN, Ksat=NaN, IMD=NaN):
        """

        Args:
            Acurve: name of curve in [CURVES] section with surface area (ft2 or m2)
                as a function of depth (ft or m) for TABULAR geometry.
            Apond (float): this parameter has been deprecated – use 0.
            Fevap (float): fraction of potential evaporation from surface realized (default is 0).
            Psi (float): soil suction head (inches or mm).
            Ksat (float): soil saturated hydraulic conductivity (in/hr or mm/hr).
            IMD (float): soil initial moisture deficit (fraction).
        """
        self.Curve = Acurve
        self._optional_args(Apond, Fevap, Psi, Ksat, IMD)

    def _optional_args(self, Apond=0, Fevap=0, Psi=NaN, Ksat=NaN, IMD=NaN):
        """

        Args:
            Apond (float): this parameter has been deprecated – use 0.
            Fevap (float): fraction of potential evaporation from surface realized (default is 0).
            Psi (float): soil suction head (inches or mm).
            Ksat (float): soil saturated hydraulic conductivity (in/hr or mm/hr).
            IMD (float): soil initial moisture deficit (fraction).

        Returns:

        """
        self.Apond = Apond
        self.Fevap = Fevap
        self.Psi = Psi
        self.Ksat = Ksat
        self.IMD = IMD


class Outfall(BaseSectionObject):
    """
    Section:
        [OUTFALLS]

    Purpose:
        Identifies each outfall node (i.e., final downstream boundary) of the drainage system and the corresponding
        water stage elevation. Only one link can be incident on an outfall node.

    Formats:
        - Name Elev FREE               (Gated) (RouteTo)
        - Name Elev NORMAL             (Gated) (RouteTo)
        - Name Elev FIXED      Stage   (Gated) (RouteTo)
        - Name Elev TIDAL      Tcurve  (Gated) (RouteTo)
        - Name Elev TIMESERIES Tseries (Gated) (RouteTo)

    Formats-PCSWMM:
        - Name Elevation Type Data Gated Route-To

    Remarks:
        - Name:
            name assigned to outfall node.
        - Elev:
            invert elevation (ft or m).
        - Stage:
            elevation of fixed stage outfall (ft or m).
        - Tcurve:
            name of curve in [CURVES] section containing tidal height (i.e., outfall stage) v. hour of day over a
            complete tidal cycle.
        - Tseries:
            name of time series in [TIMESERIES] section that describes how outfall stage varies with time.
        - Gated:
            YES or NO depending on whether a flap gate is present that prevents reverse flow. The default is NO.
        - RouteTo:
            optional name of a subcatchment that receives the outfall's discharge.
            The default is not to route the outfall’s discharge.
    """
    index = 'Name'

    class Types:
        FREE = 'FREE'
        NORMAL = 'NORMAL'
        FIXED = 'FIXED'
        TIDAL = 'TIDAL'
        TIMESERIES = 'TIMESERIES'

    def __init__(self, Name, Elevation, Type, *args, Data=NaN, FlapGate=False, RouteTo=NaN):
        """

        Args:
            Name (str): name assigned to outfall node.
            Elevation (float): invert elevation (ft or m).
            Type (str): one of <Types>
            *args: -Arguments below-
            Data (float | str): one of the following
                Stage (float): elevation of fixed stage outfall (ft or m).
                Tcurve (str): name of curve in [CURVES] section containing tidal height (i.e., outfall stage) v.
                    hour of day over a complete tidal cycle.
                Tseries (str): name of time series in [TIMESERIES] section that describes how outfall stage varies with time.
            FlapGate (bool): YES or NO depending on whether a flap gate is present that prevents reverse flow. The default is NO.
            RouteTo (str): optional name of a subcatchment that receives the outfall's discharge.
                           The default is not to route the outfall’s discharge.
        """
        self.Name = str(Name)
        self.Elevation = Elevation
        self.Type = Type

        if args:
            if Type in [Outfall.Types.FIXED,
                        Outfall.Types.TIDAL,
                        Outfall.Types.TIMESERIES]:
                self._data_init(*args)
            else:
                self._no_data_init(*args)
        else:
            self.Data = Data
            self.FlapGate = FlapGate
            self.RouteTo = RouteTo

    def _no_data_init(self, Gated=False, RouteTo=NaN):
        """
        if not keyword arguments were used

        Args:
            Gated (bool): YES or NO depending on whether a flap gate is present that prevents reverse flow. The default is NO.
            RouteTo (str): optional name of a subcatchment that receives the outfall's discharge.
                           The default is not to route the outfall’s discharge.
        """
        self.Data = NaN
        self.FlapGate = Gated
        self.RouteTo = RouteTo

    def _data_init(self, Data=NaN, Gated=False, RouteTo=NaN):
        """
        if not keyword arguments were used

        Args:
            Data (float | str): one of the following
                Stage (float): elevation of fixed stage outfall (ft or m).
                Tcurve (str): name of curve in [CURVES] section containing tidal height (i.e., outfall stage) v.
                    hour of day over a complete tidal cycle.
                Tseries (str): name of time series in [TIMESERIES] section that describes how outfall stage varies with time.
            Gated (bool): YES or NO depending on whether a flap gate is present that prevents reverse flow. The default is NO.
            RouteTo (str): optional name of a subcatchment that receives the outfall's discharge.
                           The default is not to route the outfall’s discharge.
        """
        self.Data = Data
        self.FlapGate = Gated
        self.RouteTo = RouteTo


class Conduit(BaseSectionObject):
    index = 'Name'

    def __init__(self, Name, FromNode, ToNode, Length, Roughness, InOffset, OutOffset, InitFlow=0, MaxFlow=NaN):
        """
        Section:
            [CONDUITS]

        Purpose:
            Identifies each conduit link of the drainage system. Conduits are pipes or channels that convey water
            from one node to another.

        Format:
            Name  Node1  Node2  Length  N  Z1  Z2  (Q0  Qmax)

        Format-PCSWMM:
            Name FromNode ToNode Length Roughness InOffset OutOffset InitFlow MaxFlow

        Remarks:
            Name
                name assigned to conduit link.
            Node1
                name of upstream node.
            Node2
                name of downstream node.
            Length
                conduit length (ft or m).
            N
                value of n (i.e., roughness parameter) in Manning’s equation.
            Z1
                offset of upstream end of conduit invert above the invert elevation of its upstream node (ft or m).
            Z2
                offset of downstream end of conduit invert above the invert elevation of its downstream node (ft or m).
            Q0
                flow in conduit at start of simulation (flow units) (default is 0).
            Qmax
                maximum flow allowed in the conduit (flow units) (default is no limit).

            These offsets are expressed as a relative distance above the node invert if the LINK_OFFSETS option is set
            to DEPTH (the default) or as an absolute elevation if it is set to ELEVATION.

        Args:
            Name (str): name assigned to conduit link.
            FromNode (str): name of upstream node.
            ToNode (str): name of downstream node.
            Length (float): conduit length (ft or m).
            Roughness (float): value of n (i.e., roughness parameter) in Manning’s equation.
            InOffset (float): offset of upstream end of conduit invert above the invert elevation of its
                              upstream node (ft or m).
            OutOffset (float): offset of downstream end of conduit invert above the invert elevation of its
                              downstream node (ft or m).
            InitFlow (float): flow in conduit at start of simulation (flow units) (default is 0).
            MaxFlow (float): maximum flow allowed in the conduit (flow units) (default is no limit).
        """
        self.Name = str(Name)
        self.FromNode = str(FromNode)
        self.ToNode = str(ToNode)
        self.Length = Length
        self.Roughness = Roughness
        self.InOffset = InOffset
        self.OutOffset = OutOffset
        self.InitFlow = InitFlow
        self.MaxFlow = MaxFlow


class Weir(BaseSectionObject):
    """
    Section:
        [WEIRS]

    Purpose:
        Identifies each weir link of the drainage system. Weirs are used to model flow
        diversions and storage node outlets.

    Format:
        Name Node1 Node2 Type CrestHt Cd (Gated EC Cd2 Sur (Width Surface))

    PC-SWMM Format:
        Name FromNode ToNode Type CrestHt Qcoeff Gated EndCon EndCoeff Surcharge RoadWidth RoadSurf

    The geometry of a weir’s opening is described in the [XSECTIONS] section.
    The following shapes must be used with each type of weir:

    The ROADWAY weir is a broad crested rectangular weir used model roadway crossings usually in conjunction with
    culvert-type conduits. It uses the FHWA HDS-5 method to determine a discharge coefficient as a function of flow
    depth and roadway width and surface.

    If no roadway data are provided then the weir behaves as a TRANSVERSE weir with Cd as its discharge coefficient.
    Note that if roadway data are provided, then values for the other optional weir parameters
    (NO for Gated, 0 for EC, 0 for Cd2, and NO for Sur)
    must be entered even though they do not apply to ROADWAY weirs.
    """
    index = 'Name'

    class Types:
        TRANSVERSE = 'TRANSVERSE'
        SIDEFLOW = 'SIDEFLOW'
        V_NOTCH = 'V-NOTCH'
        TRAPEZOIDAL = 'TRAPEZOIDAL'
        ROADWAY = 'ROADWAY'

    class Surfaces:
        PAVED = 'PAVED'
        GRAVEL = 'GRAVEL'

    def __init__(self, Name, FromNode, ToNode, Type, CrestHeight, Qcoeff, FlapGate=False, EndContractions=0,
                 EndCoeff=NaN,
                 Surcharge=True, RoadWidth=NaN, RoadSurface=NaN):
        """

        Args:
            Name (str): name assigned to weir link

            FromNode (str): name of node on inlet side of wier.

            ToNode (str): name of node on outlet side of weir.

            Type (str): TRANSVERSE, SIDEFLOW, V-NOTCH, TRAPEZOIDAL or ROADWAY.

            CrestHeight (float): amount that the weir’s crest is offset above the invert of inlet node (ft or m,
                expressed as either a depth or as an elevation, depending on the LINK_OFFSETS option setting).

            Qcoeff (float): (Cd) weir discharge coefficient
                            (for CFS if using US flow units or CMS if using metric flow units).

            FlapGate (bool): YES if flap gate present to prevent reverse flow, NO if not (default is NO).

            EndContractions (float): (EC) number of end contractions for TRANSVERSE or TRAPEZOIDAL weir (default is 0).

            EndCoeff (float): discharge coefficient for triangular ends of a TRAPEZOIDAL weir
                             (for CFS if using US flow units or CMS if using metric flow units)
                             (default is value of Cd).

            Surcharge (bool): YES if the weir can surcharge
                (have an upstream water level higher than the height of the opening);
                NO if it cannot (default is YES).

            RoadWidth (float): width of road lanes and shoulders for ROADWAY weir (ft or m).

            RoadSurface (str): type of road surface for ROADWAY weir: PAVED or GRAVEL.
        """
        self.Name = str(Name)
        self.FromNode = str(FromNode)
        self.ToNode = str(ToNode)
        self.Type = str(Type)
        self.CrestHeight = float(CrestHeight)
        self.Qcoeff = float(Qcoeff)
        self.FlapGate = bool(FlapGate)
        self.EndContractions = EndContractions
        if isnan(EndCoeff):
            EndCoeff = Qcoeff
        self.EndCoeff = float(EndCoeff)
        self.Surcharge = bool(Surcharge)
        self.RoadWidth = float(RoadWidth)
        self.RoadSurf = RoadSurface


class Outlet(BaseSectionObject):
    """
    Section:
        [OUTLETS]

    Purpose:
        Identifies each outlet flow control device of the drainage system. These devices are
        used to model outflows from storage units or flow diversions that have a user-defined
        relation between flow rate and water depth.

    Formats:
        - Name Node1 Node2 Offset TABULAR/DEPTH Qcurve (Gated)
        - Name Node1 Node2 Offset TABULAR/HEAD Qcurve (Gated)
        - Name Node1 Node2 Offset FUNCTIONAL/DEPTH C1 C2 (Gated)
        - Name Node1 Node2 Offset FUNCTIONAL/HEAD C1 C2 (Gated)

    PC-SWMM-Format:
        Name Inlet-Node Outlet-Node Outflow-Height Outlet-Type Qcoeff/QTable Qexpon Flap-Gate

    Remarks:
        - Name:
            name assigned to outlet link.
        - Node1:
            name of node on inlet end of link.
        - Node2:
            name of node on outflow end of link.
        - Offset:
            amount that the outlet is offset above the invert of inlet node (ft or m,
            expressed as either a depth or as an elevation, depending on the
            LINK_OFFSETS option setting).
        - Qcurve:
            name of the rating curve listed in the [CURVES] section that describes
            outflow rate (flow units) as a function of:
                - water depth above the offset elevation at the inlet node (ft or m) for a TABULAR/DEPTH outlet
                - head difference (ft or m) between the inlet and outflow nodes for a TABULAR/HEAD outlet.
        - C1, C2:
            coefficient and exponent, respectively, of a power function that relates outflow (Q) to:
                - water depth (ft or m) above the offset elevation at the inlet node for a FUNCTIONAL/DEPTH outlet
                - head difference (ft or m) between the inlet and outflow nodes for a FUNCTIONAL/HEAD outlet.
                (i.e., QQ = CC1HH CC2 where H is either depth or head).
        - Gated:
            YES if flap gate present to prevent reverse flow, NO if not (default is NO).
    """
    index = 'Name'

    class Types:
        TABULAR_DEPTH = 'TABULAR/DEPTH'
        TABULAR_HEAD = 'TABULAR/HEAD'
        FUNCTIONAL_DEPTH = 'FUNCTIONAL/DEPTH'
        FUNCTIONAL_HEAD = 'FUNCTIONAL/HEAD'

    def __init__(self, Name, FromNode, ToNode, Offset, Type, *args, Curve=None, Gated=False):
        self.Name = str(Name)

        self.FromNode = str(FromNode)
        self.ToNode = str(ToNode)
        self.Offset = Offset
        self.Type = Type

        if args:
            if Type.startswith('TABULAR'):
                self._tabular_init(*args)

            elif Type.startswith('FUNCTIONAL'):
                self._functional_init(*args)

            else:
                raise NotImplementedError('Type: "{}" is not implemented'.format(Type))

        else:
            self.Curve = Curve
            self.Gated = Gated

    def _tabular_init(self, Qcurve, Gated=False):
        self.Curve = Qcurve
        self.Gated = Gated

    def _functional_init(self, C1, C2, Gated=False):
        self.Curve = [C1, C2]
        self.Gated = Gated


class Orifice(BaseSectionObject):
    index = 'Name'

    class Types:
        SIDE = 'SIDE'
        BOTTOM = 'BOTTOM'

    def __init__(self, Name, FromNode, ToNode, Type, Offset, Qcoeff, FlapGate=False, Orate=0):
        """
        From the User's Manual Version 5.1 (2015-09) page 308

        Format:
            Name Node1 Node2 Type Offset Cd (Flap Orate)

        Purpose:
                Identifies each orifice link of the drainage system. An orifice link serves to limit the
                flow exiting a node and is often used to model flow diversions and storage node
                outlets.

        Args:
            Name (str): name assigned to orifice link.
            FromNode (str): (Node1) name of node on inlet end of orifice.
            ToNode (str): (Node2) name of node on outlet end of orifice.
            Type (str): orientation of orifice: either SIDE or BOTTOM.
            Offset (float): amount that a Side Orifice’s bottom or the position of a Bottom Orifice is offset above the invert
                        of inlet node (ft or m, expressed as either a depth or as an elevation,
                        depending on the LINK_OFFSETS option setting).
            Qcoeff (float): (Cd) discharge coefficient (unitless).
            FlapGate (bool): YES if flap gate present to prevent reverse flow, NO if not (default is NO).
            Orate (int): time in decimal hours to open a fully closed orifice (or close a fully open one).
                            Use 0 if the orifice can open/close instantaneously.

        The geometry of an orifice’s opening must be described in the [XSECTIONS] section.
        The only allowable shapes are CIRCULAR and RECT_CLOSED (closed rectangular).
        """
        self.Name = str(Name)
        self.FromNode = str(FromNode)
        self.ToNode = str(ToNode)
        self.Type = Type
        self.Offset = Offset
        self.Qcoeff = Qcoeff
        self.FlapGate = FlapGate
        self.Orate = Orate


class Junction(BaseSectionObject):
    index = 'Name'

    def __init__(self, Name, Elevation, MaxDepth=0, InitDepth=0, SurDepth=0, Aponded=0):
        """
        Section:
            [JUNCTIONS]

        Purpose:
            Identifies each junction node of the drainage system.
            Junctions are points in space where channels and pipes connect together.
            For sewer systems they can be either connection fittings or manholes.

        Format:
            Name Elev (Ymax Y0 Ysur Apond)

        Format-PC-SWMM:
            Name  Elevation MaxDepth InitDepth SurDepth Aponded

        Remarks:
            Name:
                name assigned to junction node.
            Elev:
                elevation of junction invert (ft or m).
            Ymax:
                depth from ground to invert elevation (ft or m) (default is 0).
            Y0:
                water depth at start of simulation (ft or m) (default is 0).
            Ysur:
                maximum additional head above ground elevation that manhole junction
                can sustain under surcharge conditions (ft or m) (default is 0).
            Apond:
                area subjected to surface ponding once water depth exceeds Ymax (ft2 or m2) (default is 0).

            If Ymax is 0 then SWMM sets the maximum depth equal to the distance
            from the invert to the top of the highest connecting link.

            If the junction is part of a force main section of the system then set Ysur
            to the maximum pressure that the system can sustain.

            Surface ponding can only occur when Apond is non-zero and the ALLOW_PONDING analysis option is turned on.

        Args:
            Name (str): name assigned to junction node.
            Elevation (float): elevation of junction invert (ft or m).
            MaxDepth (float): depth from ground to invert elevation (ft or m) (default is 0).
            InitDepth (float): water depth at start of simulation (ft or m) (default is 0).
            SurDepth (float): maximum additional head above ground elevation that manhole junction
                                can sustain under surcharge conditions (ft or m) (default is 0).
            Aponded (float): area subjected to surface ponding once water depth exceeds Ymax (ft2 or m2) (default is 0).
        """
        self.Name = str(Name)
        self.Elevation = Elevation
        self.MaxDepth = MaxDepth
        self.InitDepth = InitDepth
        self.SurDepth = SurDepth
        self.Aponded = Aponded


class CrossSection(BaseSectionObject):
    index = 'Link'

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
            optional name of snow pack object (from [SNOWPACKS] section) that characterizes snow accumulation and melting over the subcatchment.
    """
    index = 'Name'

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
    index = 'subcatchment'

    class RoutToOption:
        __class__ = 'RoutTo Option'
        IMPERVIOUS = 'IMPERVIOUS'
        PERVIOUS = 'PERVIOUS'
        OUTLET = 'OUTLET'

    def __init__(self, subcatchment, N_Imperv, N_Perv, S_Imperv, S_Perv, PctZero, RouteTo=RoutToOption.OUTLET,
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
        self.subcatchment = str(subcatchment)
        self.N_Imperv = N_Imperv
        self.N_Perv = N_Perv
        self.S_Imperv = S_Imperv
        self.S_Perv = S_Perv
        self.PctZero = PctZero
        self.RouteTo = RouteTo
        self.PctRouted = PctRouted


class Infiltration(BaseSectionObject):
    index = 'subcatchment'

    def __init__(self, subcatchment):
        self.subcatchment = str(subcatchment)

    @classmethod
    def from_line(cls, subcatchment, *args, **kwargs):
        n_args = len(args) + len(kwargs.keys()) + 1
        if n_args == 6:  # hortn
            return InfiltrationHorton(subcatchment, *args, **kwargs)
        elif n_args == 4:
            return InfiltrationGreenAmpt(subcatchment, *args, **kwargs)
        else:
            # TODO
            return InfiltrationCurveNumber(subcatchment, *args, **kwargs)


class InfiltrationHorton(Infiltration):

    def __init__(self, subcatchment, MaxRate, MinRate, Decay, DryTime, MaxInf):
        """
        Horton:
            Subcat  MaxRate  MinRate  Decay  DryTime  MaxInf

        PC-SWMM-Format:
            Subcatchment MaxRate MinRate Decay DryTime MaxInfil

        Args:
            line ():

        Returns:

        """
        Infiltration.__init__(self, subcatchment)
        self.MaxRate = MaxRate
        self.MinRate = MinRate
        self.Decay = Decay
        self.DryTime = DryTime
        self.MaxInf = MaxInf


class InfiltrationGreenAmpt(Infiltration):

    def __init__(self, subcatchment, Psi, Ksat, IMD):
        """
        Green-Ampt:
            Subcat  Psi  Ksat  IMD

        PC-SWMM-Format:
            Subcatchment MaxRate MinRate Decay DryTime MaxInfil

        Args:
            line ():

        Returns:

        """
        Infiltration.__init__(self, subcatchment)
        self.Psi = Psi
        self.Ksat = Ksat
        self.IMD = IMD


class InfiltrationCurveNumber(Infiltration):

    def __init__(self, subcatchment, CurveNo, Ksat, DryTime):
        """
        Curve-Number:
            Subcat  CurveNo  Ksat  DryTime

        PC-SWMM-Format:
            Subcatchment MaxRate MinRate Decay DryTime MaxInfil

        Args:
            line ():

        Returns:

        """
        Infiltration.__init__(self, subcatchment)
        self.CurveNo = CurveNo
        self.Ksat = Ksat
        self.DryTime = DryTime


class DryWeatherFlow(BaseSectionObject):
    index = ['Node', 'kind']

    def __init__(self, Node, kind, Base, pattern1=NaN, pattern2=NaN, pattern3=NaN, pattern4=NaN, pattern5=NaN):
        """
        Type: FLOW, <pollutant>
        Base: baseline
        Pat:  'monthly', 'daily', 'hourly' and 'weekend hourly' pattern

        Node  Type  Base  (Pat1  Pat2  Pat3  Pat4)
        Args:
            Node ():
            kind ():
        """
        self.Node = str(Node)
        self.kind = kind
        self.Base = Base
        self.pattern1 = pattern1
        self.pattern2 = pattern2
        self.pattern3 = pattern3
        self.pattern4 = pattern4


class Loss(BaseSectionObject):
    index = 'Link'

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


class Inflow(BaseSectionObject):
    index = ['Node', 'Constituent']

    class TypeOption:
        __class__ = 'Type Option'
        FLOW = 'FLOW'

    def __init__(self, Node, Constituent, TimeSeries=None, Type=TypeOption.FLOW, Mfactor=1.0, Sfactor=1.0, Baseline=0., Pattern=NaN):
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


class RainGauge(BaseSectionObject):
    """
    Section:
        [RAINGAGES]

    Purpose:
        Identifies each rain gage that provides rainfall data for the study area.

    Formats:
        Name Form Intvl SCF TIMESERIES Tseries
        Name Form Intvl SCF FILE       Fname   Sta Units

    PC-SWMM-Format:
        Name Format Interval SCF Source

    Remarks:
        Name
            name assigned to rain gage.
        Form
            form of recorded rainfall, either INTENSITY, VOLUME or CUMULATIVE.
        Intvl
            time interval between gage readings in decimal hours or hours:minutes format (e.g., 0:15 for 15-minute readings).
        SCF
            snow catch deficiency correction factor (use 1.0 for no adjustment).
        Tseries
            name of time series in [TIMESERIES] section with rainfall data.
        Fname
            name of external file with rainfall data. Rainfall files are discussed in Section 11.3 Rainfall Files.
        Sta
            name of recording station used in the rain file.
        Units
            rain depth units used in the rain file, either IN (inches) or MM (millimeters).
    """
    index = 'Name'

    class Formats:
        INTENSITY = 'INTENSITY'
        VOLUME = 'VOLUME'
        CUMULATIVE = 'CUMULATIVE'

    class Sources:
        TIMESERIES = 'TIMESERIES'
        FILE = 'FILE'

    class Unit:
        IN = 'IN'
        MM = 'MM'

    def __init__(self, Name, Format, Interval, SCF, Source, *args, Timeseries=NaN, Filename=NaN, Station=NaN,
                 Units=NaN):
        """

        Args:
            Name (str): name assigned to rain gage.
            Format (str): form of recorded rainfall, either INTENSITY, VOLUME or CUMULATIVE.
            Interval (str, Timedelta): time interval between gage readings in decimal hours or hours:minutes format
                                        (e.g., 0:15 for 15-minute readings).
            SCF (float): snow catch deficiency correction factor (use 1.0 for no adjustment).
            Source (str):
            *args:
            Timeseries (str): name of time series in [TIMESERIES] section with rainfall data.
            Filename (str): name of external file with rainfall data.
                            Rainfall files are discussed in Section 11.3 Rainfall Files.
            Station (str): name of recording station used in the rain file.
            Units (str): rain depth units used in the rain file, either IN (inches) or MM (millimeters).
        """
        self.Name = str(Name)
        self.Format = Format
        self.Interval = Interval
        self.SCF = SCF
        self.Source = Source

        self.Timeseries = Timeseries
        self.Filename = Filename
        self.Station = Station
        self.Units = Units

        l = len(args)
        if args:
            if (Source == RainGauge.Sources.TIMESERIES) and (l == 1):
                self.Timeseries = args[0]
            elif Source == RainGauge.Sources.FILE:

                self.Filename = args[0]
                self.Station = args[1]
                self.Units = args[2]
            else:
                raise NotImplementedError()


class Pump(BaseSectionObject):
    """
    Section:
        [PUMPS]

    Purpose:
        Identifies each pump link of the drainage system.

    Format:
        Name Node1 Node2 Pcurve (Status Startup Shutoff)

    PC-SWMM-Format:
        Name  Inlet-Node  Outlet-Node  Pump-Curve  Init.-Status  Startup-Depth  Shutoff-Depth

    Remarks:
        - Name:
            name assigned to pump link.
        - Node1:
            name of node on inlet side of pump.
        - Node2:
            name of node on outlet side of pump.
        - Pcurve:
            name of pump curve listed in the [CURVES] section of the input.
        - Status:
            status at start of simulation (either ON or OFF; default is ON).
        - Startup:
            depth at inlet node when pump turns on (ft or m) (default is 0).
        - Shutoff:
            depth at inlet node when pump shuts off (ft or m) (default is 0).

    See Section 3.2 for a description of the different types of pumps available.
    """
    index = 'Name'

    class States:
        ON = 'ON'
        OFF = 'OFF'

    def __init__(self, Name, FromNode, ToNode, Pcurve, Status='ON', Startup=0, Shutoff=0):
        self.Name = str(Name)
        self.FromNode = str(FromNode)
        self.ToNode = str(ToNode)
        self.Pcurve = Pcurve
        self.Status = Status
        self.Startup = Startup
        self.Shutoff = Shutoff


class Pattern(BaseSectionObject):
    """
    Section:
        [PATTERNS]

    Purpose:
        Specifies time pattern of dry weather flow or quality in the form of adjustment factors
        applied as multipliers to baseline values.


    Format:
        - Name MONTHLY Factor1 Factor2 ... Factor12
        - Name DAILY Factor1  Factor2  ...  Factor7
        - Name HOURLY Factor1  Factor2  ...  Factor24
        - Name WEEKEND Factor1  Factor2  ...  Factor24

    Remarks:
        - The MONTHLY format is used to set monthly pattern factors for dry weather flow constituents.
        - The DAILY format is used to set dry weather pattern factors for each day of the week, where Sunday is day 1.
        - The HOURLY format is used to set dry weather factors for each hour of the day starting from midnight.
            If these factors are different for weekend days than for weekday days then the WEEKEND format can be used
            to specify hourly adjustment factors just for weekends.
        - More than one line can be used to enter a pattern’s factors by repeating the pattern’s name
            (but not the pattern type) at the beginning of each additional line.
        - The pattern factors are applied as multipliers to any baseline dry weather flows or quality
            concentrations supplied in the [DWF] section.
    """
    index = 'Name'

    class Types:
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
    def convert_lines(cls, lines):
        """multiple lines for one entry"""
        new_lines = list()
        for line in lines:
            if line[1] in ['MONTHLY', 'DAILY', 'HOURLY', 'WEEKEND']:
                new_lines.append(line)
            else:
                new_lines[-1] += line[1:]

        # sec_lines = list()
        for line in new_lines:
            # sec_lines.append()
            yield cls(*line)

        # return sec_lines


class Pollutant(BaseSectionObject):
    """
    Section:
        [POLLUTANTS]

    Purpose:
        Identifies the pollutants being analyzed.

    Format:
        Name Units Crain Cgw Cii Kd (Sflag CoPoll CoFract Cdwf Cinit)

    PC-SWMM-Format:
        Name Units Crain Cgw Crdii Kdecay SnowOnly Co-Pollutant Co-Frac Cdwf Cinit

    Remarks:
        Name
            name assigned to pollutant.
        Units
            concentration units
                MG/L for milligrams per liter
                UG/L for micrograms per liter
                #/L for direct count per liter
        Crain
            concentration of pollutant in rainfall (concentration units).
        Cgw
            concentration of pollutant in groundwater (concentration units).
        Cii
            concentration of pollutant in inflow/infiltration (concentration units).
        Kdecay
            first-order decay coefficient (1/days).
        Sflag
            YES if pollutant buildup occurs only when there is snow cover, NO otherwise (default is NO).
        CoPoll
            name of co-pollutant (default is no co-pollutant designated by a *).
        CoFract
            fraction of co-pollutant concentration (default is 0).
        Cdwf
            pollutant concentration in dry weather flow (default is 0).
        Cinit
            pollutant concentration throughout the conveyance system at the start of the simulation (default is 0).

        FLOW is a reserved word and cannot be used to name a pollutant.

        Parameters Sflag through Cinit can be omitted if they assume their default values.
        If there is no co-pollutant but non-default values for Cdwf or Cinit, then enter an asterisk (*)
        for the co-pollutant name.

        When pollutant X has a co-pollutant Y, it means that fraction CoFract of pollutant Y’s runoff
        concentration is added to pollutant X’s runoff concentration when wash off from a subcatchment is computed.

        The dry weather flow concentration can be overridden for any specific node of the conveyance
        system by editing the node’s Inflows property.
    """
    index = 'Name'

    class Unit:
        MG_PER_L = 'MG/L'
        UG_PER_L = 'UG/L'
        COUNT_PER_L = '#/L'

    def __init__(self, Name, Units, Crain, Cgw, Crdii, Kdecay,
                 SnowOnly=False, Co_Pollutant='*', Co_Frac=0, Cdwf=0, Cinit=0):
        self.Name = str(Name)
        self.Units = Units
        self.Crain = Crain
        self.Cgw = Cgw
        self.Crdii = Crdii
        self.Kdecay = Kdecay
        self.SnowOnly = SnowOnly
        self.Co_Pollutant = Co_Pollutant
        self.Co_Frac = Co_Frac
        self.Cdwf = Cdwf
        self.Cinit = Cinit


class Transect(BaseSectionObject):
    """
    Section:
        [TRANSECTS]

    Purpose:
        Describes the cross-section geometry of natural channels or conduits with irregular shapes
        following the HEC-2 data format.

    Formats:
        NC Nleft Nright Nchanl
        X1 Name Nsta Xleft Xright 0 0 0 Lfactor Wfactor Eoffset
        GR Elev Station ... Elev Station

    Remarks:
        Nleft:
            Manning’s n of right overbank portion of channel (use 0 if no change from previous NC line).
        Nright:
            Manning’s n of right overbank portion of channel (use 0 if no change from previous NC line.
        Nchanl:
            Manning’s n of main channel portion of channel (use 0 if no change from previous NC line.
        Name:
            name assigned to transect.
        Nsta:
            number of stations across cross-section at which elevation data is supplied.
        Xleft:
            station position which ends the left overbank portion of the channel (ft or m).
        Xright :
            station position which begins the right overbank portion of the channel (ft or m).
        Lfactor:
            meander modifier that represents the ratio of the length of a meandering main channel to the length of the
            overbank area that surrounds it (use 0 if not applicable).
        Wfactor:
            factor by which distances between stations should be multiplied to increase (or decrease)
            the width of the channel (enter 0 if not applicable).
        Eoffset:
            amount added (or subtracted) from the elevation of each station (ft or m).
        Elev:
            elevation of the channel bottom at a cross-section station relative to some fixed reference (ft or m).
        Station:
            distance of a cross-section station from some fixed reference (ft or m).

    Transect geometry is described as shown below, assuming that one is looking in a downstream direction:

    The first line in this section must always be a NC line. After that, the NC line is only needed when a transect has
    different Manning’s n values than the previous one.

    The Manning’s n values on the NC line will supersede any roughness value entered for the conduit which uses the
    irregular cross-section.

    There should be one X1 line for each transect.
    Any number of GR lines may follow, and each GR line can have any number of Elevation-Station data pairs.
    (In HEC-2 the GR line is limited to 5 stations.)

    The station that defines the left overbank boundary on the X1 line must correspond to one of the station entries
    on the GR lines that follow. The same holds true for the right overbank boundary. If there is no match, a warning
    will be issued and the program will assume that no overbank area exists.

    The meander modifier is applied to all conduits that use this particular transect for their cross section.
    It assumes that the length supplied for these conduits is that of the longer main channel.
    SWMM will use the shorter overbank length in its calculations while increasing the main channel roughness to account
    for its longer length.
    """
    index = 'Name'

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

    def set_roughness(self, left=0, right=0, channel=0):
        self.roughness_left = float(left)
        self.roughness_right = float(right)
        self.roughness_channel = float(channel)

    def set_bank_stations(self, left=0, right=0):
        self.bank_station_left = float(left)
        self.bank_station_right = float(right)

    def set_modifiers(self, meander=0, stations=0, elevations=0):
        self.modifier_stations = float(stations)
        self.modifier_elevations = float(elevations)
        self.modifier_meander = float(meander)

    def get_number_stations(self):
        """get number of stations"""
        return len(self.station_elevations)

    @classmethod
    def convert_lines(cls, lines):
        """multiple lines for one entry"""
        last_roughness = [0, 0, 0]
        last = None

        for line in lines:
            if line[0] == 'NC':
                last_roughness = line[1:]

            elif line[0] == 'X1':
                if last is not None:
                    yield last
                last = cls(Name=line[1])
                last.set_bank_stations(*line[3:5])
                last.set_modifiers(*line[8:])
                last.set_roughness(*last_roughness)

            elif line[0] == 'GR':
                it = iter(line[1:])
                for station in it:
                    elevation = next(it)
                    last.add_station_elevation(station, elevation)
        yield last

    def inp_line(self):
        s = 'NC {} {} {}\n'.format(self.roughness_left, self.roughness_right, self.roughness_channel)
        s += 'X1 {} {} {} {} 0 0 0 {} {} {}\n'.format(self.Name, self.get_number_stations(),
                                                      self.bank_station_left, self.bank_station_right,
                                                      self.modifier_stations, self.modifier_elevations,
                                                      self.modifier_meander)
        s += 'GR'
        i = 0
        for x, y in self.station_elevations:
            s += ' {} {}'.format(x, y)
            i += 1
            if i == 5:
                i = 0
                s += '\nGR'

        if s.endswith('GR'):
            s = s[:-3]
        s += '\n'
        return s

# class Loading(BaseSection):
#     """
#     Section:
#         [LOADINGS]
#
#     Purpose:
#         Specifies the pollutant buildup that exists on each subcatchment at the start of a simulation.
#
#     Format:
#         Subcat  Pollut  InitBuildup  Pollut  InitBuildup ...
#
#     PC-SWMM-Format:
#         Subcatchment Pollutant Buildup
#
#     Remarks:
#         Subcat
#             name of a subcatchment.
#         Pollut
#             name of a pollutant.
#         InitBuildup
#             initial buildup of pollutant (lbs/acre or kg/hectare).
#
#         More than one pair of pollutant - buildup values can be entered per line.
#         If more than one line is needed, then the subcatchment name must still be entered first on the succeeding lines.
#
#         If an initial buildup is not specified for a pollutant,
#         then its initial buildup is computed by applying the DRY_DAYS option
#         (specified in the [OPTIONS] section) to the pollutant’s buildup function for each land use in the subcatchment.
#     """
#     index = 'Subcatchment'
#
#     def __init__(self, Subcatchment):
#         self.Subcatchment = Subcatchment
#
#     @classmethod
#     def convert_lines(cls, lines):
#         """multiple lines for one entry"""
#         new_lines = list()
#         for line in lines:
#             if line[1] in ['MONTHLY', 'DAILY', 'HOURLY', 'WEEKEND']:
#                 new_lines.append(line)
#             else:
#                 new_lines[-1].append(line[1:])
#
#         # sec_lines = list()
#         for line in new_lines:
#             # sec_lines.append()
#             yield cls(*line)
#
#         new_lines = {}
#         for line in lines:
#
#             subcat = line[0]
#
#             it = iter(line[1:])
#             for a in it:
#                 b = next(it)
#                 if subcat not in new_lines:
#                     new_lines[subcat] = {'Pollutant': [a],
#                                          'InitBuildup': [b]}
#                 else:
#                     new_lines[subcat]['Pollutant'].append(a)
#                     new_lines[subcat]['InitBuildup'].append(b)
