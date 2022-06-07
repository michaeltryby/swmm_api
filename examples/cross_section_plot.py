#%%
from swmm_api import SwmmInput
from swmm_api.input_file.macros import get_cross_section_maker
from swmm_api.input_file.sections import CrossSection
#%%
inp = SwmmInput()
#%%
link_label = 'F'
inp.add_obj(CrossSection(link_label, CrossSection.SHAPES.PARABOLIC, height=2, parameter_2=1))
c = get_cross_section_maker(inp, link_label)
# fig = c.profile_figure()
print(f'{c.area_v=:0.4f} m²')
