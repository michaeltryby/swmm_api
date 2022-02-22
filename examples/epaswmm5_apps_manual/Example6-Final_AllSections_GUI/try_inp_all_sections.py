from swmm_api import SwmmInput, SwmmReport, SwmmOutput, SwmmHotstart

inp = SwmmInput.read_file('Example6-Final_AllSections_GUI.inp')
inp.copy()
print()