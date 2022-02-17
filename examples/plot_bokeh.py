from swmm_api import read_inp_file
from swmm_api.input_file.macro_snippets.plot_macros_bokeh import plot_map
from bokeh.plotting import save

inp = read_inp_file('epaswmm5_apps_manual/Example6-Final _MP.inp')

fig = plot_map(inp)
save(fig, filename='test.html', title='epaswmm5_apps_manual/projects/Example1.inp')

# http://louistiao.me/posts/notebooks/embedding-matplotlib-animations-in-jupyter-notebooks/
