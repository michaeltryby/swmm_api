from numpy import NaN, isnan

from ._identifiers import IDENTIFIERS
from ..helpers import BaseSectionObject
from .._type_converter import to_bool
from ..section_labels import CONDUITS, ORIFICES, OUTLETS, PUMPS, WEIRS


class _Link(BaseSectionObject):
    _identifier = IDENTIFIERS.Name

    def __init__(self, Name, FromNode, ToNode):
        self.Name = str(Name)
        self.FromNode = str(FromNode)
        self.ToNode = str(ToNode)


class Conduit(_Link):
    """Section: **[CONDUITS]**

    Purpose:
        Identifies each conduit link of the drainage system. Conduits are pipes or channels that convey water
        from one node to another.

    Format:
        ::

            Name  Node1  Node2  Length  N  Z1  Z2  (Q0  Qmax)

    Format-PCSWMM:
        ``Name InletNode OutletNode Length ManningN InletOffset OutletOffset InitFlow MaxFlow``

    Format-SWMM-GUI:
        ``Name FromNode ToNode Length Roughness InOffset OutOffset InitFlow MaxFlow``

    Remarks:
        These offsets are expressed as a relative distance above the node invert if the ``LINK_OFFSETS`` option
        is set to ``DEPTH`` (the default) or as an absolute elevation if it is set to ``ELEVATION``.

    Args:
        Name (str): name assigned to conduit link.
        FromNode (str): name of upstream node. ``Node1``
        ToNode (str): name of downstream node. ``Node2``
        Length (float): conduit length (ft or m).
        Roughness (float): value of n (i.e., roughness parameter) in Manning’s equation. ``N``
        InOffset (float): offset of upstream end of conduit invert above the invert elevation of its
                          upstream node (ft or m). ``Z1``
        OutOffset (float): offset of downstream end of conduit invert above the invert elevation of its
                          downstream node (ft or m). ``Z2``
        InitFlow (float): flow in conduit at start of simulation (flow units) (default is 0). ``Q0``
        MaxFlow (float): maximum flow allowed in the conduit (flow units) (default is no limit | 0 = no limit). ``Qmax``

    Attributes:
        Name (str): name assigned to conduit link.
        FromNode (str): name of upstream node. ``Node1``
        ToNode (str): name of downstream node. ``Node2``
        Length (float): conduit length (ft or m).
        Roughness (float): value of n (i.e., roughness parameter) in Manning’s equation. ``N``
        InOffset (float): offset of upstream end of conduit invert above the invert elevation of its
                          upstream node (ft or m). ``Z1``
        OutOffset (float): offset of downstream end of conduit invert above the invert elevation of its
                          downstream node (ft or m). ``Z2``
        InitFlow (float): flow in conduit at start of simulation (flow units) (default is 0). ``Q0``
        MaxFlow (float): maximum flow allowed in the conduit (flow units) (default is no limit | 0 = no limit). ``Qmax``
    """
    _section_label = CONDUITS

    def __init__(self, Name, FromNode, ToNode, Length, Roughness, InOffset=0, OutOffset=0, InitFlow=0, MaxFlow=NaN):
        _Link.__init__(self, Name, FromNode, ToNode)
        self.Length = float(Length)
        self.Roughness = float(Roughness)
        self.InOffset = float(InOffset)
        self.OutOffset = float(OutOffset)
        self.InitFlow = float(InitFlow)
        self.MaxFlow = float(MaxFlow)
        if self.MaxFlow == 0:
            self.MaxFlow = NaN


