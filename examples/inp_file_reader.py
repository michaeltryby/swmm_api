from swmm_api.input_file import read_inp_file
from swmm_api.input_file.inp_sections.labels import *
from swmm_api.input_file.inp_sections.map_geodata import (VerticesGeo, CoordinateGeo,
                                                          PolygonGeo, )
from swmm_api.input_file.inp_macros import update_vertices
from swmm_api.input_file.inp_writer import write_inp_file
from swmm_api.input_file.macro_snippets.gis_export import convert_inp_to_geo_package
from swmm_api.run import swmm5_run

inp = read_inp_file('epaswmm5_apps_manual/Example7-Final.inp',
                    custom_converter={VERTICES: VerticesGeo,
                                      COORDINATES: CoordinateGeo,
                                      POLYGONS: PolygonGeo})

update_vertices(inp)

write_inp_file(inp, 'temp.inp')
swmm5_run('temp.inp')
