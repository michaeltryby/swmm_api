from .collection import links_dict
from .macros import find_link
from ..misc.curve_simplification import _vec2d_dist, ramer_douglas
from ..sections import Vertices, Coordinate, Polygon
from ..section_labels import COORDINATES, VERTICES, POLYGONS, CONDUITS


def transform_coordinates(inp, from_proj='epsg:31256', to_proj='epsg:32633'):
    """
    transform all coordinates of the sections COORDINATES, VERTICES and POLYGONS from one projection to another.

    Args:
        inp (swmm_api.SwmmInput): SWMM input data
        from_proj (str): Projection of data
        to_proj (str): Projection for resulting data

    .. Important::
        works inplace
    """
    from pyproj import Transformer
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


def complete_link_vertices(inp, label_link):
    """
    add node coordinates to vertices of a single link (start and end point)

    .. Important::
        works inplace

    Args:
        inp (swmm_api.SwmmInput): SWMM input data
        label_link (str): label of the link
    """
    link = find_link(inp, label_link)
    inp[VERTICES][label_link].vertices = ([inp[COORDINATES][link.FromNode].point] +
                                          inp[VERTICES][label_link].vertices +
                                          [inp[COORDINATES][link.ToNode].point])


def complete_vertices(inp):
    """
    add node coordinates to vertices of all links (start and end point)

    important for GIS export or GIS operations

    .. Important::
        works inplace

    Args:
        inp (swmm_api.SwmmInput): SWMM input data
    """
    if COORDINATES in inp:
        links = links_dict(inp)
        if links:
            if VERTICES not in inp:
                inp[VERTICES] = Vertices.create_section()

            object_type = inp[VERTICES]._section_object

            for label_link in links:  # type: Conduit # or Weir or Orifice or Pump or Outlet
                if label_link not in inp[VERTICES]:
                    inp[VERTICES].add_obj(object_type(label_link, vertices=list()))
                complete_link_vertices(inp, label_link)


def reduce_vertices(inp, node_range=0.25):
    """
    remove first and last vertices to keep only inner vertices (SWMM standard)

    important if data originally from GIS and export to SWMM

    Args:
        inp (swmm_api.SwmmInput): SWMM input data
        node_range (float): minimal distance in m from the first and last vertices to the end nodes

    .. Important::
        works inplace
    """
    links = links_dict(inp)

    for link_label in inp.VERTICES:
        l = links[link_label]
        v = inp[VERTICES][link_label].vertices
        p = inp[COORDINATES][l.FromNode].point
        if _vec2d_dist(p, v[0]) < node_range:
            v = v[1:]

        if v:
            p = inp[COORDINATES][l.ToNode].point
            if _vec2d_dist(p, v[-1]) < node_range:
                v = v[:-1]

        if v:
            inp[VERTICES][link_label].vertices = v
        else:
            del inp[VERTICES][link_label]


def remove_coordinates_from_vertices(inp):
    # SNIPPET ?!?
    new_vertices_section = {}
    for link in inp[VERTICES]:  # type: str
        conduit = inp[CONDUITS][link]  # type: Conduit
        new_vertices = []
        # n1 = inp[COORDINATES][conduit.FromNode]
        new_vertices.append(inp[COORDINATES][conduit.FromNode])
        new_vertices += inp[VERTICES][link].vertices
        new_vertices.append(inp[COORDINATES][conduit.ToNode])
        new_vertices_section[link] = new_vertices
    return new_vertices_section


def simplify_link_vertices(vertices, dist=1.):
    """
    removes unneeded vertices with the Ramer-Douglas simplification

    Args:
        vertices (Vertices): vertices-object of link
        dist (float): threshold of algorythm

    .. Important::
        works inplace
    """
    vertices.vertices = ramer_douglas(vertices.vertices, dist)


def simplify_vertices(inp, dist=1.):
    """
    removes unneeded vertices with the Ramer-Douglas simplification

    Args:
        inp (swmm_api.SwmmInput): SWMM input data
        dist (float):  threshold of algorythm

    .. Important::
        works inplace
    """
    for v in inp.VERTICES:
        simplify_link_vertices(inp.VERTICES[v], dist)
