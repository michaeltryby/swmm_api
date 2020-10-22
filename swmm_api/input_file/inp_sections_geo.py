from swmm_api.input_file.inp_sections_generic import CoordinatesSection, VerticesSection, PolygonSection
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon

"""
TESTING:
not ready
"""


class CoordinatesSectionGeo(CoordinatesSection):
    @property
    def geo_series(self):
        df = self.data_frame
        return gpd.GeoSeries(index=df.index,
                             crs="EPSG:32633",
                             data=[Point(xy) for xy in zip(df['x'], df['y'])])


class VerticesSectionGeo(VerticesSection):
    @property
    def geo_series(self):
        geometry = [list(Point(p.values()) for p in points) for points in self.values()]
        geometry = [LineString(list(tuple(p.values()) for p in points)) for points in self.values()]
        # sometimes ony 1 Point > raises error > LineString needs at least 2 Points
        return gpd.GeoSeries(index=self.keys(),
                             crs="EPSG:32633",
                             data=geometry)


class PolygonSectionGeo(PolygonSection):
    @property
    def geo_series(self):
        # geometry = [list(Point(p.values()) for p in points) for points in self.values()]
        geometry = [Polygon(list(tuple(p.values()) for p in points)) for points in self.values()]
        # sometimes ony 1 Point > raises error > LineString needs at least 2 Points
        return gpd.GeoSeries(index=self.keys(),
                             crs="EPSG:32633",
                             data=geometry)
