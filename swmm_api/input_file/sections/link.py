from numpy import NaN, isnan

from ._identifiers import IDENTIFIERS
from ..helpers import BaseSectionObject
from .._type_converter import to_bool
from ..section_labels import CONDUITS, ORIFICES, OUTLETS, PUMPS, WEIRS


class _Link(BaseSectionObject):
    _identifier = IDENTIFIERS.name

    def __init__(self, name, from_node, to_node):
        self.name = str(name)
        self.from_node = str(from_node)
        self.to_node = str(to_node)


class Conduit(_Link):
    """
    Conduit link information.

    Section:
        [CONDUITS]

    Purpose:
        Identifies each conduit link of the drainage system. Conduits are pipes or channels that convey water
        from one node to another.

    Notes:
        These offsets are expressed as a relative distance above the node invert if the ``LINK_OFFSETS`` option
        is set to ``DEPTH`` (the default) or as an absolute elevation if it is set to ``ELEVATION``.

    Attributes:
        name (str): Name assigned to conduit link.
        from_node (str): Name of upstream node.
        to_node (str): Name of downstream node.
        length (float): Conduit length (ft or m).
        roughness (float): Value of n (i.e., roughness parameter) in Manning’s equation.
        offset_upstream (float): offset of upstream end of conduit invert above the invert elevation of its
                                 upstream node (ft or m).
        offset_downstream (float): Offset of downstream end of conduit invert above the invert elevation of its
                                   downstream node (ft or m).
        flow_initial (float): Flow in conduit at start of simulation (flow units) (default is 0).
        flow_max (float): Maximum flow allowed in the conduit (flow units) (default is no limit | 0 = no limit).
    """
    _section_label = CONDUITS

    def __init__(self, name, from_node, to_node, length, roughness, offset_upstream=0, offset_downstream=0,
                 flow_initial=0, flow_max=NaN):
        """
        Conduit link information.

        Args:
            name (str): Name assigned to conduit link.
            from_node (str): Name of upstream node.
            to_node (str): Name of downstream node.
            length (float): Conduit length (ft or m).
            roughness (float): Value of n (i.e., roughness parameter) in Manning’s equation.
            offset_upstream (float): offset of upstream end of conduit invert above the invert elevation of its
                                     upstream node (ft or m).
            offset_downstream (float): Offset of downstream end of conduit invert above the invert elevation of its
                                       downstream node (ft or m).
            flow_initial (float): Flow in conduit at start of simulation (flow units) (default is 0).
            flow_max (float): Maximum flow allowed in the conduit (flow units) (default is no limit | 0 = no limit).
        """
        _Link.__init__(self, name, from_node, to_node)
        self.length = float(length)
        self.roughness = float(roughness)
        self.offset_upstream = float(offset_upstream)
        self.offset_downstream = float(offset_downstream)
        self.flow_initial = float(flow_initial)
        self.flow_max = float(flow_max)
        if self.flow_max == 0:
            self.flow_max = NaN


