import os
from tqdm import tqdm
import pandas as pd
from swmm_api.input_file import section_labels

from swmm_api import read_inp_file

parent_dir = os.path.dirname(__file__)
example_dirs = [
    os.path.join(parent_dir, 'epaswmm5_apps_manual'),
    os.path.join(parent_dir, 'epaswmm5_apps_manual', 'projects')
]

sections = dict()

process_bar = tqdm(example_dirs)
for folder in process_bar:
    for fn in os.listdir(folder):
        if '.inp' in fn:
            inp = read_inp_file(os.path.join(folder, fn), ignore_gui_sections=False)
            print(fn)
            if 'projects' in folder:
                fn = 'projects/' + fn
            else:
                fn = 'examples/' + fn
            sections[fn] = {i: int(i in inp) for i in vars(section_labels).keys() if not i.startswith('_')}

df = pd.DataFrame(sections).T
df.to_excel('sections_in_examples.xlsx')
