import os
import re
import warnings

from .helpers import (section_to_string, CustomDictWithAttributes, convert_section, InpSection,
                      InpSectionGeneric, SECTION_ORDER_DEFAULT, check_order, SECTIONS_ORDER_MP, head_to_str,
                      iter_section_lines, )
from .section_types import SECTION_TYPES
from .section_labels import *
from .sections import *
from .sections.subcatch import INFILTRATION_DICT


class SwmmInput(CustomDictWithAttributes):
    """
    overall class for an input file

    child class of dict

    just used for the copy function and to identify ``.inp``-file data
    """

    def __init__(self, *args, custom_section_handler=None, **kwargs):
        CustomDictWithAttributes.__init__(self, *args, **kwargs)
        self._converter = SECTION_TYPES.copy()

        if custom_section_handler is not None:
            self._converter.update(custom_section_handler)

        # only when reading a new file
        self._original_section_order = SECTIONS_ORDER_MP

    def update(self, d=None, **kwargs):
        for sec in d:
            if sec not in self:
                self[sec] = d[sec]
            else:
                if isinstance(self[sec], str):
                    pass
                else:
                    self[sec].update(d[sec])

    @classmethod
    def read_file(cls, filename, custom_converter=None, force_ignore_case=False, encoding='iso-8859-1'):
        """
        read ``.inp``-file and convert the sections in pythonic objects

        the sections will be converted when used

        Args:
            filename (str): path/filename to .inp file
            custom_converter (dict): dictionary of {section: converter/section_type} Default: :py:const:`SECTION_TYPES`
            force_ignore_case (bool): SWMM is case-insensitive but python is case-sensitive -> set True to ignore case
                                        all text/labels will be set to uppercase
            encoding (str): encoding of the inp text file

        Returns:
            SwmmInput: dict-like data of the sections in the ``.inp``-file
        """
        inp = cls(custom_section_handler=custom_converter)
        if os.path.isfile(filename) or filename.endswith('.inp'):
            with open(filename, 'r', encoding=encoding) as inp_file:
                txt = inp_file.read()
        else:
            txt = filename

        # __________________________________
        if force_ignore_case:
            txt = txt.upper()

        # __________________________________
        inp._original_section_order = []
        for head, lines in zip(re.findall(r"\[(\w+)\]", txt),
                               re.split(r"\[\w+\]", txt)[1:]):
            inp._data[head.upper()] = lines.strip()
            inp._original_section_order.append(head.upper())

        # ----------------
        # if order in inp follows default SWMM GUI order
        #   set full/complete order list of SWMM GUI
        #   to use the right order for additional created setions
        if check_order(inp, SECTION_ORDER_DEFAULT):
            inp._original_section_order = SECTION_ORDER_DEFAULT

        inp.set_default_infiltration_from_options()
        return inp

    def force_convert_all(self):
        _ = [self[sec] for sec in self]

    def __getitem__(self, key):
        # if section not in inp-data, create an empty section
        if key not in self:
            self._data[key] = self._converter[key].create_section()

        # if section is a string (raw string from the .inp-file) convert section first
        if isinstance(self._data[key], str):
            self[key] = convert_section(key, self._data[key], self._converter)

        return self._data.__getitem__(key)

    def __setitem__(self, key, item):
        super().__setitem__(key, item)
        # super().__setattr__(key, item)
        # self._data.__setitem__(key, item)
        # if key == OPTIONS:
        #     self.set_default_infiltration_from_options()
        if hasattr(self[key], 'set_parent_inp'):
            self[key].set_parent_inp(self)

    def __delattr__(self, item):
        """delete section"""
        if item in SECTION_TYPES:
            # print('delete section')
            del self._data[item]
        else:
            # print('delete attribute')
            super().__delattr__(item)

    def set_default_infiltration_from_options(self):
        if OPTIONS in self \
                and 'INFILTRATION' in self[OPTIONS] \
                and isinstance(self[OPTIONS], (dict, OptionSection, InpSectionGeneric)):
            self.set_infiltration_method(INFILTRATION_DICT.get(self[OPTIONS]['INFILTRATION']))

    def set_infiltration_method(self, infiltration_class):
        self._converter[INFILTRATION] = infiltration_class

    def get_section_headers(self, custom_sections_order=None):
        if custom_sections_order is None:
            custom_sections_order = self._original_section_order

        def _sort_by(key):
            if key in custom_sections_order:
                return custom_sections_order.index(key)
            else:
                return len(custom_sections_order)

        return sorted(self.keys(), key=_sort_by)

    def to_string(self, fast=True, custom_sections_order=None, sort_objects_alphabetical=False):
        """
        create the string of a new ``.inp``-file

        Args:
            fast (bool): don't use any formatting else format as table
            custom_sections_order (list[str]): list of section names to preset the order of the section in the
                created inp-file | default: order of the read inp-file + default order of the SWMM GUI
            sort_objects_alphabetical (bool): if objects in a section should be sorted alphabetical |
                default: use order of the read inp-file and append new objects

        Returns:
            str: string of input file text
        """
        f = ''
        for head in self.get_section_headers(custom_sections_order):
            f += head_to_str(head)
            f += section_to_string(self._data[head], fast=fast, sort_objects_alphabetical=sort_objects_alphabetical)
        return f

    def write_file(self, filename, fast=True, encoding='iso-8859-1', custom_sections_order=None,
                   sort_objects_alphabetical=False, per_line=False):
        """
        create/write a new ``.inp``-file

        Args:
            filename (str): path/filename of created ``.inp``-file
            fast (bool): don't use any formatting else format as table
            encoding (str): define encoding for resulting inp-file
            custom_sections_order (list[str]): list of section names to preset the order of the section in the created
                inp-file | default: order of the read inp-file + default order of the SWMM GUI
            sort_objects_alphabetical (bool): if objects in a section should be sorted alphabetical |
                default: use order of the read inp-file and append new objects
            per_line (bool): weather to write the data line per line (=True) or section per section (=False) into the
                file. line per line has an advantage for big files (> 1 GB) and uses less memory (RAM).
        """
        with open(filename, 'w', encoding=encoding) as f:
            for head in self.get_section_headers(custom_sections_order):
                f.write(head_to_str(head))
                if per_line:
                    for line in iter_section_lines(self._data[head],
                                                   sort_objects_alphabetical=sort_objects_alphabetical):
                        f.write(line + '\n')
                else:
                    f.write(section_to_string(self._data[head], fast=fast,
                                              sort_objects_alphabetical=sort_objects_alphabetical))
        return filename

    def print_string(self, custom_sections_order=None):
        for head in self.get_section_headers(custom_sections_order):
            print(head_to_str(head))
            for line in iter_section_lines(self._data[head], sort_objects_alphabetical=False):
                print(line)

    def check_for_section(self, obj):
        """
        check if a section is in the inp-data, and create it if not present

        Args:
            obj (BaseSectionObject or InpSectionGeneric):

        Returns:
            InpSection or InpSectionGeneric: section of inp
        """
        if obj._section_label not in self:
            self[obj._section_label] = obj.create_section()
        return self[obj._section_label]

    def add_new_section(self, section):
        """
        add new section to the inp-data

        Args:
            section (InpSection, InpSectionGeneric):

        .. Important::
            works inplace
        """
        if section._label not in self:
            self[section._label] = section
        else:
            warnings.warn(f'Section [{section._label}] not empty!')

    def add_obj(self, obj):
        """
        add object to respective section

        Args:
            obj (BaseSectionObject):new object
        """
        self.check_for_section(obj)
        self[obj._section_label].add_obj(obj)

    def add_multiple(self, *items):
        """
        add multiple objects to respective sections

        Args:
            *items (BaseSectionObject): new objects
        """
        for obj in items:
            self.add_obj(obj)

    @property
    def OPTIONS(self):
        """
        OPTIONS Section

        Returns:
            OptionSection: OPTIONS Section
        """
        if OPTIONS in self:
            return self[OPTIONS]

    @property
    def REPORT(self):
        """
        REPORT Section

        Returns:
            ReportSection: REPORT Section
        """
        if REPORT in self:
            return self[REPORT]

    @property
    def EVAPORATION(self):
        """
        EVAPORATION Section

        Returns:
            EvaporationSection: EVAPORATION Section
        """
        if EVAPORATION in self:
            return self[EVAPORATION]

    @property
    def TEMPERATURE(self):
        """
        TEMPERATURE Section

        Returns:
            TemperatureSection: TEMPERATURE Section
        """
        if TEMPERATURE in self:
            return self[TEMPERATURE]

    @property
    def FILES(self):
        """
        FILES Section

        Returns:
            FilesSection: FILES Section
        """
        if FILES in self:
            return self[FILES]

    @property
    def BACKDROP(self):
        """
        BACKDROP Section

        Returns:
            BackdropSection: BACKDROP Section
        """
        if BACKDROP in self:
            return self[BACKDROP]

    @property
    def ADJUSTMENTS(self):
        """
        ADJUSTMENTS Section

        Returns:
            AdjustmentsSection: ADJUSTMENTS Section
        """
        if ADJUSTMENTS in self:
            return self[ADJUSTMENTS]

    # -----
    @property
    def COORDINATES(self):
        """
        COORDINATES section

        Returns:
            dict[str, Coordinate | CoordinateGeo] | InpSection: Coordinates in INP
        """
        if COORDINATES in self:
            return self[COORDINATES]

    @property
    def VERTICES(self):
        """
        VERTICES section

        Returns:
            dict[str, Vertices] | InpSection: Vertices section
        """
        if VERTICES in self:
            return self[VERTICES]

    @property
    def POLYGONS(self):
        """
        POLYGONS section

        Returns:
            dict[str, Polygon] | InpSection: Polygon section
        """
        if POLYGONS in self:
            return self[POLYGONS]

    @property
    def SYMBOLS(self):
        """
        SYMBOLS section

        Returns:
            dict[str, Symbol] | InpSection: Symbol section
        """
        if SYMBOLS in self:
            return self[SYMBOLS]

    @property
    def MAP(self):
        """
        MAP section

        Returns:
            dict[str, MapSection] | InpSection: MapSection section
        """
        if MAP in self:
            return self[MAP]

    @property
    def LABELS(self):
        """
        LABELS section

        Returns:
            dict[str, Label] | InpSection: Label section
        """
        if LABELS in self:
            return self[LABELS]

    @property
    def CONDUITS(self):
        """
        CONDUITS section

        Returns:
            dict[str, Conduit] | InpSection: Conduit section
        """
        if CONDUITS in self:
            return self[CONDUITS]

    @property
    def ORIFICES(self):
        """
        ORIFICES section

        Returns:
            dict[str, Orifice] | InpSection: Orifice section
        """
        if ORIFICES in self:
            return self[ORIFICES]

    @property
    def WEIRS(self):
        """
        WEIRS section

        Returns:
            dict[str, Weir] | InpSection: Weir section
        """
        if WEIRS in self:
            return self[WEIRS]

    @property
    def PUMPS(self):
        """
        PUMPS section

        Returns:
            dict[str, Pump] | InpSection: Pump section
        """
        if PUMPS in self:
            return self[PUMPS]

    @property
    def OUTLETS(self):
        """
        OUTLETS section

        Returns:
            dict[str, Outlet] | InpSection: Outlet section
        """
        if OUTLETS in self:
            return self[OUTLETS]

    @property
    def TRANSECTS(self):
        """
        TRANSECTS section

        Returns:
            dict[str, Transect] | InpSection: Transect section
        """
        if TRANSECTS in self:
            return self[TRANSECTS]

    @property
    def XSECTIONS(self):
        """
        XSECTIONS section

        Returns:
            dict[str, CrossSection] | InpSection: CrossSection section
        """
        if XSECTIONS in self:
            return self[XSECTIONS]

    @property
    def LOSSES(self):
        """
        LOSSES section

        Returns:
            dict[str, Loss] | InpSection: Loss section
        """
        if LOSSES in self:
            return self[LOSSES]

    @property
    def JUNCTIONS(self):
        """
        JUNCTIONS section

        Returns:
            dict[str, Junction] | InpSection: Junction section
        """
        if JUNCTIONS in self:
            return self[JUNCTIONS]

    @property
    def OUTFALLS(self):
        """
        OUTFALLS section

        Returns:
            dict[str, Outfall] | InpSection: Outfall section
        """
        if OUTFALLS in self:
            return self[OUTFALLS]

    @property
    def STORAGE(self):
        """
        STORAGE section

        Returns:
            dict[str, swmm_api.input_file.sections.node.Storage] | InpSection: Storage section
        """
        if STORAGE in self:
            return self[STORAGE]

    @property
    def DWF(self):
        """
        DWF section

        Returns:
            dict[str, DryWeatherFlow] | InpSection: DryWeatherFlow section
        """
        if DWF in self:
            return self[DWF]

    @property
    def INFLOWS(self):
        """
        INFLOWS section

        Returns:
            dict[str, Inflow] | InpSection: Inflow section
        """
        if INFLOWS in self:
            return self[INFLOWS]

    @property
    def RDII(self):
        """
        RDII section

        Returns:
            dict[str, RainfallDependentInfiltrationInflow] | InpSection: RainfallDependentInfiltrationInflow section
        """
        if RDII in self:
            return self[RDII]

    @property
    def TREATMENT(self):
        """
        TREATMENT section

        Returns:
            dict[str, Treatment] | InpSection: Treatment section
        """
        if TREATMENT in self:
            return self[TREATMENT]

    @property
    def SUBCATCHMENTS(self):
        """
        SUBCATCHMENTS section

        Returns:
            dict[str, SubCatchment] | InpSection: SubCatchment section
        """
        if SUBCATCHMENTS in self:
            return self[SUBCATCHMENTS]

    @property
    def SUBAREAS(self):
        """
        SUBAREAS section

        Returns:
            dict[str, SubArea] | InpSection: SubArea section
        """
        if SUBAREAS in self:
            return self[SUBAREAS]

    @property
    def INFILTRATION(self):
        """
        INFILTRATION section

        Returns:
            dict[str, Infiltration] | InpSection: Infiltration section
        """
        if INFILTRATION in self:
            return self[INFILTRATION]

    @property
    def LOADINGS(self):
        """
        LOADINGS section

        Returns:
            dict[str, Loading] | InpSection: Loading section
        """
        if LOADINGS in self:
            return self[LOADINGS]

    @property
    def WASHOFF(self):
        """
        WASHOFF section

        Returns:
            dict[str, WashOff] | InpSection: WashOff section
        """
        if WASHOFF in self:
            return self[WASHOFF]

    @property
    def BUILDUP(self):
        """
        BUILDUP section

        Returns:
            dict[str, BuildUp] | InpSection: BuildUp section
        """
        if BUILDUP in self:
            return self[BUILDUP]

    @property
    def COVERAGES(self):
        """
        COVERAGES section

        Returns:
            dict[str, Coverage] | InpSection: Coverage section
        """
        if COVERAGES in self:
            return self[COVERAGES]

    @property
    def GWF(self):
        """
        GWF section

        Returns:
            dict[str, GroundwaterFlow] | InpSection: GroundwaterFlow section
        """
        if GWF in self:
            return self[GWF]

    @property
    def GROUNDWATER(self):
        """
        GROUNDWATER section

        Returns:
            dict[str, Groundwater] | InpSection: Groundwater section
        """
        if GROUNDWATER in self:
            return self[GROUNDWATER]

    @property
    def RAINGAGES(self):
        """
        RAINGAGES section

        Returns:
            dict[str, RainGage] | InpSection: RainGage section
        """
        if RAINGAGES in self:
            return self[RAINGAGES]

    @property
    def PATTERNS(self):
        """
        PATTERNS section

        Returns:
            dict[str, Pattern] | InpSection: Pattern section
        """
        if PATTERNS in self:
            return self[PATTERNS]

    @property
    def POLLUTANTS(self):
        """
        POLLUTANTS section

        Returns:
            dict[str, Pollutant] | InpSection: Pollutant section
        """
        if POLLUTANTS in self:
            return self[POLLUTANTS]

    @property
    def CONTROLS(self):
        """
        CONTROLS section

        Returns:
            dict[str, Control] | InpSection: Control section
        """
        if CONTROLS in self:
            return self[CONTROLS]

    @property
    def CURVES(self):
        """
        CURVES section

        Returns:
            dict[str, Curve] | InpSection: Curve section
        """
        if CURVES in self:
            return self[CURVES]

    @property
    def TIMESERIES(self):
        """
        TIMESERIES section

        Returns:
            dict[str, Timeseries] | InpSection: Timeseries section
        """
        if TIMESERIES in self:
            return self[TIMESERIES]

    @property
    def TAGS(self):
        """
        TAGS section

        Returns:
            dict[str, Tag] | InpSection: Tag section
        """
        if TAGS in self:
            return self[TAGS]

    @property
    def HYDROGRAPHS(self):
        """
        HYDROGRAPHS section

        Returns:
            dict[str, Hydrograph] | InpSection: Hydrograph section
        """
        if HYDROGRAPHS in self:
            return self[HYDROGRAPHS]

    @property
    def LANDUSES(self):
        """
        LANDUSES section

        Returns:
            dict[str, LandUse] | InpSection: LandUse section
        """
        if LANDUSES in self:
            return self[LANDUSES]

    @property
    def AQUIFERS(self):
        """
        AQUIFERS section

        Returns:
            dict[str, Aquifer] | InpSection: Aquifer section
        """
        if AQUIFERS in self:
            return self[AQUIFERS]

    @property
    def SNOWPACKS(self):
        """
        SNOWPACKS section

        Returns:
            dict[str, SnowPack] | InpSection: SnowPack section
        """
        if SNOWPACKS in self:
            return self[SNOWPACKS]

    @property
    def LID_CONTROLS(self):
        """
        LID_CONTROLS section

        Returns:
            dict[str, LIDControl] | InpSection: LIDControl section
        """
        if LID_CONTROLS in self:
            return self[LID_CONTROLS]

    @property
    def LID_USAGE(self):
        """
        LID_USAGE section

        Returns:
            dict[str, LIDUsage] | InpSection: LIDUsage section
        """
        if LID_USAGE in self:
            return self[LID_USAGE]


def read_inp_file(filename, custom_converter=None, force_ignore_case=False, encoding='iso-8859-1'):
    """
    read ``.inp``-file and convert the sections in pythonic objects

    the sections will be converted when used

    Args:
        filename (str): path/filename to .inp file
        custom_converter (dict): dictionary of {section: converter/section_type} Default: :py:const:`SECTION_TYPES`
        force_ignore_case (bool): SWMM is case-insensitive but python is case-sensitive -> set True to ignore case
        encoding (str): encoding of the inp text file

    Returns:
        SwmmInput: dict-like data of the sections in the ``.inp``-file
    """
    return SwmmInput.read_file(filename, custom_converter=custom_converter, force_ignore_case=force_ignore_case,
                               encoding=encoding)
