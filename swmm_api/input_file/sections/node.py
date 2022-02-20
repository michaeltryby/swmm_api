from numpy import NaN

from ._identifiers import IDENTIFIERS
from ..helpers import BaseSectionObject
from .._type_converter import to_bool, infer_type
from ..section_labels import JUNCTIONS, OUTFALLS, STORAGE


# NEU in python 3.7
# from dataclasses import dataclass
# @dataclass
# class Junction2(BaseSectionObject):
#     _identifier = IDENTIFIERS.Name
#     Name: str
#     Elevation: float
#     MaxDepth: float = 0
#     InitDepth: float = 0
#     SurDepth: float = 0
#     Aponded: float = 0


class _Node(BaseSectionObject):
    _identifier = IDENTIFIERS.Name

    def __init__(self, Name, Elevation):
        self.Name = str(Name)
        self.Elevation = float(Elevation)


class Junction(_Node):
    """
    Section: [**JUNCTIONS**]

    Purpose:
        Identifies each junction node of the drainage system.
        Junctions are points in space where channels and pipes connect together.
        For sewer systems they can be either connection fittings or manholes.

    Format:
        ::

            Name Elev (Ymax Y0 Ysur Apond)

    Format-PCSWMM:
        ``Name  InvertElev  MaxDepth  InitDepth  SurchargeDepth  PondedArea``

    Format-SWMM-GUI:
        ``Name  Elevation  MaxDepth  InitDepth  SurDepth  Aponded``

    Remarks:
        If Ymax is 0 then SWMM sets the maximum depth equal to the distance
        from the invert to the top of the highest connecting link.

        If the junction is part of a force main section of the system then set Ysur
        to the maximum pressure that the system can sustain.

        Surface ponding can only occur when Apond is non-zero and the ALLOW_PONDING analysis option is turned on.

    Args:
        Name (str): name assigned to junction node.
        Elevation (float): elevation of junction invert (ft or m). ``Elev``
        MaxDepth (float): depth from ground to invert elevation (ft or m) (default is 0). ``Ymax``
        InitDepth (float): water depth at start of simulation (ft or m) (default is 0). ``Y0``
        SurDepth (float): maximum additional head above ground elevation that manhole junction
                            can sustain under surcharge conditions (ft or m) (default is 0). ``Ysur``
        Aponded (float): area subjected to surface ponding once water depth exceeds Ymax (ft2 or m2) (default is 0). ``Apond``

    Attributes:
        Name (str): name assigned to junction node.
        Elevation (float): elevation of junction invert (ft or m). ``Elev``
        MaxDepth (float): depth from ground to invert elevation (ft or m) (default is 0). ``Ymax``
        InitDepth (float): water depth at start of simulation (ft or m) (default is 0). ``Y0``
        SurDepth (float): maximum additional head above ground elevation that manhole junction
                            can sustain under surcharge conditions (ft or m) (default is 0). ``Ysur``
        Aponded (float): area subjected to surface ponding once water depth exceeds Ymax (ft2 or m2) (default is 0). ``Apond``
    """
    _section_label = JUNCTIONS

    def __init__(self, Name, Elevation, MaxDepth=0, InitDepth=0, SurDepth=0, Aponded=0):
        _Node.__init__(self, Name, Elevation)
        self.MaxDepth = float(MaxDepth)
        self.InitDepth = float(InitDepth)
        self.SurDepth = float(SurDepth)
        self.Aponded = float(Aponded)


