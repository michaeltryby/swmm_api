import pandas
from swmm_api.input_file.inp_sections.labels import *
from swmm_api.input_file.inp_sections import *

SECTION_TYPES = {
    TITLE: str,
    OPTIONS: dict,
    EVAPORATION: dict,
    TEMPERATURE: dict,

    REPORT: ReportSection,

    CURVES: Curve,
    TIMESERIES: TimeseriesSection,

    LOADINGS: pandas.DataFrame,

    # something different
    TAGS: TagsSection,

    # GUI data
    COORDINATES: Coordinate,
    VERTICES: Vertices,
    POLYGONS: Polygon,
    SYMBOLS: Symbol,
    MAP: MapSection,

    # custom section objects
    CONDUITS: Conduit,
    ORIFICES: Orifice,
    WEIRS: Weir,
    PUMPS: Pump,
    OUTLETS: Outlet,

    TRANSECTS: Transect,
    XSECTIONS: CrossSection,
    LOSSES: Loss,

    JUNCTIONS: Junction,
    OUTFALLS: Outfall,
    STORAGE: Storage,

    DWF: DryWeatherFlow,
    INFLOWS: Inflow,

    SUBCATCHMENTS: SubCatchment,
    SUBAREAS: SubArea,
    INFILTRATION: Infiltration,

    RAINGAGES: RainGage,
    PATTERNS: Pattern,
    POLLUTANTS: Pollutant,
    CONTROLS: Control,
}

GUI_SECTIONS = [
    MAP,
    COORDINATES,
    VERTICES,
    POLYGONS,
    SYMBOLS,
    LABELS,
    BACKDROP,
]