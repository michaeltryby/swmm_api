#%% md

## Example for INP File Macros

#%%

from swmm_api import read_inp_file
from swmm_api.input_file.macros.plotting import plot_map, plot_longitudinal

#%%

inp = read_inp_file('epaswmm5_apps_manual/projects/Example1.inp', ignore_gui_sections=False)

#%%

fig, ax = plot_map(inp)


#%%

fig, ax = plot_longitudinal(inp, start_node='9', end_node='18', out=None, ax=None, zero_node=None)
ax.set_title("start_node='9', end_node='18'")
