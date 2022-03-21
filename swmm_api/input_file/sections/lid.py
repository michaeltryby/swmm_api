from numpy import NaN

from ._identifiers import IDENTIFIERS
from ..helpers import BaseSectionObject
from ..section_labels import LID_USAGE, LID_CONTROLS


class LIDControl(BaseSectionObject):
    """
    Section: [**LID_CONTROLS**]

    Purpose:
        Defines scale-independent LID controls that can be deployed within subcatchments.

    Formats:
        ::

            Name SURFACE StorHt VegFrac Rough Slope Xslope
            Name SOIL Thick Por FC WP Ksat Kcoeff Suct
            Name PAVEMENT Thick Vratio FracImp Perm Vclog
            Name STORAGE Height Vratio Seepage Vclog
            Name DRAIN Coeff Expon Offset Delay
            Name DRAINMAT Thick Vratio Rough

    Attributes:
        Name (str):
            name assigned to LID process.
        lid_kind (str): - BC for bio-retention cell
                        - RG for rain garden; GR for green roof
                        - IT for infiltration trench
                        - PP for permeable pavement
                        - RB for rain barrel
                        - RD for rooftop disconnection
                        - VS for vegetative swale.

    Examples:
        ::

            ;A street planter with no drain
            Planter BC
            Planter SURFACE 6 0.3 0 0 0
            Planter SOIL 24 0.5 0.1 0.05 1.2 2.4
            Planter STORAGE 12 0.5 0.5 0

            ;A green roof with impermeable bottom
            GR1 BC
            GR1 SURFACE 3 0 0 0 0
            GR1 SOIL 3 0.5 0.1 0.05 1.2 2.4
            GR1 STORAGE 3 0.5 0 0
            GR1 DRAIN 5 0.5 0 0

            ;A rain barrel that drains 6 hours after rainfall ends
            RB12 RB
            RB12 STORAGE 36 0 0 0
            RB12 DRAIN 10 0.5 0 6

            ;A grass swale 24 in. high with 5:1 side slope
            Swale VS
            Swale SURFACE 24 0 0.2 3 5

    Remarks:
        The following table shows which layers are required (x) or are optional (o) for each type of LID process:

        +-----------------------+---------+----------+------+---------+-------+-----------+
        | LID Type              | Surface | Pavement | Soil | Storage | Drain | Drain Mat |
        +-----------------------+---------+----------+------+---------+-------+-----------+
        | Bio-Retention Cell    | x       |          | x    | x       | o     |           |
        +-----------------------+---------+----------+------+---------+-------+-----------+
        | Rain Garden           | x       |          | x    |         |       |           |
        +-----------------------+---------+----------+------+---------+-------+-----------+
        | Green Roof            | x       |          | x    |         |       | x         |
        +-----------------------+---------+----------+------+---------+-------+-----------+
        | Infiltration Trench   | x       |          |      | x       | o     |           |
        +-----------------------+---------+----------+------+---------+-------+-----------+
        | Permeable Pavement    | x       | x        | o    | x       | o     |           |
        +-----------------------+---------+----------+------+---------+-------+-----------+
        | Rain Barrel           |         |          |      | x       | x     |           |
        +-----------------------+---------+----------+------+---------+-------+-----------+
        | Rooftop Disconnection | x       |          |      |         | x     |           |
        +-----------------------+---------+----------+------+---------+-------+-----------+
        | Vegetative Swale      | x       |          |      |         |       |           |
        +-----------------------+---------+----------+------+---------+-------+-----------+


        The equation used to compute flow rate out of the underdrain per unit area of the LID (in in/hr or
        mm/hr) is q = C * (h - H_d) ^ n where q is outflow, h is height of stored water (inches or mm) and H d
        is the drain offset height. Note that the units of C depend on the unit system being used as well
        as the value assigned to n.

        The actual dimensions of an LID control are provided in the [LID_USAGE] section when it is
        placed in a particular subcatchment.
    """
    _identifier = (IDENTIFIERS.Name, 'lid_kind')
    _section_label = LID_CONTROLS
    _table_inp_export = False

    class LID_TYPES:
        BC = 'BC'  # for bio-retention cell
        RG = 'RG'  # for rain garden
        GR = 'GR'  # for green roof
        IT = 'IT'  # for infiltration trench
        PP = 'PP'  # for permeable pavement
        RB = 'RB'  # for rain barrel
        RD = 'RD'  # for rooftop disconnection
        VS = 'VS'  # for vegetative swale.

        _possible = [BC, RG, GR, IT, PP, RB, RD, VS]

    def __init__(self, Name, lid_kind, layer_dict=None):
        """
        Create LID_CONTROLS object

        Args:
            Name (str):
            name assigned to LID process.
        lid_kind (str): - BC for bio-retention cell
                        - RG for rain garden; GR for green roof
                        - IT for infiltration trench
                        - PP for permeable pavement
                        - RB for rain barrel
                        - RD for rooftop disconnection
                        - VS for vegetative swale.
            layer_dict (dict[str, LIDControl.LAYER_TYPES.Surface]): dict of used layers in control
        """
        self.Name = str(Name)
        self.lid_kind = lid_kind.upper()  # one of LID_TYPES
        self.layer_dict = {} if layer_dict is None else layer_dict

    @classmethod
    def _convert_lines(cls, multi_line_args):
        last = None

        for name, *line in multi_line_args:
            # ---------------------------------
            if line[0].upper() in cls.LID_TYPES._possible:
                if last is not None:
                    yield last
                last = cls(name, lid_kind=line[0].upper())
            elif name == last.Name:
                surface_kind = line.pop(0).upper()  # one of SURFACE_TYPES
                last.layer_dict[surface_kind] = cls.LAYER_TYPES._dict[surface_kind](*line)
        yield last

    class LAYER_TYPES:
        class Surface(BaseSectionObject):
            _LABEL = 'SURFACE'

            def __init__(self, StorHt, VegFrac, Rough, Slope, Xslope):
                """
                Args:
                    StorHt (float): when confining walls or berms are present this is the maximum depth to which water can
                        pond above the surface of the unit before overflow occurs (in inches or mm). For LIDs that
                        experience overland flow it is the height of any surface depression storage.
                        For swales, it is the height of its trapezoidal cross section.
                    VegFrac (float): fraction of the surface storage volume that is filled with vegetation.
                    Rough (float): Manning's n for overland flow over surface soil cover, pavement, roof surface or a
                        vegetative swale. Use 0 for other types of LIDs.
                    Slope (float): slope of a roof surface, pavement surface or vegetative swale (percent).
                        Use 0 for other types of LIDs.
                    Xslope (float): slope (run over rise) of the side walls of a vegetative swale's cross section.
                        Use 0 for other types of LIDs.

                Remarks:
                    If either Rough or Slope values are 0 then any ponded water that exceeds the
                    surface storage depth is assumed to completely overflow the LID control within a
                    single time step.
                """
                self.StorHt = float(StorHt)
                self.VegFrac = float(VegFrac)
                self.Rough = float(Rough)
                self.Slope = float(Slope)
                self.Xslope = float(Xslope)

        class Soil(BaseSectionObject):
            _LABEL = 'SOIL'

            def __init__(self, Thick, Por, FC, WP, Ksat, Kcoeff, Suct):
                """
                Args:
                    Thick (float): thickness of the soil layer (inches or mm).
                    Por (float): soil porosity (volume of pore space relative to total volume).
                    FC (float): soil field capacity (volume of pore water relative to total volume after the
                        soil has been allowed to drain fully).
                    WP (float): soil wilting point (volume of pore water relative to total volume for a well
                        dried soil where only bound water remains).
                    Ksat (float): soil’s saturated hydraulic conductivity (in/hr or mm/hr).
                    Kcoeff (float): slope of the curve of log(conductivity) versus soil moisture content
                        (dimensionless).
                    Suct (float): soil capillary suction (in or mm).
                """
                self.Thick = float(Thick)
                self.Por = float(Por)
                self.FC = float(FC)
                self.WP = float(WP)
                self.Ksat = float(Ksat)
                self.Kcoeff = float(Kcoeff)
                self.Suct = float(Suct)

        class Pavement(BaseSectionObject):
            _LABEL = 'PAVEMENT'

            def __init__(self, Thick, Vratio, FracImp, Perm, Vclog, regeneration_interval=NaN, regeneration_fraction=NaN):
                """
                Args:
                    Thick (float): thickness of the pavement layer (inches or mm).
                    Vratio (float): void ratio (volume of void space relative to the volume of solids in the
                        pavement for continuous systems or for the fill material used in modular
                        systems). Note that porosity = void ratio / (1 + void ratio).

                    FracImp (float): ratio of impervious paver material to total area for modular systems; 0 for
                        continuous porous pavement systems.
                    Perm (float): permeability of the concrete or asphalt used in continuous systems or
                        hydraulic conductivity of the fill material (gravel or sand) used in modular
                        systems (in/hr or mm/hr).
                    Vclog (float): number of pavement layer void volumes of runoff treated it takes to
                        completely clog the pavement. Use a value of 0 to ignore clogging.
                """
                self.Thick = float(Thick)
                self.Vratio = float(Vratio)
                self.FracImp = float(FracImp)
                self.Perm = float(Perm)
                self.Vclog = Vclog  # acc. to documentation
                # self.clogging_factor = float(clogging_factor)
                self.regeneration_interval = float(regeneration_interval)
                self.regeneration_fraction = float(regeneration_fraction)

        class Storage(BaseSectionObject):
            _LABEL = 'STORAGE'

            def __init__(self, Height, Vratio, Seepage, Vclog):
                """
                Args:
                    Height (float): thickness of the storage layer or height of a rain barrel (inches or mm).
                    Vratio (float): void ratio (volume of void space relative to the volume of solids in the
                        layer). Note that porosity = void ratio / (1 + void ratio).
                    Seepage (float): the rate at which water seeps from the layer into the underlying native
                        soil when first constructed (in/hr or mm/hr). If there is an impermeable
                        floor or liner below the layer then use a value of 0.
                    Vclog (int): number of storage layer void volumes of runoff treated it takes to
                        completely clog the layer. Use a value of 0 to ignore clogging.

                Remarks:
                    Values for Vratio, Seepage, and Vclog are ignored for rain barrels.
                """
                self.Height = float(Height)
                self.Vratio = float(Vratio)
                self.Seepage = float(Seepage)
                self.Vclog = int(Vclog)

        class Drain(BaseSectionObject):
            _LABEL = 'DRAIN'

            def __init__(self, Coeff, Expon, Offset, Delay, open_level=NaN, close_level=NaN):
                """
                Args:
                    Coeff (float): coefficient C that determines the rate of flow through the drain as a
                        function of height of stored water above the drain bottom. For Rooftop
                        Disconnection it is the maximum flow rate (in inches/hour or mm/hour)
                        that the roof’s gutters and downspouts can handle before overflowing.
                    Expon (float): exponent n that determines the rate of flow through the drain as a
                        function of height of stored water above the drain outlet.
                    Offset (float): height of the drain line above the bottom of the storage layer or rain
                        barrel (inches or mm).
                    Delay: number of dry weather hours that must elapse before the drain line in a
                        rain barrel is opened (the line is assumed to be closed once rainfall
                        begins). A value of 0 signifies that the barrel's drain line is always open
                        and drains continuously. This parameter is ignored for other types of
                        LIDs.
                """
                self.Coeff = float(Coeff)
                self.Expon = float(Expon)
                self.Offset = float(Offset)
                self.Delay = Delay  # acc. to documentation  / for Rain Barrels only
                # self.open_level = open_level  # to in documentation
                # self.close_level = close_level  # to in documentation

        class Drainmat(BaseSectionObject):
            _LABEL = 'DRAINMAT'

            def __init__(self, Thick, Vratio, Rough):
                """
                Args:
                    Thick (float): thickness of the drainage mat (inches or mm).
                    Vratio (float): ratio of void volume to total volume in the mat.
                    Rough (float): Manning's n constant used to compute the horizontal flow rate of drained water through the mat.
                """
                self.Thick = float(Thick)
                self.Vratio = float(Vratio)
                self.Rough = float(Rough)

        SURFACE = Surface._LABEL
        SOIL = Soil._LABEL
        PAVEMENT = Pavement._LABEL
        STORAGE = Storage._LABEL
        DRAIN = Drain._LABEL
        DRAINMAT = Drainmat._LABEL

        _possible = [SURFACE, SOIL, PAVEMENT, STORAGE, DRAIN, DRAINMAT]

        _dict = {x._LABEL: x for x in (Surface, Soil, Pavement, Storage, Drain, Drainmat)}

    def to_inp_line(self):
        s = '{} {}\n'.format(self.Name, self.lid_kind)
        for layer, l in self.layer_dict.items():
            s += '{} {:<8} '.format(self.Name, layer) + l.to_inp_line() + '\n'
        return s