class Orifice(_Link):
    """
    Section: [**ORIFICES**]

    Purpose:
        Identifies each orifice link of the drainage system. An orifice link serves to limit the
        flow exiting a node and is often used to model flow diversions and storage node
        outlets.

    Format:
        ::

            Name Node1 Node2 Type Offset Cd (Flap Orate)

    Format-PCSWMM:
        ``Name  InletNode  OutletNode  OrificeType  CrestHeight  DischCoeff  FlapGate  Open/CloseTime``

    Format-SWMM-GUI:
        ``Name  FromNode  ToNode  Type  Offset  Qcoeff  Gated  CloseTime``

    Remarks:
        The geometry of an orifice’s opening must be described in the [``XSECTIONS``] section.
        The only allowable shapes are CIRCULAR and RECT_CLOSED (closed rectangular).

    Args:
        Name (str): name assigned to orifice link.
        FromNode (str): name of node on inlet end of orifice. ``Node1``
        ToNode (str): name of node on outlet end of orifice. ``Node2``
        Type (str): orientation of orifice: either SIDE or BOTTOM.
        Offset (float): amount that a Side Orifice’s bottom or the position of a Bottom Orifice is offset above
            the invert of inlet node (ft or m, expressed as either a depth or as an elevation,
            depending on the LINK_OFFSETS option setting).
        Qcoeff (float): discharge coefficient (unitless). ``Cd``
        FlapGate (bool): YES if flap gate present to prevent reverse flow, NO if not (default is NO). ``Flap``
        Orate (int): time in decimal hours to open a fully closed orifice (or close a fully open one).
                        Use 0 if the orifice can open/close instantaneously.

    Attributes:
        Name (str): name assigned to orifice link.
        FromNode (str): name of node on inlet end of orifice. ``Node1``
        ToNode (str): name of node on outlet end of orifice. ``Node2``
        Type (str): orientation of orifice: either SIDE or BOTTOM.
        Offset (float): amount that a Side Orifice’s bottom or the position of a Bottom Orifice is offset above
            the invert of inlet node (ft or m, expressed as either a depth or as an elevation,
            depending on the LINK_OFFSETS option setting).
        Qcoeff (float): discharge coefficient (unitless). ``Cd``
        FlapGate (bool): YES if flap gate present to prevent reverse flow, NO if not (default is NO). ``Flap``
        Orate (int): time in decimal hours to open a fully closed orifice (or close a fully open one).
                        Use 0 if the orifice can open/close instantaneously.
    """
    _section_label = ORIFICES

    class TYPES:
        """orientation of orifice: either SIDE or BOTTOM"""
        SIDE = 'SIDE'
        BOTTOM = 'BOTTOM'

    def __init__(self, Name, FromNode, ToNode, Type, Offset, Qcoeff, FlapGate=False, Orate=0):
        _Link.__init__(self, Name, FromNode, ToNode)
        self.Type = str(Type)
        self.Offset = float(Offset)
        self.Qcoeff = float(Qcoeff)
        self.FlapGate = to_bool(FlapGate)
        self.Orate = int(Orate)


