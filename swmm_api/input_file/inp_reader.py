from .inp_sections_generic import (convert_title, convert_options, convert_report, convert_evaporation,
                                   convert_temperature, convert_loadings, convert_coordinates, convert_map)
from .inp_sections_generic import TimeseriesSection, TagsSection, CurvesSection
from .inp_sections import *
from .inp_helpers import InpSection, InpData
from .helpers.sections import *

from inspect import isclass, isfunction

"""read SWMM .inp file and convert the data to a more usable format"""

CONVERTER = {
    # options = dict
    REPORT: convert_report,
    TITLE: convert_title,
    OPTIONS: convert_options,
    EVAPORATION: convert_evaporation,
    TEMPERATURE: convert_temperature,

    CURVES: CurvesSection,
    TIMESERIES: TimeseriesSection,
    LOADINGS: convert_loadings,
    TAGS: TagsSection,

    # GUI data
    COORDINATES: convert_coordinates,
    MAP: convert_map,

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

GUI_SECTIONS = [
    MAP,
    COORDINATES,
    VERTICES,
    POLYGONS,
    SYMBOLS,
    LABELS,
    BACKDROP,
]


def _read_inp_file_raw(filename):
    """
    reads full .inp file and splits the lines into a list and each line into a list of strings

    Args:
        filename (str): path to .inp file

    Returns:
        InpData: raw inp-file data
    """
    inp = InpData()
    if isinstance(filename, str):
        inp_file = open(filename, 'r', encoding='iso-8859-1')
    else:
        inp_file = filename

    head = None
    for line in inp_file:
        line = line.strip()
        if line == '' or line.startswith(';'):  # ignore empty and comment lines
            continue

        elif line.startswith('[') and line.endswith(']'):  # section head
            head = line.replace('[', '').replace(']', '').upper()
            inp[head] = list()

        else:
            inp[head].append(line.split())

    return inp


def _convert_sections(inp, ignore_sections=None, convert_sections=None, custom_converter=None):
    """
    convert sections into special Sections Objects (InpSection)
    and for each section into special separate objects (BaseSection)

    Args:
        inp (InpData): raw inp-file data
        ignore_sections (list[str]): don't convert ignored sections
        convert_sections (list[str]): only convert these sections
        custom_converter (dict): dictionary of {section: converter/section_type}

    Returns:
        InpData: converted inp-file data
    """
    converter = CONVERTER.copy()
    if custom_converter is not None:
        converter.update(custom_converter)

    # from mp.helpers.check_time import Timer
    for head, lines in inp.items():
        # with Timer(head):
        if (convert_sections is not None) and (head not in convert_sections):
            continue

        elif (ignore_sections is not None) and (head in ignore_sections):
            continue

        if head in converter:
            section_ = converter[head]

            if isfunction(section_):  # section_ ... converter
                inp[head] = section_(lines)

            elif isclass(section_):  # section_ ... type
                if hasattr(section_, 'from_lines'):
                    inp[head] = section_.from_lines(lines)
                else:
                    inp[head] = InpSection.from_lines(lines, section_)

            else:
                raise NotImplemented()

    return inp


def read_inp_file(filename, ignore_sections=None, convert_sections=None, custom_converter=None,
                  ignore_gui_sections=True):
    """
    read .inp file and convert given/all sections

    Args:
        filename (str): path/filename to .inp file
        ignore_sections (list[str]): don't convert ignored sections
        convert_sections (list[str]): only convert these sections
        custom_converter (dict): dictionary of {section: converter/section_type}
        ignore_gui_sections (bool): don't convert gui sections (ie. for commandline use)

    Returns:
        InpData: of sections of the .inp file
    """
    inp = _read_inp_file_raw(filename)
    if ignore_gui_sections:
        if ignore_sections is None:
            ignore_sections = list()
        ignore_sections += GUI_SECTIONS

    inp = _convert_sections(inp, ignore_sections=ignore_sections, convert_sections=convert_sections,
                            custom_converter=custom_converter)
    return inp