class LIDUsage(BaseSectionObject):
    """
    Section: [**LID_USAGE**]

    Purpose:
        Deploys LID controls within specific subcatchment areas.

    Formats:
        ::

            Subcat LID Number Area Width InitSat FromImp ToPerv (RptFile DrainTo)

    Args:
        Subcat (str): name of the subcatchment using the LID process.
        LID (str): name of an LID process defined in the [LID_CONTROLS] section.
        Number (int): number of replicate LID units deployed.
        Area (float): area of each replicate unit (ft^2 or m^2 ).
        Width (float): width of the outflow face of each identical LID unit (in ft or m). This
            parameter applies to roofs, pavement, trenches, and swales that use
            overland flow to convey surface runoff off of the unit. It can be set to 0 for
            other LID processes, such as bio-retention cells, rain gardens, and rain
            barrels that simply spill any excess captured runoff over their berms.
        InitSat (float): for bio-retention cells, rain gardens, and green roofs this is the degree to
            which the unit's soil is initially filled with water (0 % saturation
            corresponds to the wilting point moisture content, 100 % saturation has
            the moisture content equal to the porosity). The storage zone beneath
            the soil zone of the cell is assumed to be completely dry. For other types
            of LIDs it corresponds to the degree to which their storage zone is
            initially filled with water
        FromImp (float): percent of the impervious portion of the subcatchment’s non-LID area
            whose runoff is treated by the LID practice. (E.g., if rain barrels are used
            to capture roof runoff and roofs represent 60% of the impervious area,
            then the impervious area treated is 60%). If the LID unit treats only direct
            rainfall, such as with a green roof, then this value should be 0. If the LID
            takes up the entire subcatchment then this field is ignored.
        ToPerv (int): a value of 1 indicates that the surface and drain flow from the LID unit
            should be routed back onto the pervious area of the subcatchment that
            contains it. This would be a common choice to make for rain barrels,
            rooftop disconnection, and possibly green roofs. The default value is 0.
        RptFile (str): optional name of a file to which detailed time series results for the LID
            will be written. Enclose the name in double quotes if it contains spaces
            and include the full path if it is different than the SWMM input file path.
            Use ‘*’ if not applicable and an entry for DrainTo follows
        DrainTo (str): optional name of subcatchment or node that receives flow from the unit’s
            drain line, if different from the outlet of the subcatchment that the LID is
            placed in.

    Remarks:
        If ``ToPerv`` is set to 1 and ``DrainTo`` set to some other outlet, then only the excess
        surface flow from the LID unit will be routed back to the subcatchment’s pervious
        area while the underdrain flow will be sent to ``DrainTo``.

        More than one type of LID process can be deployed within a subcatchment as long
        as their total area does not exceed that of the subcatchment and the total percent
        impervious area treated does not exceed 100.

    Examples:
        ::

            ;34 rain barrels of 12 sq ft each are placed in
            ;subcatchment S1. They are initially empty and treat 17%
            ;of the runoff from the subcatchment’s impervious area.
            ;The outflow from the barrels is returned to the
            ;subcatchment’s pervious area.
            S1 RB14 34 12 0 0 17 1

            ;Subcatchment S2 consists entirely of a single vegetative
            ;swale 200 ft long by 50 ft wide.
            S2 Swale 1 10000 50 0 0 0 “swale.rpt”
    """
    _identifier = (IDENTIFIERS.Subcatch, 'LID')
    _section_label = LID_USAGE

    def __init__(self, Subcatch, LID, Number, Area, Width, InitSat, FromImp, ToPerv, RptFile=NaN, DrainTo=NaN):
        self.Subcatch = str(Subcatch)
        self.LID = str(LID)
        self.Number = Number
        self.Area = float(Area)
        self.Width = float(Width)
        self.InitSat = float(InitSat)
        self.FromImp = float(FromImp)
        self.ToPerv = int(ToPerv)
        self.RptFile = RptFile
        self.DrainTo = DrainTo