class Outfall(_Node):
    """
    Section: [**OUTFALLS**]

    Purpose:
        Identifies each outfall node (i.e., final downstream boundary) of the drainage system and the corresponding
        water stage elevation. Only one link can be incident on an outfall node.

    Formats:
        ::

            Name Elev FREE               (Gated) (RouteTo)
            Name Elev NORMAL             (Gated) (RouteTo)
            Name Elev FIXED      Stage   (Gated) (RouteTo)
            Name Elev TIDAL      Tcurve  (Gated) (RouteTo)
            Name Elev TIMESERIES Tseries (Gated) (RouteTo)

    Formats-PCSWMM:
        ``Name  InvertElev  OutfallType  Stage/Table/TimeSeries  TideGate  RouteTo``

    Format-SWMM-GUI:
        ``Name  Elevation  Type  StageData  Gated  RouteTo``

    Args:
        Name (str): name assigned to outfall node.
        Elevation (float): invert elevation (ft or m). ``Elev``
        Type (str): one of ``FREE``, ``NORMAL``, ``FIXED``, ``TIDAL``, ``TIMESERIES``
        *args: -Arguments below-
        Data (float | str): one of the following

            - Stage (float): elevation of fixed stage outfall (ft or m). for ``FIXED``-Type
            - Tcurve (str): name of curve in [``CURVES``] section containing tidal height (i.e., outfall stage) v. hour of day over a complete tidal cycle. for ``TIDAL``-Type
            - Tseries (str): name of time series in [``TIMESERIES``] section that describes how outfall stage varies with time.  for ``TIMESERIES``-Type

        FlapGate (bool, Optional): ``YES`` or ``NO`` depending on whether a flap gate is present that prevents reverse flow. The default is ``NO``. ``Gated``
        RouteTo (str, Optional): name of a subcatchment that receives the outfall's discharge. The default is not to route the outfall’s discharge.

    Attributes:
        Name (str): name assigned to outfall node.
        Elevation (float): invert elevation (ft or m). ``Elev``
        Type (str): one of ``FREE``, ``NORMAL``, ``FIXED``, ``TIDAL``, ``TIMESERIES``
        Data (float | str): one of the following

            - Stage (float): elevation of fixed stage outfall (ft or m). for ``FIXED``-Type
            - Tcurve (str): name of curve in [``CURVES``] section containing tidal height (i.e., outfall stage) v. hour of day over a complete tidal cycle. for ``TIDAL``-Type
            - Tseries (str): name of time series in [``TIMESERIES``] section that describes how outfall stage varies with time.  for ``TIMESERIES``-Type

        FlapGate (bool, Optional): ``YES`` or ``NO`` depending on whether a flap gate is present that prevents reverse flow. The default is ``NO``. ``Gated``
        RouteTo (str, Optional): name of a subcatchment that receives the outfall's discharge. The default is not to route the outfall’s discharge.
    """
    _section_label = OUTFALLS

    class TYPES:
        FREE = 'FREE'
        NORMAL = 'NORMAL'
        FIXED = 'FIXED'
        TIDAL = 'TIDAL'
        TIMESERIES = 'TIMESERIES'

    def __init__(self, Name, Elevation, Type, *args, Data=NaN, FlapGate=False, RouteTo=NaN):
        _Node.__init__(self, Name, Elevation)
        self.Type = Type
        self.Data = NaN

        if args:
            if Type in [Outfall.TYPES.FIXED,
                        Outfall.TYPES.TIDAL,
                        Outfall.TYPES.TIMESERIES]:
                self._data_init(*args)
            else:
                if len(args) == 3:
                    self._data_init(*args)
                else:
                    self._no_data_init(*args)
        else:
            self.Data = Data
            self.FlapGate = to_bool(FlapGate)
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
        self.FlapGate = to_bool(Gated)
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
        self.FlapGate = to_bool(Gated)
        self.RouteTo = RouteTo


