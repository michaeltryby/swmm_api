import shapely.geometry as sh
from geopandas import GeoSeries

from . import Conduit, Vertices, Coordinate, Polygon
from ..section_labels import CONDUITS, VERTICES, COORDINATES, POLYGONS
from ..helpers import InpSection


class InpSectionGeo(InpSection):
    """child class of :obj:`swmm_api.input_file.helpers.InpSection`. See parent class for all functions."""
    def __init__(self, section_object, crs="EPSG:32633"):
        """
        create a section for ``.inp``-file with geo-objects (i.e. nodes, links, subcatchments, raingages, ...)

        Args:
            section_object (BaseSectionObject-like): object class which is stored in this section.
                This information is used to set the index of the section and
                to decide if the section can be exported (converted to a string) as a table.
            crs: Coordinate Reference System of the geometry objects.
                Can be anything accepted by :meth:`pyproj.CRS.from_user_input() <pyproj.crs.CRS.from_user_input>`,
                such as an authority string (eg “EPSG:32633”) or a WKT string.
        """
        InpSection.__init__(self, section_object)
        self._crs = crs

    def set_crs(self, crs):
        """
        Set the Coordinate Reference System (CRS) of a geo-section.

        Notes:
            The underlying geometries are not transformed to this CRS.

        Args:
            crs: Coordinate Reference System of the geometry objects.
                Can be anything accepted by :meth:`pyproj.CRS.from_user_input() <pyproj.crs.CRS.from_user_input>`,
                such as an authority string (eg “EPSG:32633”) or a WKT string.
        """
        self._crs = crs

    @property
    def geo_series(self) -> GeoSeries:
        """
        Get a geopandas.GeoSeries representation for the geo-section.
        This function sets the object default crs.

        Returns:
            GeoSeries: geo-series of the section-data
        """
        return self.get_geo_series(self._crs)

    def get_geo_series(self, crs) -> GeoSeries:
        """
        get a geopandas.GeoSeries representation for the geo-section using a custom crs.

        Args:
            crs: Coordinate Reference System of the geometry objects.
                Can be anything accepted by :meth:`pyproj.CRS.from_user_input() <pyproj.crs.CRS.from_user_input>`,
                such as an authority string (eg “EPSG:32633”) or a WKT string.

        Returns:
            GeoSeries: geo-series of the section-data
        """
        return GeoSeries({label: item.geo for label, item in self.items()}, crs=crs, name='geometry')


########################################################################################################################
class CoordinateGeo(Coordinate):
    """child class of :obj:`.node_component.Coordinate`. See parent class for all functions."""
    _section_class = InpSectionGeo

    @property
    def geo(self):
        """
        get the shapely representation for the object (Point).

        Returns:
            shapely.geometry.Point: point object for the coordinates.
        """
        return sh.Point(self.point)

    @classmethod
    def create_section_from_geoseries(cls, data: GeoSeries) -> InpSectionGeo:
        """
        create a COORDINATES inp-file section for a geopandas.GeoSeries

        Args:
            data (GeoSeries): geopandas.GeoSeries of coordinates

        Returns:
            InpSectionGeo: COORDINATES inp-file section
        """
        return cls.create_section(zip(data.index, data.x, data.y))


class VerticesGeo(Vertices):
    """child class of :obj:`.link_component.Vertices`. See parent class for all functions."""
    _section_class = InpSectionGeo

    @property
    def geo(self):
        """
        get the shapely representation for the object (LineString).

        Returns:
            shapely.geometry.LineString: LineString object for the vertices.
        """
        return sh.LineString(self.vertices)

    @classmethod
    def create_section_from_geoseries(cls, data: GeoSeries) -> InpSectionGeo:
        """
        create a VERTICES inp-file section for a geopandas.GeoSeries

        Args:
            data (GeoSeries): geopandas.GeoSeries of coordinates

        Returns:
            InpSectionGeo: VERTICES inp-file section
        """
        # geometry mit MultiLineString deswegen v[0] mit ersten und einzigen linestring zu verwenden
        s = cls.create_section()
        # s.update({i: Vertices(i, v) for i, v in zip(data.index, map(lambda i: list(i.coords), data.values))})
        s.add_multiple(s._section_object(i, list(v.coords)) for i, v in data.to_dict().items())
        return s


