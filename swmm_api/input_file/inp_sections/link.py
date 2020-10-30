from numpy import NaN, isnan

from .identifiers import IDENTIFIERS
from ..inp_helpers import BaseSectionObject


class Conduit(BaseSectionObject):
    """Section: **[CONDUITS]**

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
            offset of downstream end of conduit invert above the invert elevation of its downstream node (ft
            or m).
        Q0
            flow in conduit at start of simulation (flow units) (default is 0).
        Qmax
            maximum flow allowed in the conduit (flow units) (default is no limit).

        These offsets are expressed as a relative distance above the node invert if the LINK_OFFSETS option
        is set to DEPTH (the default) or as an absolute elevation if it is set to ELEVATION.
    """
    identifier =IDENTIFIERS.Name

    def __init__(self, Name, FromNode, ToNode, Length, Roughness, InOffset, OutOffset, InitFlow=0, MaxFlow=NaN):
        """Identifies each conduit link of the drainage system.

        Conduits are pipes or channels that convey water from one node to another.

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
    """WEIRS

    Section:
        [WEIRS]

    Purpose:
        Identifies each weir link of the drainage system. Weirs are used to model flow
        diversions and storage node outlets.

    Format:
        Name Node1 Node2 Type CrestHt Cd (Gated EC Cd2 Sur (Width Surface))

    PC-SWMM Format:
        Name FromNode ToNode Type CrestHt Qcoeff Gated EndCon EndCoeff Surcharge RoadWidth RoadSurf

    Remarks:
        The geometry of a weir’s opening is described in the [XSECTIONS] section.
        The following shapes must be used with each type of weir:

        =============  ===================
        Weir Type      Cross-Section Shape
        =============  ===================
        Transverse     RECT_OPEN
        Sideflow       RECT_OPEN
        V-Notch        TRIANGULAR
        Trapezoidal    TRAPEZOIDAL
        Roadway        RECT_OPEN
        =============  ===================

        The ROADWAY weir is a broad crested rectangular weir used model roadway crossings usually in conjunction with
        culvert-type conduits. It uses the FHWA HDS-5 method to determine a discharge coefficient as a function of flow
        depth and roadway width and surface.
        If no roadway data are provided then the weir behaves as a TRANSVERSE weir with Cd as its discharge coefficient.
        Note that if roadway data are provided, then values for the other optional weir parameters
        (NO for Gated, 0 for EC, 0 for Cd2, and NO for Sur)
        must be entered even though they do not apply to ROADWAY weirs.
    """
    identifier =IDENTIFIERS.Name

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
        """Identifies each weir link of the drainage system.

        Weirs are used to model flow diversions and storage node outlets.

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
    """OUTLETS

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
    identifier =IDENTIFIERS.Name

    class Types:
        TABULAR_DEPTH = 'TABULAR/DEPTH'
        TABULAR_HEAD = 'TABULAR/HEAD'
        FUNCTIONAL_DEPTH = 'FUNCTIONAL/DEPTH'
        FUNCTIONAL_HEAD = 'FUNCTIONAL/HEAD'

    def __init__(self, Name, FromNode, ToNode, Offset, Type, *args, Curve=None, Gated=False):
        """Identifies each outlet flow control device of the drainage system.

        These devices are used to model outflows from storage units or flow diversions that have a user-defined
        relation between flow rate and water depth.

        Args:
            Name (str): name assigned to outlet link.
            FromNode (str): name of node on inlet end of link.
            ToNode (str): name of node on outflow end of link.
            Offset (float): amount that the outlet is offset above the invert of inlet node
                (ft or m, expressed as either a depth or as an elevation, depending on the LINK_OFFSETS option setting).
            Type (str): one of Outlet.Types
            *args: for automatic input file reading
            Curve (str | list[float]):
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
            Gated (bool): YES if flap gate present to prevent reverse flow, NO if not (default is NO).
        """
        self.Name = str(Name)

        self.FromNode = str(FromNode)
        self.ToNode = str(ToNode)
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
            self.Gated = bool(Gated)

    def _tabular_init(self, Qcurve, Gated=False):
        self.Curve = str(Qcurve)
        self.Gated = bool(Gated)

    def _functional_init(self, C1, C2, Gated=False):
        self.Curve = [float(C1), float(C2)]
        self.Gated = bool(Gated)


class Orifice(BaseSectionObject):
    """ORIFICES

    Section:
        [ORIFICES]

    Purpose:
        Identifies each orifice link of the drainage system. An orifice link serves to limit the
        flow exiting a node and is often used to model flow diversions and storage node
        outlets.

    Format:
        Name Node1 Node2 Type Offset Cd (Flap Orate)

    The geometry of an orifice’s opening must be described in the [XSECTIONS] section.
    The only allowable shapes are CIRCULAR and RECT_CLOSED (closed rectangular).
    """
    identifier =IDENTIFIERS.Name

    class Types:
        SIDE = 'SIDE'
        BOTTOM = 'BOTTOM'

    def __init__(self, Name, FromNode, ToNode, Type, Offset, Qcoeff, FlapGate=False, Orate=0):
        """Identifies each orifice link of the drainage system.

        An orifice link serves to limit the flow exiting a node and
        is often used to model flow diversions and storage node outlets.

        Args:
            Name (str): name assigned to orifice link.
            FromNode (str): (Node1) name of node on inlet end of orifice.
            ToNode (str): (Node2) name of node on outlet end of orifice.
            Type (str): orientation of orifice: either SIDE or BOTTOM.
            Offset (float): amount that a Side Orifice’s bottom or the position of a Bottom Orifice is offset above
            the invert
                        of inlet node (ft or m, expressed as either a depth or as an elevation,
                        depending on the LINK_OFFSETS option setting).
            Qcoeff (float): (Cd) discharge coefficient (unitless).
            FlapGate (bool): YES if flap gate present to prevent reverse flow, NO if not (default is NO).
            Orate (int): time in decimal hours to open a fully closed orifice (or close a fully open one).
                            Use 0 if the orifice can open/close instantaneously.
        """
        self.Name = str(Name)
        self.FromNode = str(FromNode)
        self.ToNode = str(ToNode)
        self.Type = Type
        self.Offset = Offset
        self.Qcoeff = Qcoeff
        self.FlapGate = FlapGate
        self.Orate = Orate


class Pump(BaseSectionObject):
    """PUMPS

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
    identifier =IDENTIFIERS.Name

    class States:
        ON = 'ON'
        OFF = 'OFF'

    def __init__(self, Name, FromNode, ToNode, Curve, Status='ON', Startup=0, Shutoff=0):
        """Identifies each pump link of the drainage system.

        Args:
            Name (str): name assigned to pump link.
            FromNode (str): name of node on inlet side of pump.
            ToNode (str): name of node on outlet side of pump.
            Curve (str): name of pump curve listed in the [CURVES] section of the input.
            Status (str): status at start of simulation (either ON or OFF; default is ON).
            Startup (float): depth at inlet node when pump turns on (ft or m) (default is 0).
            Shutoff (float): depth at inlet node when pump shuts off (ft or m) (default is 0).
        """
        self.Name = str(Name)
        self.FromNode = str(FromNode)
        self.ToNode = str(ToNode)
        self.Curve = str(Curve)
        self.Status = str(Status)
        self.Startup = float(Startup)
        self.Shutoff = float(Shutoff)
