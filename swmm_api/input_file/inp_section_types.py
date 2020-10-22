import pandas
from .helpers.sections import *
from .inp_sections import *
from .inp_sections_generic import (TimeseriesSection, TagsSection, CurvesSection, ReportSection, CoordinatesSection,
                                   VerticesSection, TransectSection, PolygonSection, SymbolSection)

SECTION_TYPES = {
    TITLE: str,
    OPTIONS: dict,
    EVAPORATION: dict,
    TEMPERATURE: dict,

    REPORT: ReportSection,

    CURVES: CurvesSection,
    TIMESERIES: TimeseriesSection,
    TRANSECTS: TransectSection,

    LOADINGS: pandas.DataFrame,

    # something different
    TAGS: TagsSection,

    # GUI data
    COORDINATES: CoordinatesSection,
    VERTICES: VerticesSection,
    POLYGONS: PolygonSection,
    SYMBOLS: SymbolSection,
    MAP: dict,

    # custom section objects
    CONDUITS: Conduit,
    ORIFICES: Orifice,
    JUNCTIONS: Junction,
    SUBCATCHMENTS: SubCatchment,
    SUBAREAS: SubArea,
    DWF: DryWeatherFlow,
    XSECTIONS: CrossSection,
    INFILTRATION: Infiltration,
    OUTFALLS: Outfall,
    WEIRS: Weir,
    STORAGE: Storage,
    OUTLETS: Outlet,
    LOSSES: Loss,
    INFLOWS: Inflow,
    RAINGAGES: RainGauge,
    PUMPS: Pump,
    PATTERNS: Pattern,
    POLLUTANTS: Pollutant,
}