class Outlet(_Link):
    """
    Section: [**OUTLETS**]

    Purpose:
        Identifies each outlet flow control device of the drainage system.
        These devices are used to model outflows from storage units or flow diversions
        that have a user-defined relation between flow rate and water depth.

    Formats:
        ::

            Name Node1 Node2 Offset TABULAR/DEPTH Qcurve (Gated)
            Name Node1 Node2 Offset TABULAR/HEAD Qcurve (Gated)
            Name Node1 Node2 Offset FUNCTIONAL/DEPTH C1 C2 (Gated)
            Name Node1 Node2 Offset FUNCTIONAL/HEAD C1 C2 (Gated)

    Format-PCSWMM:
        ``Name InletNode OutletNode OutflowHeight OutletType Qcoeff/QTable Qexpon FlapGate``

    Format-SWMM-GUI:
        ``Name FromNode ToNode Offset Type QTable/Qcoeff Qexpon Gated``

    Args:
        Name (str): name assigned to outlet link.
        FromNode (str): name of node on inlet end of link. ``Node1``
        ToNode (str): name of node on outflow end of link. ``Node2``
        Offset (float): amount that the outlet is offset above the invert of inlet node
            (ft or m, expressed as either a depth or as an elevation, depending on the LINK_OFFSETS option setting).
        Type (str): one of Outlet.Types
        *args: for automatic input file reading
        Curve (str | tuple[float, float]):

            - :obj:`float`: ``Qcurve`` name of the rating curve listed in the [``CURVES``] section that describes outflow rate (flow units) as a function of:

                    - water depth above the offset elevation at the inlet node (ft or m) for a TABULAR/DEPTH outlet
                    - head difference (ft or m) between the inlet and outflow nodes for a TABULAR/HEAD outlet.
            - :obj:`tuple[float, float]`: (``C1``, ``C2``) coefficient and exponent, respectively, of a power function that relates outflow (Q) to:

                    - water depth (ft or m) above the offset elevation at the inlet node for a FUNCTIONAL/DEPTH outlet
                    - head difference (ft or m) between the inlet and outflow nodes for a FUNCTIONAL/HEAD outlet.
                      (i.e., Q = C1H^C2 where H is either depth or head).

        Gated (bool): ``YES`` if flap gate present to prevent reverse flow, ``NO`` if not (default is ``NO``).

    Attributes:
        Name (str): name assigned to outlet link.
        FromNode (str): name of node on inlet end of link. ``Node1``
        ToNode (str): name of node on outflow end of link. ``Node2``
        Offset (float): amount that the outlet is offset above the invert of inlet node
            (ft or m, expressed as either a depth or as an elevation, depending on the LINK_OFFSETS option setting).
        Type (str): one of Outlet.Types
        Curve (str | tuple[float, float]):

            - :obj:`float`: ``Qcurve`` name of the rating curve listed in the [``CURVES``] section that describes outflow rate (flow units) as a function of:

                    - water depth above the offset elevation at the inlet node (ft or m) for a TABULAR/DEPTH outlet
                    - head difference (ft or m) between the inlet and outflow nodes for a TABULAR/HEAD outlet.
            - :obj:`tuple[float, float]`: (``C1``, ``C2``) coefficient and exponent, respectively, of a power function that relates outflow (Q) to:

                    - water depth (ft or m) above the offset elevation at the inlet node for a FUNCTIONAL/DEPTH outlet
                    - head difference (ft or m) between the inlet and outflow nodes for a FUNCTIONAL/HEAD outlet.
                      (i.e., Q = C1H^C2 where H is either depth or head).

        Gated (bool): ``YES`` if flap gate present to prevent reverse flow, ``NO`` if not (default is ``NO``).
    """
    _section_label = OUTLETS

    class TYPES:
        TABULAR_DEPTH = 'TABULAR/DEPTH'
        TABULAR_HEAD = 'TABULAR/HEAD'
        FUNCTIONAL_DEPTH = 'FUNCTIONAL/DEPTH'
        FUNCTIONAL_HEAD = 'FUNCTIONAL/HEAD'

    def __init__(self, Name, FromNode, ToNode, Offset, Type, *args, Curve=None, Gated=False):
        _Link.__init__(self, Name, FromNode, ToNode)
        self.Offset = float(Offset)
        self.Type = str(Type)

        if args:
            if Type.startswith('TABULAR'):
                self._tabular_init(*args)

            elif Type.startswith('FUNCTIONAL'):
                self._functional_init(*args)

            else:
                raise NotImplementedError('Type: "{}" is not implemented'.format(Type))

        else:
            self.Curve = Curve
            self.Gated = to_bool(Gated)

    def _tabular_init(self, Qcurve, Gated=False):
        self.Curve = str(Qcurve)
        self.Gated = to_bool(Gated)

    def _functional_init(self, C1, C2, Gated=False):
        self.Curve = [float(C1), float(C2)]
        self.Gated = to_bool(Gated)


