from swmm_api import read_inp_file
from swmm_api.input_file.section_labels import *
from swmm_api.input_file.sections.map_geodata import (VerticesGeo, CoordinateGeo,
                                                      PolygonGeo, )
from swmm_api.input_file.macros.geo import update_vertices
from swmm_api.run import swmm5_run

inp = read_inp_file('epaswmm5_apps_manual/Example7-Final.inp',
                    custom_converter={VERTICES: VerticesGeo,
                                      COORDINATES: CoordinateGeo,
                                      POLYGONS: PolygonGeo})

update_vertices(inp)

inp.write_file('temp.inp')
swmm5_run('temp.inp')
