import shapely.geometry as sh
from geopandas import GeoSeries

from . import Conduit, Vertices, Coordinate, Polygon
from ..section_labels import CONDUITS, VERTICES, COORDINATES
from ..helpers import InpSection

"""
TESTING:
not ready
"""


class InpSectionGeo(InpSection):
    @property
    def geo_series(self):
        return GeoSeries({l: i.geo for l, i in self.items()}, crs="EPSG:32633", name='geometry')  # .simplify(0.5)


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


def convert_section_to_geosection(section: InpSection) -> InpSectionGeo:
    di = {Coordinate: CoordinateGeo,
          Vertices: VerticesGeo,
          Polygon: PolygonGeo}
    old_type = section._section_object
    new_type = di[old_type]
    new = new_type.create_section()
    new._data = {k: new_type(**vars(section[k])) for k in section}
    return new


def coordinates_to_geopandas(section):
    return GeoSeries({l: sh.Point(c.point) for l, c in section.items()}, crs="EPSG:32633")


def geopandas_to_coordinates(data: GeoSeries) -> InpSectionGeo:
    return CoordinateGeo.create_section(zip(data.index, data.x, data.y))


def geopandas_to_vertices(data: GeoSeries) -> InpSectionGeo:
    # geometry mit MultiLineString deswegen v[0] mit ersten und einzigen linestring zu verwenden
    s = VerticesGeo.create_section()
    # s.update({i: Vertices(i, v) for i, v in zip(data.index, map(lambda i: list(i.coords), data.values))})
    s.add_multiple(s._section_object(i, list(v.coords)) for i, v in data.to_dict().items())
    return s


def geopandas_to_polygons(data: GeoSeries) -> InpSectionGeo:
    # geometry mit MultiLineString deswegen v[0] mit ersten und einzigen linestring zu verwenden
    s = PolygonGeo.create_section()
    # s.update({i: Vertices(i, v) for i, v in zip(data.index, map(lambda i: list(i.coords), data.values))})
    s.add_multiple(s._section_object(i, list(v.boundary.coords)) for i, v in data.to_dict().items())
    return s


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


# class CoordinatesSectionGeo(InpSection):
#     @property
#     def geo_series(self):
#         df = self.frame
#         return GeoSeries(index=df.index,
#                          crs="EPSG:32633",
#                          data=[sh.Point(xy) for xy in zip(df['x'], df['y'])])
#
#     @classmethod
#     def from_geopandas(cls, data):
#         x_name = 'x'
#         y_name = 'y'
#         df = DataFrame.from_dict({x_name: data.geometry.x, y_name: data.geometry.y})
#         a = np.vstack((df.index.values, df.values.T)).T
#         return CoordinatesSectionGeo.from_inp_lines(a, section_class=Coordinate)
#
#
# class VerticesSectionGeo(InpSection):
#     @property
#     def geo_series(self):
#         geometry = [list(sh.Point(p.values()) for p in points) for points in self.values()]
#         geometry = [sh.LineString(list(tuple(p.values()) for p in points)) for points in self.values()]
#         # sometimes ony 1 Point > raises error > LineString needs at least 2 Points
#         return GeoSeries(index=self.keys(),
#                          crs="EPSG:32633",
#                          data=geometry)
#
#
# class PolygonSectionGeo(InpSection):
#     @property
#     def geo_series(self):
#         # geometry = [list(Point(p.values()) for p in points) for points in self.values()]
#         geometry = [sh.Polygon(list(tuple(p.values()) for p in points)) for points in self.values()]
#         # sometimes ony 1 Point > raises error > LineString needs at least 2 Points
#         return GeoSeries(index=self.keys(),
#                          crs="EPSG:32633",
#                          data=geometry)
