from swmm_api.input_file import read_inp_file
from swmm_api.input_file.inp_writer import write_inp_file
from swmm_api.run import swmm5_run

inp = read_inp_file('epaswmm5_apps_manual/Example7-Final.inp')

write_inp_file(inp, 'temp.inp')
swmm5_run('temp.inp')
