from .inp_sections_generic import (convert_title, convert_options, convert_report, convert_evaporation,
                                   convert_temperature, convert_timeseries, convert_curves, convert_loadings,
                                   convert_coordinates, convert_map, convert_tags)
from .inp_sections import *
from .inp_helpers import InpSection
from .helpers.sections import *


########################################################################################################################
class InpReader:
    """read SWMM .inp file and convert the data to a more usable format"""

    def __init__(self):
        self._data = dict()

    convert_handler_old = {
        REPORT: convert_report,
        TITLE: convert_title,
        OPTIONS: convert_options,
        EVAPORATION: convert_evaporation,
        TEMPERATURE: convert_temperature,

        CURVES: convert_curves,
        TIMESERIES: convert_timeseries,

        LOADINGS: convert_loadings,

        COORDINATES: convert_coordinates,
        MAP: convert_map,

        TAGS: convert_tags,
    }
    # convert_handler_generic = {
    #
    # }

    convert_handler_new = {
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

    def read_inp(self, filename):
        """
        reads full .inp file and splits the lines into a list and each line into a list of strings

        Args:
            filename (str): path to .inp file
        """
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
                self._data[head] = list()

            else:
                self._data[head].append(line.split())

    def convert_sections(self, ignore_sections=None, convert_sections=None):
        """
        convert sections into special Sections Objects (InpSection)
        and for each section into special separate objects (BaseSection)

        Args:
            ignore_sections (list[str]): don't convert ignored sections
            convert_sections (list[str]): only convert these sections
        """
        for head, lines in self._data.items():
            if convert_sections is not None and head not in convert_sections:
                continue

            elif ignore_sections is not None and head in ignore_sections:
                continue

            if head in self.convert_handler_old:
                self._data[head] = self.convert_handler_old[head](lines)

            # elif head in self.convert_handler_generic:
            #     self._data[head] = self.convert_handler_generic[head].from_lines(lines)

            elif head in self.convert_handler_new:
                self._data[head] = InpSection.from_lines(lines, self.convert_handler_new[head])

    @classmethod
    def from_file(cls, filename, drop_gui_part=True, ignore_sections=None, convert_sections=None):
        """
        read .inp file and convert given/all sections

        Args:
            filename (str): path/filename to .inp file
            drop_gui_part (bool): don't convert gui sections (ie. for commandline use)
            ignore_sections (list[str]): don't convert ignored sections
            convert_sections (list[str]): only convert these sections

        Returns:
            dict: of sections of the .inp file
        """
        inp_reader = cls()
        inp_reader.read_inp(filename)
        if drop_gui_part:
            if ignore_sections is None:
                ignore_sections = list()
            ignore_sections += cls.GUI_SECTIONS

        inp_reader.convert_sections(ignore_sections=ignore_sections, convert_sections=convert_sections)
        return inp_reader._data
