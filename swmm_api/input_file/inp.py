import os
import re

from .helpers import _sort_by, section_to_string, CustomDictWithAttributes, convert_section, inp_sep, InpSection
from .section_types import SECTION_TYPES, GUI_SECTIONS


class SwmmInput(CustomDictWithAttributes):
    """
    overall class for an input file

    child class of dict

    just used for the copy function and to identify ``.inp``-file data
    """

    def __getitem__(self, item: str) -> InpSection:
        return super().__getitem__(item)

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
    def read_file(cls, filename, ignore_sections=None, convert_sections=None, custom_converter=None,
                  ignore_gui_sections=False):
        """
        read ``.inp``-file and convert the sections in pythonic objects

        Args:
            filename (str): path/filename to .inp file
            ignore_sections (list[str]): don't convert ignored sections. Default: ignore none.
            convert_sections (list[str]): only convert these sections. Default: convert all
            custom_converter (dict): dictionary of {section: converter/section_type} Default: :py:const:`SECTION_TYPES`
            ignore_gui_sections (bool): don't convert gui/geo sections (ie. for commandline use)

        Returns:
            SwmmInput: dict-like data of the sections in the ``.inp``-file
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
        if os.path.isfile(filename):
            with open(filename, 'r', encoding='iso-8859-1') as inp_file:
                txt = inp_file.read()
        else:
            txt = filename
        # __________________________________
        headers = [h.upper() for h in re.findall(r"\[(\w+)\]", txt)]
        section_text = [h.strip() for h in re.split(r"\[\w+\]", txt)[1:]]

        # __________________________________
        inp = cls()
        for head, lines in zip(headers, section_text):
            inp[head] = convert_section(head, lines, converter)
        return inp

    def to_string(self, fast=True):
        """
        create the string of a new ``.inp``-file

        Args:
            inp (swmm_api.input_file.SwmmInput): dict-like Input-file data with several sections
            fast (bool): don't use any formatting else format as table

        Returns:
            str: string of input file text
        """
        f = ''
        sep = f'\n{inp_sep}\n[{{}}]\n'
        # sep = f'\n[{{}}]  ;;{"_" * 100}\n'
        for head in sorted(self.keys(), key=_sort_by):
            f += sep.format(head)
            section_data = self[head]
            f += section_to_string(section_data, fast=fast)
        return f

    def write_file(self, filename, fast=True, encoding='iso-8859-1'):
        """
        create/write a new ``.inp``-file

        Args:
            inp (SwmmInput): dict-like ``.inp``-file data with several sections
            filename (str): path/filename of created ``.inp``-file
            fast (bool): don't use any formatting else format as table
        """
        with open(filename, 'w', encoding=encoding) as f:
            f.write(self.to_string(fast=fast))


def read_inp_file(filename, ignore_sections=None, convert_sections=None, custom_converter=None,
                  ignore_gui_sections=True):
    """
    read ``.inp``-file and convert the sections in pythonic objects

    Args:
        filename (str): path/filename to .inp file
        ignore_sections (list[str]): don't convert ignored sections. Default: ignore none.
        convert_sections (list[str]): only convert these sections. Default: convert all
        custom_converter (dict): dictionary of {section: converter/section_type} Default: :py:const:`SECTION_TYPES`
        ignore_gui_sections (bool): don't convert gui/geo sections (ie. for commandline use)

    Returns:
        SwmmInput: dict-like data of the sections in the ``.inp``-file
    """
    return SwmmInput.read_file(filename, ignore_sections=ignore_sections, convert_sections=convert_sections,
                               custom_converter=custom_converter, ignore_gui_sections=ignore_gui_sections)
