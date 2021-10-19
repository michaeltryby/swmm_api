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

    def set_crs(self, crs):
        self._crs = crs

    @property
    def geo_series(self) -> GeoSeries:
        return self.get_geo_series(self._crs)

    def get_geo_series(self, crs) -> GeoSeries:
        return GeoSeries({l: i.geo for l, i in self.items()}, crs=crs, name='geometry')  # .simplify(0.5)


########################################################################################################################
class CoordinateGeo(Coordinate):
    _section_class = InpSectionGeo

    @property
    def geo(self):
        return sh.Point(self.point)

    @classmethod
    def create_section_from_geoseries(cls, data: GeoSeries) -> InpSectionGeo:
        return cls.create_section(zip(data.index, data.x, data.y))


class VerticesGeo(Vertices):
    _section_class = InpSectionGeo

    @property
    def geo(self):
        return sh.LineString(self.vertices)

    @classmethod
    def create_section_from_geoseries(cls, data: GeoSeries) -> InpSectionGeo:
        # geometry mit MultiLineString deswegen v[0] mit ersten und einzigen linestring zu verwenden
        s = cls.create_section()
        # s.update({i: Vertices(i, v) for i, v in zip(data.index, map(lambda i: list(i.coords), data.values))})
        s.add_multiple(s._section_object(i, list(v.coords)) for i, v in data.to_dict().items())
        return s


class PolygonGeo(Polygon):
    _section_class = InpSectionGeo

    @property
    def geo(self):
        return sh.Polygon(self.polygon)

    @classmethod
    def create_section_from_geoseries(cls, data: GeoSeries) -> InpSectionGeo:
        s = cls.create_section()
        s.add_multiple(s._section_object(i, [xy[0:2] for xy in list(p.coords)]) for i, p in data.exterior.iteritems())
        return s


########################################################################################################################
def convert_section_to_geosection(section: InpSection, crs="EPSG:32633") -> InpSectionGeo:
    di = {Coordinate: CoordinateGeo,
          Vertices: VerticesGeo,
          Polygon: PolygonGeo}
    old_type = section._section_object
    new_type = di[old_type]
    if old_type == new_type:
        section.set_crs(crs)
        return section
    new = new_type.create_section()  # type: InpSectionGeo
    new._data = {k: new_type(**vars(section[k])) for k in section}
    new.set_crs(crs)
    return new


# GeoPandas support for sections
geo_section_converter = {COORDINATES: CoordinateGeo, VERTICES: VerticesGeo, POLYGONS: PolygonGeo}


def add_geo_support(inp, crs="EPSG:32633"):
    for sec in [VERTICES, COORDINATES, POLYGONS]:
        if (sec in inp) and not isinstance(inp[sec], InpSectionGeo):
            inp[sec] = convert_section_to_geosection(inp[sec], crs=crs)


########################################################################################################################
def section_to_geopandas(section, crs="EPSG:32633"):
    return convert_section_to_geosection(section).get_geo_series(crs)


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
