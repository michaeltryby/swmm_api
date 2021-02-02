import re
from inspect import isclass, isfunction

from .inp_helpers import InpSection, InpData, inp_sep
from .inp_sections.types import SECTION_TYPES, GUI_SECTIONS


def convert_section(head, lines, converter):
    """
    convert section string to a section object

    Args:
        head (str): header of the section
        lines (str): lines in the section
        converter (dict): dict of converters assigned to header {header: converter]

    Returns:
        str | InpSection | InpSectionGeneric: converted section
    """
    if head in converter:
        section_ = converter[head]

        if isfunction(section_):  # section_ ... converter function
            return section_(lines)

        elif isclass(section_):  # section_ ... type/class
            if hasattr(section_, 'from_inp_lines'):
                # section has multiple options over multiple lines
                return section_.from_inp_lines(lines)
                # REPORT, TIMESERIES, CURVES, TAGS
            else:
                # each line is a object OR each object has multiple lines
                return InpSection.from_inp_lines(lines, section_)

        else:
            raise NotImplemented()
    else:
        return lines.replace(inp_sep, '').strip()


def read_inp_file(filename, ignore_sections=None, convert_sections=None, custom_converter=None,
                  ignore_gui_sections=True, txt=None):
    """
    read ``.inp``-file and convert the sections in pythonic objects

    Args:
        filename (str): path/filename to .inp file
        ignore_sections (list[str]): don't convert ignored sections. Default: ignore none.
        convert_sections (list[str]): only convert these sections. Default: convert all
        custom_converter (dict): dictionary of {section: converter/section_type} Default: :py:const:`SECTION_TYPES`
        ignore_gui_sections (bool): don't convert gui/geo sections (ie. for commandline use)

    Returns:
        InpData: dict-like data of the sections in the ``.inp``-file
    """
    converter = SECTION_TYPES.copy()

    if ignore_sections is None:
        ignore_sections = list()
    if ignore_gui_sections:
        ignore_sections += GUI_SECTIONS
    for s in ignore_sections:
        if s in converter:
            converter.pop(s)

    if custom_converter is not None:
        converter.update(custom_converter)

    if convert_sections is not None:
        converter = {h: converter[h] for h in converter if h in convert_sections}

    # __________________________________
    if txt is None:
        with open(filename, 'r', encoding='iso-8859-1') as inp_file:
            txt = inp_file.read()

    # __________________________________
    headers = [h.upper() for h in re.findall(r"\[(\w+)\]", txt)]
    section_text = [h.strip() for h in re.split(r"\[\w+\]", txt)[1:]]

    # __________________________________
    inp = InpData()
    for head, lines in zip(headers, section_text):
        inp[head] = convert_section(head, lines, converter)
    return inp
