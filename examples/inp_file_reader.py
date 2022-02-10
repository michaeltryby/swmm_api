from swmm_api import read_inp_file
from swmm_api.input_file.section_labels import *
from swmm_api.input_file.sections.map_geodata import (VerticesGeo, CoordinateGeo,
                                                      PolygonGeo, )
from swmm_api.input_file.macros.geo import complete_vertices
from swmm_api.run import swmm5_run

inp = read_inp_file('/home/markus/PycharmProjects/swmm_api/examples/internal/2015_06_17_UG_Weiz_OPTI_maxAbk_Ret_3J_60_KW.inp')
exit()

inp = read_inp_file('epaswmm5_apps_manual/Example7-Final.inp',
                    custom_converter={VERTICES: VerticesGeo,
                                      COORDINATES: CoordinateGeo,
                                      POLYGONS: PolygonGeo})

complete_vertices(inp)

inp.write_file('temp.inp')
swmm5_run('temp.inp')