class Storage(_Node):
    """
    Section: [**STORAGE**]

    Purpose:
        Identifies each storage node of the drainage system.
        Storage nodes can have any shape as specified by a surface area versus water depth relation.

    Format:
        ::

            Name Elev Ymax Y0 TABULAR    Acurve   (Apond Fevap Psi Ksat IMD)
            Name Elev Ymax Y0 FUNCTIONAL A1 A2 A0 (Apond Fevap Psi Ksat IMD)

    Format-PCSWMM:
        ``Name Elev MaxDepth InitDepth Shape CurveName/Params N/A Fevap Psi Ksat IMD``

    Format-SWMM-GUI:
        ``Name  InvertElev  MaxDepth  InitDepth  StorageCurve  CurveParams  EvapFrac  InfiltrationParameters``

    Remarks:
        A1, A2, and A0 are used in the following expression that relates surface area (ft2 or m2) to water depth
        (ft or m) for a storage unit with ``FUNCTIONAL`` geometry:

        Area = A0 + A1 * Depth ^ A2

        For ``TABULAR`` geometry, the surface area curve will be extrapolated outwards to meet the unit's maximum depth
        if need be.

        The parameters Psi, Ksat, and IMD need only be supplied if seepage loss through the soil at the bottom and
        sloped sides of the storage unit should be considered.
        They are the same Green-Ampt infiltration parameters described in the [``INFILTRATION``] section.
        If Ksat is zero then no seepage occurs while if IMD is zero then seepage occurs at a constant rate equal to
        Ksat.
        Otherwise seepage rate will vary with storage depth.

    From C-Code:
        ::

            //  Format of input line is:
            //     nodeID  elev  maxDepth  initDepth  FUNCTIONAL a1 a2 a0 surDepth fEvap (infil) //(5.1.013)
            //     nodeID  elev  maxDepth  initDepth  TABULAR    curveID  surDepth fEvap (infil) //

    Args:
        Name (str): name assigned to storage node.
        Elevation (float): invert elevation (ft or m). ``Elev``
        MaxDepth (float): maximum water depth possible (ft or m). ``Ymax``
        InitDepth (float): water depth at the start of the simulation (ft or m). ``Y0``
        Type (str): ``TABULAR`` | ``FUNCTIONAL``
        *args (): -Arguments below-
        Curve (str | list):

            - :obj:`str`: name of curve in [``CURVES``] section with surface area (ft2 or m2) as a function of depth (ft or m) for ``TABULAR`` geometry. ``Acurve``
            - :obj:`list`: ``FUNCTIONAL`` relation between surface area and depth with

               - A1 (:obj:`float`): coefficient
               - A2 (:obj:`float`): exponent
               - A0 (:obj:`float`): constant

        Apond (float): this parameter has been deprecated – use 0.
        Fevap (float): fraction of potential evaporation from surface realized (default is 0).
        Psi (float): soil suction head (inches or mm).
        Ksat (float): soil saturated hydraulic conductivity (in/hr or mm/hr).
        IMD (float): soil initial moisture deficit (fraction).

    Attributes:
        Name (str): name assigned to storage node.
        Elevation (float): invert elevation (ft or m). ``Elev``
        MaxDepth (float): maximum water depth possible (ft or m). ``Ymax``
        InitDepth (float): water depth at the start of the simulation (ft or m). ``Y0``
        Type (str): ``TABULAR`` or ``FUNCTIONAL``
        Curve (str | list):

            - :obj:`str`: name of curve in [``CURVES``] section with surface area (ft2 or m2) as a function of depth (ft or m) for ``TABULAR`` geometry. ``Acurve``
            - :obj:`list`: ``FUNCTIONAL`` relation between surface area and depth with

               - A1 (:obj:`float`): coefficient
               - A2 (:obj:`float`): exponent
               - A0 (:obj:`float`): constant

        Apond (float): this parameter has been deprecated – use 0.
        Fevap (float): fraction of potential evaporation from surface realized (default is 0).
        Psi (float): soil suction head (inches or mm).
        Ksat (float): soil saturated hydraulic conductivity (in/hr or mm/hr).
        IMD (float): soil initial moisture deficit (fraction).
    """
    _section_label = STORAGE

    class TYPES:
        TABULAR = 'TABULAR'
        FUNCTIONAL = 'FUNCTIONAL'

    def __init__(self, Name: str, Elevation: float, MaxDepth: float, InitDepth: float, Type: str, *args, Curve=None,
                 Apond: float = 0, Fevap: float=0, Psi: float=NaN, Ksat: float=NaN, IMD: float=NaN):
        _Node.__init__(self, Name, Elevation)
        self.MaxDepth = float(MaxDepth)
        self.InitDepth = float(InitDepth)
        self.Type = Type

        if args:
            if Type == Storage.TYPES.TABULAR:
                self._tabular_init(*args)

            elif Type == Storage.TYPES.FUNCTIONAL:
                self._functional_init(*args)

            else:
                raise NotImplementedError()
        else:
            self.Curve = Curve
            self._optional_args(Apond, Fevap, Psi, Ksat, IMD)

    def _functional_init(self, A1, A2, A0, *args, **kwargs):
        """
        for storage type ``'FUNCTIONAL'``

        Args:
            A1 (float): coefficient of FUNCTIONAL relation between surface area and depth.
            A2 (float): exponent of FUNCTIONAL relation between surface area and depth.
            A0 (float): constant of FUNCTIONAL relation between surface area and depth.

            Apond (float): this parameter has been deprecated – use 0.
            Fevap (float): fraction of potential evaporation from surface realized (default is 0).
        """
        self.Curve = infer_type([A1, A2, A0])
        self._optional_args(*args, **kwargs)

    def _tabular_init(self, Curve, *args, **kwargs):
        """
        for storage type ``'TABULAR'``

        Args:
            Curve (str): name of curve in [CURVES] section with surface area (ft2 or m2)
                as a function of depth (ft or m) for TABULAR geometry.
            Apond (float): this parameter has been deprecated – use 0.
            Fevap (float): fraction of potential evaporation from surface realized (default is 0).
        """
        self.Curve = Curve
        self._optional_args(*args, **kwargs)

    def _optional_args(self, Apond=0, Fevap=0, *exfiltration_args, **exfiltration_kwargs):
        """
        for the optional arguemts

        Args:
            Apond (float): this parameter has been deprecated – use 0.
            Fevap (float): fraction of potential evaporation from surface realized (default is 0).
        """
        self.Apond = float(Apond)
        self.Fevap = float(Fevap)
        self._exfiltration_args(*exfiltration_args, **exfiltration_kwargs)

    def _exfiltration_args(self, Psi=NaN, Ksat=NaN, IMD=NaN):
        """
        for the optional arguemts

        Args:
            Psi (float): soil suction head (inches or mm).
            Ksat (float): soil saturated hydraulic conductivity (in/hr or mm/hr).
            IMD (float): soil initial moisture deficit (fraction).
        """
        self.Psi = float(Psi)
        self.Ksat = float(Ksat)
        self.IMD = float(IMD)
