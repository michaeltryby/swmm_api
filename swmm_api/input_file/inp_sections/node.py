from numpy import NaN

from ..inp_helpers import BaseSectionObject
from .identifiers import IDENTIFIERS

class Junction(BaseSectionObject):
    identifier =IDENTIFIERS.Name

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
        If Ksat is zero then no seepage occurs while if IMD is zero then seepage occurs at a constant rate equal to
        Ksat.
        Otherwise seepage rate will vary with storage depth.
    """
    identifier =IDENTIFIERS.Name

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
    identifier =IDENTIFIERS.Name

    class Types:
        FREE = 'FREE'
        NORMAL = 'NORMAL'
        FIXED = 'FIXED'
        TIDAL = 'TIDAL'
        TIMESERIES = 'TIMESERIES'

    def __init__(self, Name, Elevation, Type, *args, Data=NaN, FlapGate=False, RouteTo=NaN):
        """Identifies each outfall node (i.e., final downstream boundary) of the drainage system and the corresponding
        water stage elevation. Only one link can be incident on an outfall node.

        Args:
            Name (str): name assigned to outfall node.
            Elevation (float): invert elevation (ft or m).
            Type (str): one of <Types>
            *args: -Arguments below-
            Data (float | str): one of the following
                Stage (float): elevation of fixed stage outfall (ft or m).
                Tcurve (str): name of curve in [CURVES] section containing tidal height (i.e., outfall stage) v.
                    hour of day over a complete tidal cycle.
                Tseries (str): name of time series in [TIMESERIES] section that describes how outfall stage varies
                with time.
            FlapGate (bool): YES or NO depending on whether a flap gate is present that prevents reverse flow. The
            default is NO.
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
        if no keyword arguments used

        Args:
            Gated (bool): YES or NO depending on whether a flap gate is present that prevents reverse flow. The
            default is NO.
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
                Tseries (str): name of time series in [TIMESERIES] section that describes how outfall stage varies
                with time.
            Gated (bool): YES or NO depending on whether a flap gate is present that prevents reverse flow. The
            default is NO.
            RouteTo (str): optional name of a subcatchment that receives the outfall's discharge.
                           The default is not to route the outfall’s discharge.
        """
        self.Data = Data
        self.FlapGate = Gated
        self.RouteTo = RouteTo
