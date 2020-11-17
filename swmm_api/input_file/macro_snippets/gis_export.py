from ... import read_inp_file
from ..inp_sections.labels import *
from ..inp_sections.map_geodata import VerticesGeo, CoordinateGeo, PolygonGeo
from ..inp_macros import update_vertices
from geopandas import GeoDataFrame


def convert_inp_to_geo_package(inp_fn, gpkg_fn):
    inp = read_inp_file(inp_fn,
                        custom_converter={VERTICES: VerticesGeo,
                                          COORDINATES: CoordinateGeo,
                                          POLYGONS: PolygonGeo})

    update_vertices(inp)

    for sec in [JUNCTIONS, STORAGE, OUTFALLS]:
        if sec in inp:
            df = inp[sec].frame.rename(columns=lambda c: f'{sec}/{c}')

            if sec == STORAGE:
                df[f'{STORAGE}/Curve'] = df[f'{STORAGE}/Curve'].astype(str)

            for sub_sec in [DWF, INFLOWS]:
                if sub_sec in inp:
                    x = inp[sub_sec].frame.unstack(1)
                    x.columns = ['/'.join([sub_sec, c[1] , c[0]]) for c in x.columns]
                    df = df.join(x)
            df = df.join(inp[COORDINATES].geo_series)
            GeoDataFrame(df).to_file(gpkg_fn, driver="GPKG", layer=sec)

    for sec in [CONDUITS, WEIRS, OUTLETS, ORIFICES, PUMPS]:
        if sec in inp:
            df = inp[sec].frame.rename(columns=lambda c: f'{sec}/{c}').join(inp[XSECTIONS].frame.rename(columns=lambda c: f'{XSECTIONS}/{c}'))

            if sec == OUTLETS:
                df[f'{OUTLETS}/Curve'] = df[f'{OUTLETS}/Curve'].astype(str)

            if LOSSES in inp:
                df = df.join(inp[LOSSES].frame.rename(columns=lambda c: f'{LOSSES}/{c}'))
            df = df.join(inp[VERTICES].geo_series)
            GeoDataFrame(df).to_file(gpkg_fn, driver="GPKG", layer=sec)

    if SUBCATCHMENTS in inp:
        GeoDataFrame(inp[SUBCATCHMENTS].frame.rename(columns=lambda c: f'{SUBCATCHMENTS}/{c}').join(inp[SUBAREAS].frame.rename(columns=lambda c: f'{SUBAREAS}/{c}')).join(inp[INFILTRATION].frame.rename(columns=lambda c: f'{INFILTRATION}/{c}')).join(
            inp[POLYGONS].geo_series)).to_file(gpkg_fn, driver="GPKG", layer=SUBCATCHMENTS)
