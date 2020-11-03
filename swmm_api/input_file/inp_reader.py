import re
from inspect import isclass, isfunction

from .inp_sections.labels import *
from .inp_helpers import InpSection, InpData, txt_to_lines
from .inp_sections.types import SECTION_TYPES, GUI_SECTIONS
from .inp_sections.generic_section import convert_title, convert_options, convert_evaporation, convert_temperature

"""read SWMM .inp file and convert the data to a more usable format"""

CONVERTER = SECTION_TYPES.copy()
CONVERTER.update({
    # options = dict
    TITLE: convert_title,  # str
    OPTIONS: convert_options,  # dict
    EVAPORATION: convert_evaporation,  # dict
    TEMPERATURE: convert_temperature,  # dict
})

# ___________________________________________________________________
# to create a progressbar in the reading process
# only needed with big (> 200 MB) files
if 0:
    try:
        from tqdm import tqdm
        def _custom_iter(i, desc=None):
            if isinstance(i, str):
                i = list(txt_to_lines(i))
            return tqdm(i, desc=desc)
    except ImportError as e:
        def _custom_iter(i, desc=None):
            return i

else:
    def _custom_iter(i, desc=None):
        return i


########################################################################################################################
def _read_inp_file_raw(filename):
    """
    reads full .inp file and splits the text into a dict of sections and each sections into a string

    Args:
        filename (str): path to .inp file

    Returns:
        InpData: dict-like raw inp-file data (values=string)
    """

    if isinstance(filename, str):
        inp_file = open(filename, 'r', encoding='iso-8859-1')
    else:
        inp_file = filename

    txt = inp_file.read()
    inp_file.close()
    headers = re.findall(r"\[(\w+)\]", txt)
    headers = [h.upper() for h in headers]
    section_text = re.split(r"\[\w+\]", txt)[1:]
    section_text = [h.strip() for h in section_text]
    inp = InpData(dict(zip(headers, section_text)))
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

    # iter_ = _custom_iter(inp.items(), desc='convert sections')
    iter_ = inp.items()
    for head, lines in iter_:
        if (convert_sections is not None) and (head not in convert_sections):
            continue

        elif (ignore_sections is not None) and (head in ignore_sections):
            continue

        if head in converter:
            lines = _custom_iter(lines, desc=head)

            section_ = converter[head]

            if isfunction(section_):  # section_ ... converter function
                inp[head] = section_(lines)

            elif isclass(section_):  # section_ ... type/class
                if hasattr(section_, 'from_inp_lines'):
                    inp[head] = section_.from_inp_lines(lines)  # section has multiple options over multiple lines
                    # REPORT, TIMESERIES, CURVES, TAGS
                else:
                    # each line is a object OR each object has multiple lines
                    inp[head] = InpSection.from_inp_lines(lines, section_)

            else:
                raise NotImplemented()

    return inp


def read_inp_file(filename, ignore_sections=None, convert_sections=None, custom_converter=None,
                  ignore_gui_sections=False):
    """
    read ``.inp``-file and convert the sections in pythonic objects

    Args:
        filename (str): path/filename to .inp file
        ignore_sections (list[str]): don't convert ignored sections. Default: ignore none.
        convert_sections (list[str]): only convert these sections Default: convert all
        custom_converter (dict): dictionary of {section: converter/section_type}
        ignore_gui_sections (bool): don't convert gui/geo sections (ie. for commandline use)

    Returns:
        InpData: dict-like data of the sections in the ``.inp``-file
    """
    if ignore_gui_sections:
        if ignore_sections is None:
            ignore_sections = list()
        ignore_sections += GUI_SECTIONS

    inp = _read_inp_file_raw(filename)
    inp = _convert_sections(inp, ignore_sections=ignore_sections, convert_sections=convert_sections,
                            custom_converter=custom_converter)
    return inp
