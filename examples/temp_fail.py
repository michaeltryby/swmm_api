from swmm_api import SwmmInput

# inp = SwmmInput.read_file('epaswmm5_apps_manual/Example5-EMC.inp')
# inp.force_convert_all()
# inp.copy()

from swmm_api.input_file.sections import FilesSection
from swmm_api.input_file.section_labels import FILES

inp = SwmmInput()
# inp['FILES'] = {'USE HOTSTART': 'xxx.HSF'}
# inp[FILES] = FilesSection({'USE HOTSTART': 'xxx.HSF'})
inp[FILES]['USE HOTSTART'] = 'xxx.HSF'
print(inp.to_string())