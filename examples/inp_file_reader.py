import os

from swmm_api import read_inp_file
from swmm_api.input_file import SEC
from swmm_api.input_file.macros.geo import complete_vertices
from swmm_api.run import swmm5_run, delete_swmm_files

# inp = read_inp_file('adjust_subcatchemnt_pattern.inp')
# inp.force_convert_all()
# fn_inp_temp = 'temp.inp'
# inp.write_file(fn_inp_temp)
# swmm5_run(fn_inp_temp)
# delete_swmm_files(fn_inp_temp, including_inp=False)
# exit()

# inp = read_inp_file('/home/markus/PycharmProjects/swmm_api/examples/internal/2015_06_17_UG_Weiz_OPTI_maxAbk_Ret_3J_60_KW.inp')
inp = read_inp_file('epaswmm5_apps_manual/Example7-Final.inp')

inp.RAINGAGES

inp[SEC.RAINGAGES]['RainGage'].Interval = '0:01'
inp[SEC.RAINGAGES]['RainGage'].set('Interval', '0:01')
inp[SEC.RAINGAGES]['RainGage']['Interval'] = '0:01'

print(inp[SEC.RAINGAGES]['RainGage'].to_inp_line())
exit()


complete_vertices(inp)

inp.write_file('temp.inp')
swmm5_run('temp.inp')
