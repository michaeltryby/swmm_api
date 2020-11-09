from .labels import *
from swmm_api.input_file.inp_sections import *

SECTION_TYPES = {
    # TITLE: str,
    OPTIONS: OptionSection,
    EVAPORATION: EvaporationSection,
    TEMPERATURE: TemperatureSection,
    REPORT: ReportSection,
    # -----
    # something different
    TAGS: TagsSection,
    # -----
    # GUI data
    COORDINATES: Coordinate,
    VERTICES: Vertices,
    POLYGONS: Polygon,
    SYMBOLS: Symbol,
    MAP: MapSection,
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
    # -----
    SUBCATCHMENTS: SubCatchment,
    SUBAREAS: SubArea,
    INFILTRATION: Infiltration,

    LOADINGS: Loading,
    # -----
    RAINGAGES: RainGage,
    PATTERNS: Pattern,
    POLLUTANTS: Pollutant,
    CONTROLS: Control,
    CURVES: Curve,
    TIMESERIES: Timeseries,
}

GEO_SECTIONS = [
    COORDINATES,
    VERTICES,
    POLYGONS
]

GUI_SECTIONS = [
    MAP,
    SYMBOLS,
    LABELS,
    BACKDROP,
]
