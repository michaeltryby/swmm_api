from swmm_api import SwmmInput
from swmm_api.input_file.macros import remove_empty_sections

inp = SwmmInput.read_file('demo_catchment_adap.inp')
remove_empty_sections(inp)
inp.write_file('demo_catchment_adap_py.inp', fast=False)
