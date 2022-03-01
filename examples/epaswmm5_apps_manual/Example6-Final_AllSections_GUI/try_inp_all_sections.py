from swmm_api import SwmmInput, SwmmReport, SwmmOutput, SwmmHotstart

rpt = SwmmReport('Example6-Final_AllSections_GUI.rpt')
rpt.analyse_end

inp = SwmmInput.read_file('Example6-Final_AllSections_GUI.inp')
inp.force_convert_all()
inp.copy()
inp.to_string(fast=True)
print()