class Pump(_Link):
    """
    Section: [**PUMPS**]

    Purpose:
        Identifies each pump link of the drainage system.

    Format:
        ::

            Name Node1 Node2 Pcurve (Status Startup Shutoff)

    Format-PCSWMM:
        ``Name  InletNode  OutletNode  PumpCurve  InitStatus  StartupDepth  ShutoffDepth``

    Format-SWMM-GUI:
        ``Name  FromNode  ToNode  PumpCurve  Status  Sartup  Shutoff``

    Args:
        Name (str): name assigned to pump link.
        FromNode (str): name of node on inlet side of pump. ``Node1``
        ToNode (str): name of node on outlet side of pump. ``Node2``
        Curve (str): name of pump curve listed in the [CURVES] section of the input. ``Pcurve``
        Status (str): status at start of simulation (either ON or OFF; default is ON).
        Startup (float): depth at inlet node when pump turns on (ft or m) (default is 0).
        Shutoff (float): depth at inlet node when pump shuts off (ft or m) (default is 0).

    Attributes:
        Name (str): name assigned to pump link.
        FromNode (str): name of node on inlet side of pump. ``Node1``
        ToNode (str): name of node on outlet side of pump. ``Node2``
        Curve (str): name of pump curve listed in the [CURVES] section of the input. ``Pcurve``
        Status (str): status at start of simulation (either ON or OFF; default is ON).
        Startup (float): depth at inlet node when pump turns on (ft or m) (default is 0).
        Shutoff (float): depth at inlet node when pump shuts off (ft or m) (default is 0).

    See Section 3.2 for a description of the different types of pumps available.
    """
    _section_label = PUMPS

    class STATES:
        """status at start of simulation (either ON or OFF; default is ON)."""
        ON = 'ON'
        OFF = 'OFF'

    def __init__(self, Name, FromNode, ToNode, Curve, Status='ON', Startup=0, Shutoff=0):
        _Link.__init__(self, Name, FromNode, ToNode)
        self.Curve = str(Curve)
        self.Status = str(Status)
        self.Startup = float(Startup)
        self.Shutoff = float(Shutoff)


