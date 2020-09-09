import pandas
from .helpers.sections import *
from .inp_sections import *
from .inp_sections_generic import TimeseriesSection, TagsSection, CurvesSection, ReportSection, CoordinatesSection, VerticesSection

SECTION_TYPES = {
    TITLE: str,
    OPTIONS: dict,
    EVAPORATION: dict,
    TEMPERATURE: dict,

    REPORT: ReportSection,
    CURVES: CurvesSection,
    TIMESERIES: TimeseriesSection,
    LOADINGS: pandas.DataFrame,
    TAGS: TagsSection,

    # GUI data
    COORDINATES: CoordinatesSection,
    VERTICES: VerticesSection,
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
    TRANSECTS: Transect,
}