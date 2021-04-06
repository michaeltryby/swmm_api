from os import path, listdir, mkdir, remove
from shutil import rmtree

from tqdm import tqdm

from swmm_api import read_inp_file, swmm5_run, SwmmReport


class tqdm2(tqdm):
    def refresh(self, *args, **kwargs):
        # self.desc = self.iterable[self.n]
        if self.n < self.total:
            self.postfix = str(list(self.iterable)[self.n])
        else:
            self.postfix = ''
        tqdm.refresh(self, *args, **kwargs)


"""if no error occur pretty much everything works (or more test cases are needed)"""

temp_dir = 'temp'
if not path.isdir(temp_dir):
    mkdir(temp_dir)

parent_dir = path.dirname(__file__)
example_dirs = [path.join(parent_dir, 'epaswmm5_apps_manual'),
                path.join(parent_dir, 'epaswmm5_apps_manual', 'projects')]

example_files = [path.join(folder, fn) for folder in example_dirs for fn in listdir(folder) if '.inp' in fn]

for fn in tqdm2(example_files):
    inp = read_inp_file(fn, ignore_gui_sections=False)
    inp_fn = path.join(temp_dir, 'temp.inp')
    inp.write_file(inp_fn)
    swmm5_run(inp_fn, init_print=False)
    # rpt = SwmmReport(inp_fn.replace('.inp', '.rpt'))
    # print(rpt.get_warnings())
    remove(inp_fn.replace('.inp', '.rpt'))

rmtree(temp_dir)