class Weir(_Link):
    """
    Section: [**WEIRS**]

    Purpose:
        Identifies each weir link of the drainage system. Weirs are used to model flow
        diversions and storage node outlets.

    Format:
        ::

            Name Node1 Node2 Type CrestHt Cd (Gated EC Cd2 Sur (Width Surface))

    Format-PCSWMM:
        ``Name InletNode OutletNode WeirType CrestHeight DischCoeff FlapGate EndCon EndCoeff Surcharge RoadWidth RoadSurf``

    Format-SWMM-GUI:
        ``Name FromNode ToNode Type CrestHt Qcoeff Gated EndCon EndCoeff Surcharge RoadWidth RoadSurf``

    Remarks:
        The geometry of a weir’s opening is described in the [XSECTIONS] section.
        The following shapes must be used with each type of weir:

        =============  ===================
        Weir Type      Cross-Section Shape
        =============  ===================
        Transverse     ``RECT_OPEN``
        Sideflow       ``RECT_OPEN``
        V-Notch        ``TRIANGULAR``
        Trapezoidal    ``TRAPEZOIDAL``
        Roadway        ``RECT_OPEN``
        =============  ===================

        The ``ROADWAY`` weir is a broad crested rectangular weir used model roadway crossings usually in conjunction with
        culvert-type conduits. It uses the FHWA HDS-5 method to determine a discharge coefficient as a function of flow
        depth and roadway width and surface.
        If no roadway data are provided then the weir behaves as a ``TRANSVERSE`` weir with Cd as its discharge coefficient.
        Note that if roadway data are provided, then values for the other optional weir parameters
        (``NO`` for Gated, 0 for EC, 0 for Cd2, and ``NO`` for Sur)
        must be entered even though they do not apply to ``ROADWAY`` weirs.

    Args:
        Name (str): name assigned to weir link
        FromNode (str): name of node on inlet side of weir. ``Node1``
        ToNode (str): name of node on outlet side of weir. ``Node2``
        Type (str): ``TRANSVERSE``, ``SIDEFLOW``, ``V-NOTCH``, ``TRAPEZOIDAL`` or ``ROADWAY``.
        CrestHeight (float): amount that the weir’s crest is offset above the invert of inlet node (ft or m,
            expressed as either a depth or as an elevation, depending on the LINK_OFFSETS option setting). ``CrestHt``
        Qcoeff (float): weir discharge coefficient (for CFS if using US flow units or CMS if using metric flow units). ``Cd``
        FlapGate (bool): ``YES`` if flap gate present to prevent reverse flow, ``NO`` if not (default is ``NO``). ``Gated``
        EndContractions (float): number of end contractions for ``TRANSVERSE`` or ``TRAPEZOIDAL`` weir (default is 0). ``EC``
        EndCoeff (float): discharge coefficient for triangular ends of a ``TRAPEZOIDAL`` weir
                         (for ``CFS`` if using US flow units or ``CMS`` if using metric flow units)
                         (default is value of Cd). ``Cd2``
        Surcharge (bool): ``YES`` if the weir can surcharge
            (have an upstream water level higher than the height of the opening);
            ``NO`` if it cannot (default is ``YES``). ``Sur``
        RoadWidth (float): width of road lanes and shoulders for ``ROADWAY`` weir (ft or m). ``Width``
        RoadSurface (str): type of road surface for ``ROADWAY`` weir: ``PAVED`` or ``GRAVEL``. ``Surface``

    Attributes:
        Name (str): name assigned to weir link
        FromNode (str): name of node on inlet side of weir. ``Node1``
        ToNode (str): name of node on outlet side of weir. ``Node2``
        Type (str): ``TRANSVERSE``, ``SIDEFLOW``, ``V-NOTCH``, ``TRAPEZOIDAL`` or ``ROADWAY``.
        CrestHeight (float): amount that the weir’s crest is offset above the invert of inlet node (ft or m,
            expressed as either a depth or as an elevation, depending on the LINK_OFFSETS option setting). ``CrestHt``
        Qcoeff (float): weir discharge coefficient (for CFS if using US flow units or CMS if using metric flow units). ``Cd``
        FlapGate (bool): ``YES`` if flap gate present to prevent reverse flow, ``NO`` if not (default is ``NO``). ``Gated``
        EndContractions (float): number of end contractions for ``TRANSVERSE`` or ``TRAPEZOIDAL`` weir (default is 0). ``EC``
        EndCoeff (float): discharge coefficient for triangular ends of a ``TRAPEZOIDAL`` weir
                         (for ``CFS`` if using US flow units or ``CMS`` if using metric flow units)
                         (default is value of Cd). ``Cd2``
        Surcharge (bool): ``YES`` if the weir can surcharge
            (have an upstream water level higher than the height of the opening);
            ``NO`` if it cannot (default is ``YES``). ``Sur``
        RoadWidth (float): width of road lanes and shoulders for ``ROADWAY`` weir (ft or m). ``Width``
        RoadSurface (str): type of road surface for ``ROADWAY`` weir: ``PAVED`` or ``GRAVEL``. ``Surface``
    """
    _section_label = WEIRS

    class TYPES:
        TRANSVERSE = 'TRANSVERSE'
        SIDEFLOW = 'SIDEFLOW'
        V_NOTCH = 'V-NOTCH'
        TRAPEZOIDAL = 'TRAPEZOIDAL'
        ROADWAY = 'ROADWAY'

    class ROADSURFACES:
        PAVED = 'PAVED'
        GRAVEL = 'GRAVEL'

    def __init__(self, Name, FromNode, ToNode, Type, CrestHeight, Qcoeff, FlapGate=False, EndContractions=0,
                 EndCoeff=NaN,
                 Surcharge=True, RoadWidth=NaN, RoadSurface=NaN):
        _Link.__init__(self, Name, FromNode, ToNode)
        self.Type = str(Type)
        self.CrestHeight = float(CrestHeight)
        self.Qcoeff = float(Qcoeff)
        self.FlapGate = to_bool(FlapGate)
        self.EndContractions = EndContractions
        if not isinstance(EndCoeff, str) and isnan(EndCoeff):
            EndCoeff = Qcoeff
        self.EndCoeff = float(EndCoeff)
        self.Surcharge = to_bool(Surcharge)
        self.RoadWidth = float(RoadWidth)
        self.RoadSurface = RoadSurface
