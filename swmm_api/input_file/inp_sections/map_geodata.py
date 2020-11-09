import numpy as np
from geopandas import GeoSeries
from pandas import DataFrame
from shapely.geometry import Point, LineString, Polygon

from .node_component import Coordinate
from ..inp_helpers import InpSection

"""
TESTING:
not ready
"""


def coordinates_to_geopandas(section):
    return GeoSeries({l: Point(c.x, c.y) for l, c in section.items()}, crs="EPSG:32633")


def geopandas_to_coordinates(data):
    return Coordinate.create_section([[label, point.x, point.x] for label, point in data.iteritems()])


class CoordinatesSectionGeo(InpSection):
    @property
    def geo_series(self):
        df = self.frame
        return GeoSeries(index=df.index,
                         crs="EPSG:32633",
                         data=[Point(xy) for xy in zip(df['x'], df['y'])])

    @classmethod
    def from_geopandas(cls, data):
        x_name = 'x'
        y_name = 'y'
        df = DataFrame.from_dict({x_name: data.geometry.x, y_name: data.geometry.y})
        a = np.vstack((df.index.values, df.values.T)).T
        return CoordinatesSectionGeo.from_inp_lines(a, section_class=Coordinate)


class VerticesSectionGeo(InpSection):
    @property
    def geo_series(self):
        geometry = [list(Point(p.values()) for p in points) for points in self.values()]
        geometry = [LineString(list(tuple(p.values()) for p in points)) for points in self.values()]
        # sometimes ony 1 Point > raises error > LineString needs at least 2 Points
        return GeoSeries(index=self.keys(),
                         crs="EPSG:32633",
                         data=geometry)


class PolygonSectionGeo(InpSection):
    @property
    def geo_series(self):
        # geometry = [list(Point(p.values()) for p in points) for points in self.values()]
        geometry = [Polygon(list(tuple(p.values()) for p in points)) for points in self.values()]
        # sometimes ony 1 Point > raises error > LineString needs at least 2 Points
        return GeoSeries(index=self.keys(),
                         crs="EPSG:32633",
                         data=geometry)