class PolygonGeo(Polygon):
    """child class of :obj:`.subcatch.Polygon`. See parent class for all functions."""
    _section_class = InpSectionGeo

    @property
    def geo(self):
        """
        get the shapely representation for the object (Polygon).

        Returns:
            shapely.geometry.Polygon: LineString object for the polygon.
        """
        return sh.Polygon(self.polygon)

    @classmethod
    def create_section_from_geoseries(cls, data: GeoSeries) -> InpSectionGeo:
        """
        create a POLYGONS inp-file section for a geopandas.GeoSeries

        Warnings:
            Only uses the exterior coordinates and ignoring all interiors.

        Args:
            data (GeoSeries): geopandas.GeoSeries of polygons

        Returns:
            InpSectionGeo: POLYGONS inp-file section
        """
        s = cls.create_section()
        s.add_multiple(s._section_object(i, [xy[0:2] for xy in list(p.coords)]) for i, p in data.exterior.iteritems())
        return s


########################################################################################################################
def convert_section_to_geosection(section: InpSection, crs="EPSG:32633") -> InpSectionGeo:
    """
    converting the section into a geo-section

    Args:
        section (InpSection): section (only `VERTICES`, `COORDINATES`, `POLYGONS` sections)
        crs: Coordinate Reference System of the geometry objects.
                Can be anything accepted by :meth:`pyproj.CRS.from_user_input() <pyproj.crs.CRS.from_user_input>`,
                such as an authority string (eg “EPSG:32633”) or a WKT string.

    Returns:
        InpSectionGeo: geo-section
    """
    di = {Coordinate: CoordinateGeo,
          Vertices: VerticesGeo,
          Polygon: PolygonGeo}
    # base object of the section
    old_type = section._section_object  # type: swmm_api.input_file.helpers.BaseSectionObject
    new_type = di[old_type]
    # if already a geo-section
    if old_type == new_type:
        section.set_crs(crs)
        return section
    # create new section and set crs.
    new = new_type.create_section()  # type: InpSectionGeo
    new._data = {k: new_type(**vars(section[k])) for k in section}
    new.set_crs(crs)
    return new


# GeoPandas support for sections
geo_section_converter = {COORDINATES: CoordinateGeo, VERTICES: VerticesGeo, POLYGONS: PolygonGeo}


def add_geo_support(inp, crs="EPSG:32633"):
    """
    add geo-support to the inp-data

    Warnings:
        only for `VERTICES`, `COORDINATES`, `POLYGONS` sections

    Args:
        inp:
        crs: Coordinate Reference System of the geometry objects.
                Can be anything accepted by :meth:`pyproj.CRS.from_user_input() <pyproj.crs.CRS.from_user_input>`,
                such as an authority string (eg “EPSG:32633”) or a WKT string.
    """
    for sec in [VERTICES, COORDINATES, POLYGONS]:
        if (sec in inp) and not isinstance(inp[sec], InpSectionGeo):
            inp[sec] = convert_section_to_geosection(inp[sec], crs=crs)


########################################################################################################################
def section_to_geopandas(section, crs="EPSG:32633"):
    """
    convert a section into a GeoSeries.

    Warnings:
        only for `VERTICES`, `COORDINATES`, `POLYGONS` sections

    Args:
        section (InpSection | InpSectionGeo): section (only `VERTICES`, `COORDINATES`, `POLYGONS`)
        crs: Coordinate Reference System of the geometry objects.
                Can be anything accepted by :meth:`pyproj.CRS.from_user_input() <pyproj.crs.CRS.from_user_input>`,
                such as an authority string (eg “EPSG:32633”) or a WKT string.

    Returns:
        geopandas.GeoSeries: geo-data
    """
    return convert_section_to_geosection(section).get_geo_series(crs)


########################################################################################################################
def remove_coordinates_from_vertices(inp):
    # SNIPPET ?!?
    new_vertices_section = dict()
    for link in inp[VERTICES]:  # type: str
        conduit = inp[CONDUITS][link]  # type: Conduit
        new_vertices = list()
        # n1 = inp[COORDINATES][conduit.FromNode]
        new_vertices.append(inp[COORDINATES][conduit.FromNode])
        new_vertices += inp[VERTICES][link].vertices
        new_vertices.append(inp[COORDINATES][conduit.ToNode])
        new_vertices_section[link] = new_vertices
    return new_vertices_section
