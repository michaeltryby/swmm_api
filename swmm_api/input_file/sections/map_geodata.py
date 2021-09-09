import shapely.geometry as sh
from geopandas import GeoSeries

from . import Conduit, Vertices, Coordinate, Polygon
from ..section_labels import CONDUITS, VERTICES, COORDINATES, POLYGONS
from ..helpers import InpSection


class InpSectionGeo(InpSection):
    def __init__(self, section_object, crs="EPSG:32633"):
        """
        create an object for ``.inp``-file sections with objects (i.e. nodes, links, subcatchments, raingages, ...)

        Args:
            section_object (BaseSectionObject-like): object class which is stored in this section.
                This information is used to set the index of the section and
                to decide if the section can be exported (converted to a string) as a table.
        """
        InpSection.__init__(self, section_object)
        self._crs = crs

    @property
    def geo_series(self):
        return GeoSeries({l: i.geo for l, i in self.items()}, crs=self._crs, name='geometry')  # .simplify(0.5)


########################################################################################################################
class CoordinateGeo(Coordinate):
    _section_class = InpSectionGeo

    @property
    def geo(self):
        return sh.Point(self.point)


class VerticesGeo(Vertices):
    _section_class = InpSectionGeo

    @property
    def geo(self):
        return sh.LineString(self.vertices)


class PolygonGeo(Polygon):
    _section_class = InpSectionGeo

    @property
    def geo(self):
        return sh.Polygon(self.polygon)


########################################################################################################################
def convert_section_to_geosection(section: InpSection) -> InpSectionGeo:
    di = {Coordinate: CoordinateGeo,
          Vertices: VerticesGeo,
          Polygon: PolygonGeo}
    old_type = section._section_object
    new_type = di[old_type]
    new = new_type.create_section()
    new._data = {k: new_type(**vars(section[k])) for k in section}
    return new


########################################################################################################################
def add_geo_support(inp):
    for sec in [VERTICES, COORDINATES, POLYGONS]:
        if (sec in inp) and not isinstance(inp[sec], InpSectionGeo):
            inp[sec] = convert_section_to_geosection(inp[sec])


########################################################################################################################
def coordinates_to_geopandas(section, crs="EPSG:32633"):
    return GeoSeries({l: sh.Point(c.point) for l, c in section.items()}, crs=crs)


########################################################################################################################
def geopandas_to_coordinates(data: GeoSeries) -> InpSectionGeo:
    return CoordinateGeo.create_section(zip(data.index, data.x, data.y))


def geopandas_to_vertices(data: GeoSeries) -> InpSectionGeo:
    # geometry mit MultiLineString deswegen v[0] mit ersten und einzigen linestring zu verwenden
    s = VerticesGeo.create_section()
    # s.update({i: Vertices(i, v) for i, v in zip(data.index, map(lambda i: list(i.coords), data.values))})
    s.add_multiple(s._section_object(i, list(v.coords)) for i, v in data.to_dict().items())
    return s


def convert_polygon_shapely_to_swmm(poly):
    return [xy[0:2] for xy in list(poly.exterior.coords)]


def geopandas_to_polygons(data: GeoSeries) -> InpSectionGeo:
    # geometry mit MultiLineString deswegen v[0] mit ersten und einzigen linestring zu verwenden
    s = PolygonGeo.create_section()
    # s.update({i: Vertices(i, v) for i, v in zip(data.index, map(lambda i: list(i.coords), data.values))})
    # s.add_multiple(s._section_object(i, list(v.boundary.coords)) for i, v in data.to_dict().items())
    s.add_multiple(s._section_object(i, convert_polygon_shapely_to_swmm(v)) for i, v in data.to_dict().items())
    return s


########################################################################################################################
def remove_coordinates_from_vertices(inp):
    new_vertices_section = dict()
    for link in inp[VERTICES]:  # type: str
        conduit = inp[CONDUITS][link]  # type: Conduit
        new_vertices = list()
        n1 = inp[COORDINATES][conduit.FromNode]

        new_vertices.append(inp[COORDINATES][conduit.FromNode])
        new_vertices += inp[VERTICES][link].vertices
        new_vertices.append(inp[COORDINATES][conduit.ToNode])
        new_vertices_section[link] = new_vertices
    return new_vertices_section