class Orifice(_Link):
    """
    Orifice link information.

    Section:
        [ORIFICES]

    Purpose:
        Identifies each orifice link of the drainage system. An orifice link serves to limit the
        flow exiting a node and is often used to model flow diversions and storage node outlets.

    Notes:
        The geometry of an orifice’s opening must be described in the [``XSECTIONS``] section.
        The only allowable shapes are CIRCULAR and RECT_CLOSED (closed rectangular).

    Attributes:
        name (str): Name assigned to orifice link.
        from_node (str): Name of node on inlet end of orifice.
        to_node (str): Name of node on outlet end of orifice.
        orientation (str): Orientation of orifice: either SIDE or BOTTOM.
        offset (float): Amount that a Side Orifice’s bottom or the position of a Bottom Orifice is offset above
                        the invert of inlet node (ft or m, expressed as either a depth or as an elevation,
                        depending on the LINK_OFFSETS option setting).
        discharge_coefficient (float): Discharge coefficient (unitless).
        has_flap_gate (bool): ``YES`` (:obj:`True`) if flap gate present to prevent reverse flow,
                              ``NO`` (:obj:`False`) if not (default is ``NO``).
        hours_to_open (int): Time in decimal hours to open a fully closed orifice (or close a fully open one).
                             Use 0 if the orifice can open/close instantaneously.
    """
    _section_label = ORIFICES

    class ORIENTATION:
        """Orientation of orifice."""
        SIDE = 'SIDE'
        BOTTOM = 'BOTTOM'

    def __init__(self, name, from_node, to_node, orientation, offset, discharge_coefficient, has_flap_gate=False, hours_to_open=0):
        """
        Orifice link information.

        Args:
            name (str): Name assigned to orifice link.
            from_node (str): Name of node on inlet end of orifice.
            to_node (str): Name of node on outlet end of orifice.
            orientation (str): Orientation of orifice: either SIDE or BOTTOM.
            offset (float): Amount that a Side Orifice’s bottom or the position of a Bottom Orifice is offset above
                            the invert of inlet node (ft or m, expressed as either a depth or as an elevation,
                            depending on the LINK_OFFSETS option setting).
            discharge_coefficient (float): Discharge coefficient (unitless).
            has_flap_gate (bool): ``YES`` (:obj:`True`) if flap gate present to prevent reverse flow,
                                  ``NO`` (:obj:`False`) if not (default is ``NO``).
            hours_to_open (int): Time in decimal hours to open a fully closed orifice (or close a fully open one).
                                 Use 0 if the orifice can open/close instantaneously.
        """
        _Link.__init__(self, name, from_node, to_node)
        self.orientation = str(orientation)
        self.offset = float(offset)
        self.discharge_coefficient = float(discharge_coefficient)
        self.has_flap_gate = to_bool(has_flap_gate)
        self.hours_to_open = int(hours_to_open)


