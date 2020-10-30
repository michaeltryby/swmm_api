from os import path, listdir, mkdir, remove

from swmm_api import read_inp_file, write_inp_file, swmm5_run

"""if no error occur pretty much everything works (or more test cases are needed)"""

temp_dir = 'temp'
if not path.isdir(temp_dir):
    mkdir(temp_dir)

parent_dir = path.dirname(__file__)
example_dirs = [
    # path.join(parent_dir, 'epaswmm5_apps_manual'),
    path.join(parent_dir, 'epaswmm5_apps_manual', 'projects')
]
for folder in example_dirs:
    for fn in listdir(folder):
        if '.inp' in fn:
            inp = read_inp_file(path.join(folder, fn), ignore_gui_sections=False)
            inp_fn = path.join(temp_dir, 'temp.inp')
            write_inp_file(inp, inp_fn)

            swmm5_run(inp_fn, init_print=False)
            remove(inp_fn.replace('.inp', '.rpt'))
            remove(inp_fn.replace('.inp', '.out'))
            print(fn, 'CHECK')
