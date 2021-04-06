from swmm_api import read_inp_file, swmm5_run
from swmm_api.input_file.section_labels import OPTIONS, LID_USAGE
import os


inp = read_inp_file('epaswmm5_apps_manual/Example6-Final.inp', ignore_gui_sections=False)
for unit in ['CFS', 'CMS', 'GPM', 'MGD', 'LPS', 'MLD']:
    inp[OPTIONS]['FLOW_UNITS'] = unit
    fn = f'temp/{unit}.inp'
    # if unit in ['CMS', 'LPS']:
    #     for label, l in inp[LID_USAGE].items():
    #         inp[LID_USAGE][label].Area /= 5
    inp.write_file(fn)
    swmm5_run(fn)
    os.remove(fn)
    os.remove(fn.replace('.inp', '.out'))
