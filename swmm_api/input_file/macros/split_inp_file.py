import os

from ..helpers import section_to_string, convert_section
from ... import SwmmInput
from ..section_types import SECTION_TYPES


def split_inp_to_files(inp_fn, convert_sections=None, **kwargs):
    """
    spit an inp-file into the sections and write per section one file

    creates a subdirectory in the directory of the input file with the name of the input file (without ``.inp``)
    and creates for each section a ``.txt``-file

    Args:
        inp_fn (str): path to inp-file
        convert_sections (list): only convert these sections. Default: convert no section
        **kwargs: keyword arguments of the :func:`~swmm_api.input_file.inp_reader.read_inp_file`-function

    Keyword Args:
        ignore_sections (list[str]): don't convert ignored sections. Default: ignore none.
        custom_converter (dict): dictionary of {section: converter/section_type} Default: :const:`SECTION_TYPES`
        ignore_gui_sections (bool): don't convert gui/geo sections (ie. for commandline use)
    """
    parent = inp_fn.replace('.inp', '')
    os.mkdir(parent)
    inp = SwmmInput.read_file(inp_fn, convert_sections=convert_sections, **kwargs)
    for s in inp.keys():
        with open(os.path.join(parent, s + '.txt'), 'w') as f:
            f.write(section_to_string(inp[s], fast=False))


def read_split_inp_file(inp_fn):
    """
    use this function to read an split inp-file after splitting the file with the :func:`~split_inp_to_files`-function

    Args:
        inp_fn (str): path of the directory of the split inp-file

    Returns:
        SwmmInput: inp-file data
    """
    inp = SwmmInput()
    for header_file in os.listdir(inp_fn):
        header = header_file.replace('.txt', '')
        with open(os.path.join(inp_fn, header_file), 'r') as f:
            inp[header] = convert_section(header, f.read(), SECTION_TYPES)

    return inp