class Outlet(_Link):
    """
    Outlet link information.

    Section:
        [OUTLETS]

    Purpose:
        Identifies each outlet flow control device of the drainage system.
        These devices are used to model outflows from storage units or flow diversions
        that have a user-defined relation between flow rate and water depth.

    Attributes:
        name (str): Name assigned to outlet link.
        from_node (str): Name of node on inlet end of link.
        to_node (str): Name of node on outflow end of link.
        offset (float): Amount that the outlet is offset above the invert of inlet node
            (ft or m, expressed as either a depth or as an elevation, depending on the LINK_OFFSETS option setting).
        curve_type (str): One of :attr:`Outlet.TYPES`
        *args: Only for automatic input file reading ...
        curve_description (str | tuple[float, float]):

            - :obj:`str`: ``name_curve`` Name of the rating curve listed in the [``CURVES``] section that
                          describes outflow rate (flow units) as a function of:

                - water depth above the offset elevation at the inlet node (ft or m) for a TABULAR/DEPTH outlet.
                - head difference (ft or m) between the inlet and outflow nodes for a TABULAR/HEAD outlet.
            - :obj:`tuple[float, float]`: Coefficient and exponent, respectively, of a power
                                          function that relates outflow (Q) to:

                - water depth (ft or m) above the offset elevation at the inlet node for a FUNCTIONAL/DEPTH outlet.
                - head difference (ft or m) between the inlet and outflow nodes for a FUNCTIONAL/HEAD outlet.
                  (i.e., Q = C1H^C2 where H is either depth or head).

        has_flap_gate (bool): ``YES`` (:obj:`True`) if flap gate present to prevent reverse flow,
                              ``NO`` (:obj:`False`) if not (default is ``NO``).
    """
    _section_label = OUTLETS

    class TYPES:
        """Outlet flow rate."""
        TABULAR_DEPTH = 'TABULAR/DEPTH'
        TABULAR_HEAD = 'TABULAR/HEAD'
        FUNCTIONAL_DEPTH = 'FUNCTIONAL/DEPTH'
        FUNCTIONAL_HEAD = 'FUNCTIONAL/HEAD'

    def __init__(self, name, from_node, to_node, offset, curve_type, *args, curve_description=None, has_flap_gate=False):
        """
        Outlet link information.

        Args:
            name (str): Name assigned to outlet link.
            from_node (str): Name of node on inlet end of link.
            to_node (str): Name of node on outflow end of link.
            offset (float): Amount that the outlet is offset above the invert of inlet node
                (ft or m, expressed as either a depth or as an elevation, depending on the LINK_OFFSETS option setting).
            curve_type (str): One of :attr:`Outlet.TYPES`
            *args: Only for automatic input file reading ...
            curve_description (str | tuple[float, float]):

                - :obj:`str`: ``name_curve`` Name of the rating curve listed in the [``CURVES``] section that
                              describes outflow rate (flow units) as a function of:

                    - water depth above the offset elevation at the inlet node (ft or m) for a TABULAR/DEPTH outlet.
                    - head difference (ft or m) between the inlet and outflow nodes for a TABULAR/HEAD outlet.
                - :obj:`tuple[float, float]`: Coefficient and exponent, respectively, of a power
                                              function that relates outflow (Q) to:

                    - water depth (ft or m) above the offset elevation at the inlet node for a FUNCTIONAL/DEPTH outlet.
                    - head difference (ft or m) between the inlet and outflow nodes for a FUNCTIONAL/HEAD outlet.
                      (i.e., Q = C1H^C2 where H is either depth or head).

            has_flap_gate (bool): ``YES`` (:obj:`True`) if flap gate present to prevent reverse flow,
                                  ``NO`` (:obj:`False`) if not (default is ``NO``).
        """
        _Link.__init__(self, name, from_node, to_node)
        self.offset = float(offset)
        self.curve_type = str(curve_type).upper()

        if args:
            if self.curve_type.startswith('TABULAR'):
                self._tabular_init(*args)
            elif self.curve_type.startswith('FUNCTIONAL'):
                self._functional_init(*args)
            else:
                raise NotImplementedError(f'Type: "{self.curve_type}" is not implemented')

        else:
            self.curve_description = curve_description
            self.has_flap_gate = to_bool(has_flap_gate)

    def _tabular_init(self, name_curve, has_flap_gate=False):
        """
        Init for object which describes the outflow rate (flow units) as a rating curve.

        Args:
            name_curve (str): Name of the rating curve listed in the [``CURVES``] section that describes
                              outflow rate (flow units) as a function of:

                - water depth above the offset elevation at the inlet node (ft or m) for a TABULAR/DEPTH outlet.
                - head difference (ft or m) between the inlet and outflow nodes for a TABULAR/HEAD outlet.
            has_flap_gate (bool): ``YES`` (:obj:`True`) if flap gate present to prevent reverse flow,
                                  ``NO`` (:obj:`False`) if not (default is ``NO``).
        """
        self.curve_description = str(name_curve)
        self.has_flap_gate = to_bool(has_flap_gate)

    def _functional_init(self, coefficient, exponent, has_flap_gate=False):
        """
        Init for object which describes the outflow rate (flow units) as a function.

        Q = coefficient * H^exponent

        where H is either:

            - water depth (ft or m) above the offset elevation at the inlet node for a FUNCTIONAL/DEPTH outlet.
            - head difference (ft or m) between the inlet and outflow nodes for a FUNCTIONAL/HEAD outlet.

        Args:
            coefficient (float): Coefficient of a power function.
            exponent (float): Exponent of a power function.
            has_flap_gate (bool): ``YES`` (:obj:`True`) if flap gate present to prevent reverse flow,
                                  ``NO`` (:obj:`False`) if not (default is ``NO``).
        """
        self.curve_description = [float(coefficient), float(exponent)]
        self.has_flap_gate = to_bool(has_flap_gate)


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

    Attributes:
        name (str): name assigned to pump link.
        from_node (str): name of node on inlet side of pump. ``Node1``
        to_node (str): name of node on outlet side of pump. ``Node2``
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

    def __init__(self, name, from_node, to_node, Curve, Status='ON', Startup=0, Shutoff=0):
        """
        Pump

        Args:
            name (str): name assigned to pump link.
            from_node (str): name of node on inlet side of pump. ``Node1``
            to_node (str): name of node on outlet side of pump. ``Node2``
            Curve (str): name of pump curve listed in the [CURVES] section of the input. ``Pcurve``
            Status (str): status at start of simulation (either ON or OFF; default is ON).
            Startup (float): depth at inlet node when pump turns on (ft or m) (default is 0).
            Shutoff (float): depth at inlet node when pump shuts off (ft or m) (default is 0).
        """
        _Link.__init__(self, name, from_node, to_node)
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
        ``Name InletNode OutletNode WeirType CrestHeight DischCoeff FlapGate EndCon EndCoeff Surcharge RoadWidth
        RoadSurf``

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

        The ``ROADWAY`` weir is a broad crested rectangular weir used model roadway crossings usually in conjunction
        with
        culvert-type conduits. It uses the FHWA HDS-5 method to determine a discharge coefficient as a function of flow
        depth and roadway width and surface.
        If no roadway data are provided then the weir behaves as a ``TRANSVERSE`` weir with Cd as its discharge
        coefficient.
        Note that if roadway data are provided, then values for the other optional weir parameters
        (``NO`` for Gated, 0 for EC, 0 for Cd2, and ``NO`` for Sur)
        must be entered even though they do not apply to ``ROADWAY`` weirs.

    Attributes:
        name (str): name assigned to weir link
        from_node (str): name of node on inlet side of weir. ``Node1``
        to_node (str): name of node on outlet side of weir. ``Node2``
        Type (str): ``TRANSVERSE``, ``SIDEFLOW``, ``V-NOTCH``, ``TRAPEZOIDAL`` or ``ROADWAY``.
        CrestHeight (float): amount that the weir’s crest is offset above the invert of inlet node (ft or m,
            expressed as either a depth or as an elevation, depending on the LINK_OFFSETS option setting). ``CrestHt``
        Qcoeff (float): weir discharge coefficient (for CFS if using US flow units or CMS if using metric flow
        units). ``Cd``
        FlapGate (bool): ``YES`` if flap gate present to prevent reverse flow, ``NO`` if not (default is ``NO``).
        ``Gated``
        EndContractions (float): number of end contractions for ``TRANSVERSE`` or ``TRAPEZOIDAL`` weir (default is
        0). ``EC``
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

    def __init__(self, name, from_node, to_node, Type, CrestHeight, Qcoeff, FlapGate=False, EndContractions=0,
                 EndCoeff=NaN, Surcharge=True, RoadWidth=NaN, RoadSurface=NaN):
        """
        Weir.

        Args:
            name (str): name assigned to weir link
            from_node (str): name of node on inlet side of weir. ``Node1``
            to_node (str): name of node on outlet side of weir. ``Node2``
            Type (str): ``TRANSVERSE``, ``SIDEFLOW``, ``V-NOTCH``, ``TRAPEZOIDAL`` or ``ROADWAY``.
            CrestHeight (float): amount that the weir’s crest is offset above the invert of inlet node (ft or m,
                expressed as either a depth or as an elevation, depending on the LINK_OFFSETS option setting). ``CrestHt``
            Qcoeff (float): weir discharge coefficient (for CFS if using US flow units or CMS if using metric flow
            units). ``Cd``
            FlapGate (bool): ``YES`` if flap gate present to prevent reverse flow, ``NO`` if not (default is ``NO``).
            ``Gated``
            EndContractions (float): number of end contractions for ``TRANSVERSE`` or ``TRAPEZOIDAL`` weir (default is
            0). ``EC``
            EndCoeff (float): discharge coefficient for triangular ends of a ``TRAPEZOIDAL`` weir
                             (for ``CFS`` if using US flow units or ``CMS`` if using metric flow units)
                             (default is value of Cd). ``Cd2``
            Surcharge (bool): ``YES`` if the weir can surcharge
                (have an upstream water level higher than the height of the opening);
                ``NO`` if it cannot (default is ``YES``). ``Sur``
            RoadWidth (float): width of road lanes and shoulders for ``ROADWAY`` weir (ft or m). ``Width``
            RoadSurface (str): type of road surface for ``ROADWAY`` weir: ``PAVED`` or ``GRAVEL``. ``Surface``
        """
        _Link.__init__(self, name, from_node, to_node)
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
