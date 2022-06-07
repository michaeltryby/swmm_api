from swmm_api.input_file.macros.plotting_longitudinal import plot_longitudinal
from swmm_api.input_file.macros import plot_map
from swmm_api import read_inp_file

inp = read_inp_file('epaswmm5_apps_manual/Example6-Final _MP.inp')

fig, ax = plot_map(inp)
fig.show()

fig, ax = plot_longitudinal(inp, start_node='9', end_node='18', out=None, ax=None, zero_node=None)
ax.set_title("start_node='9', end_node='18'")
fig.show()