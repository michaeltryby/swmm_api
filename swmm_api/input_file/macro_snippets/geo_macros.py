from pyproj import Transformer

from swmm_api.input_file.inp_sections import Vertices, Coordinate
from swmm_api.input_file.inp_sections.labels import COORDINATES, VERTICES


def transform_coordinates(inp, from_proj='epsg:31256', to_proj='epsg:32633'):
    # GK M34 to WGS 84 UTM zone 33N
    transformer = Transformer.from_crs(from_proj, to_proj, always_xy=True)
    # -----------------------------------
    if COORDINATES in inp:
        for node in inp[COORDINATES]:
            c = inp[COORDINATES][node] # type: Coordinate
            c.x, c.y = transformer.transform(c.x, c.y)

    if VERTICES in inp:
        for link in inp[VERTICES]:
            v = inp[VERTICES][link]  # type: Vertices
            x,y = list(zip(*v.vertices))
            v.vertices = list(zip(*transformer.transform(x, y)))
