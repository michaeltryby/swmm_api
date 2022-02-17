from swmm_api import SwmmInput

inp = SwmmInput.read_file('example_controls.inp')
c = inp.CONTROLS
print(c.to_inp_lines())
