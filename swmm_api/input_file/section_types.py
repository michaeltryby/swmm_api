from .section_labels import *
from .sections import *

"""objects or section class for a section in the inp-file"""
SECTION_TYPES = {
    TITLE: TitleSection,
    OPTIONS: OptionSection,
    EVAPORATION: EvaporationSection,
    TEMPERATURE: TemperatureSection,
    REPORT: ReportSection,
    FILES: FilesSection,
    BACKDROP: BackdropSection,
    ADJUSTMENTS: AdjustmentsSection,
    # -----
    # GUI data
    COORDINATES: Coordinate,
    VERTICES: Vertices,
    POLYGONS: Polygon,
    SYMBOLS: Symbol,
    MAP: MapSection,
    LABELS: Label,
    # -----
    # custom section objects
    CONDUITS: Conduit,
    ORIFICES: Orifice,
    WEIRS: Weir,
    PUMPS: Pump,
    OUTLETS: Outlet,

    TRANSECTS: Transect,
    XSECTIONS: CrossSection,
    LOSSES: Loss,
    # -----
    JUNCTIONS: Junction,
    OUTFALLS: Outfall,
    STORAGE: Storage,

    DWF: DryWeatherFlow,
    INFLOWS: Inflow,
    RDII: RainfallDependentInfiltrationInflow,
    TREATMENT: Treatment,
    # -----
    SUBCATCHMENTS: SubCatchment,
    SUBAREAS: SubArea,
    INFILTRATION: InfiltrationGreenAmpt,

    LOADINGS: Loading,
    WASHOFF: WashOff,
    BUILDUP: BuildUp,
    COVERAGES: Coverage,
    GWF: GroundwaterFlow,
    GROUNDWATER: Groundwater,
    SNOWPACKS: SnowPack,
    # -----
    RAINGAGES: RainGage,
    PATTERNS: Pattern,
    POLLUTANTS: Pollutant,
    CONTROLS: Control,
    CURVES: Curve,
    TIMESERIES: Timeseries,
    TAGS: Tag,
    HYDROGRAPHS: Hydrograph,
    LANDUSES: LandUse,
    AQUIFERS: Aquifer,
    # -----
    LID_CONTROLS: LIDControl,
    LID_USAGE: LIDUsage,
}
"""objects or section class for a section in the inp-file"""
