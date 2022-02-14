from swmm_api import SwmmInput
from swmm_api.input_file.section_abr import SEC
from swmm_api.input_file.sections import FilesSection, BuildUp
from swmm_api.input_file.section_labels import FILES


inp = SwmmInput.read_file('epaswmm5_apps_manual/Example5-EMC.inp')
# inp.force_convert_all()
inp.test = 5
del inp.test
del inp.BUILDUP
del inp.CONDUITS
SEC.BUILDUP in inp
inp.BUILDUP
inp['BUILDUP'][('a', 'b')] = BuildUp('1', '2', '4', 1, 2, 3, 'AREA')
inp['BUILDUP'].add_obj(BuildUp('1', '2', '4', 1, 2, 3, 'AREA'))
inp.add_obj(BuildUp('1', '2', '4', 1, 2, 3, 'AREA'))
print(inp.to_string())
exit()



inp = SwmmInput()
# inp['FILES'] = {'USE HOTSTART': 'xxx.HSF'}
# inp[FILES] = FilesSection({'USE HOTSTART': 'xxx.HSF'})
inp[FILES]['USE HOTSTART'] = 'xxx.HSF'
print(inp.to_string())