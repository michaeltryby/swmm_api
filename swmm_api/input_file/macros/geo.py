from pyproj import Transformer

from . import links_dict
from ..sections import Vertices, Coordinate, Polygon
from ..section_labels import COORDINATES, VERTICES, POLYGONS


def transform_coordinates(inp, from_proj='epsg:31256', to_proj='epsg:32633'):
    # GK M34 to WGS 84 UTM zone 33N
    transformer = Transformer.from_crs(from_proj, to_proj, always_xy=True)
    # -----------------------------------
    if COORDINATES in inp:
        for node in inp[COORDINATES]:
            c = inp[COORDINATES][node]  # type: Coordinate
            c.x, c.y = transformer.transform(c.x, c.y)

    if VERTICES in inp:
        for link in inp[VERTICES]:
            v = inp[VERTICES][link]  # type: Vertices
            x, y = list(zip(*v.vertices))
            v.vertices = list(zip(*transformer.transform(x, y)))

    if POLYGONS in inp:
        for subcatchment in inp[POLYGONS]:
            p = inp[POLYGONS][subcatchment]  # type: Polygon
            x, y = list(zip(*p.polygon))
            p.polygon = list(zip(*transformer.transform(x, y)))


def update_vertices(inp):
    """
    add node coordinates to link vertices (start and end point)

    important for GIS export or GIS operations

    Notes:
        works inplace

    Args:
        inp (SwmmInput): inp data

    Returns:
        SwmmInput: changes inp data
    """
    links = links_dict(inp)
    coords = inp[COORDINATES]
    for l in links.values():  # type: Conduit # or Weir or Orifice or Pump or Outlet
        if l.Name not in inp[VERTICES]:
            object_type = inp[VERTICES]._section_object
            inp[VERTICES].add_obj(object_type(l.Name, vertices=list()))

        v = inp[VERTICES][l.Name].vertices
        inp[VERTICES][l.Name].vertices = [coords[l.FromNode].point] + v + [coords[l.ToNode].point]
    return inp
