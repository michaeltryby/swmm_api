from mp.helpers.check_time import Timer
from swmm_api import read_inp_file
from ..inp_sections.labels import *
from ..inp_sections.map_geodata import VerticesGeo, CoordinateGeo, PolygonGeo
from ..inp_macros import update_vertices
from geopandas import GeoDataFrame

"""
{'AeronavFAA': 'r',
 'ARCGEN': 'r',
 'BNA': 'raw',
 'DXF': 'raw',
 'CSV': 'raw',
 'OpenFileGDB': 'r',
 'ESRIJSON': 'r',
 'ESRI Shapefile': 'raw',
 'GeoJSON': 'rw',
 'GPKG': 'rw',
 'GML': 'raw',
 'GPX': 'raw',
 'GPSTrackMaker': 'raw',
 'Idrisi': 'r',
 'MapInfo File': 'raw',
 'DGN': 'raw',
 'S57': 'r',
 'SEGY': 'r',
 'SUA': 'r',
 'TopoJSON': 'r'}
"""


def convert_inp_to_geo_package(inp_fn, gpkg_fn=None, driver='GeoJSON'):
    if gpkg_fn is None:
        gpkg_fn = inp_fn.replace('.inp', '.gpkg')

    end = '.gpkg'
    end = '.shp'
    end = '.json.zip'

    gpkg_fn = gpkg_fn.replace('.gpkg', '')

    todo_sections = ['read_inp_file', JUNCTIONS, STORAGE, OUTFALLS, CONDUITS, WEIRS, OUTLETS, ORIFICES, PUMPS, SUBCATCHMENTS]
    # print(*todo_sections, sep=' | ')

    inp = read_inp_file(inp_fn,
                        custom_converter={VERTICES: VerticesGeo,
                                          COORDINATES: CoordinateGeo,
                                          POLYGONS: PolygonGeo})
    update_vertices(inp)

    # print(f'{"done":^{len("read_inp_file")}s}', end=' | ')

    sep='.'

    for sec in [JUNCTIONS, STORAGE, OUTFALLS]:
        if sec in inp:
            with Timer(sec):
                df = inp[sec].frame.rename(columns=lambda c: f'{sec}{sep}{c}')

                if sec == STORAGE:
                    df[f'{STORAGE}{sep}Curve'] = df[f'{STORAGE}{sep}Curve'].astype(str)

                for sub_sec in [DWF, INFLOWS]:
                    if sub_sec in inp:
                        x = inp[sub_sec].frame.unstack(1)
                        x.columns = [{sep}.join([sub_sec, c[1] , c[0]]) for c in x.columns]
                        df = df.join(x)
                df = df.join(inp[COORDINATES].geo_series)
            with Timer(sec + ' to_file'):
                # GeoDataFrame(df).to_file(gpkg_fn, driver=driver, layer=sec)
                GeoDataFrame(df).to_file(gpkg_fn + '_' + sec + end, driver=driver)
        # print(f'{"done":^{len(sec)}s}', end=' | ')

    for sec in [CONDUITS, WEIRS, OUTLETS, ORIFICES, PUMPS]:
        if sec in inp:
            with Timer(sec):
                df = inp[sec].frame.rename(columns=lambda c: f'{sec}{sep}{c}').join(inp[XSECTIONS].frame.rename(columns=lambda c: f'{XSECTIONS}{sep}{c}'))

                if sec == OUTLETS:
                    df[f'{OUTLETS}{sep}Curve'] = df[f'{OUTLETS}{sep}Curve'].astype(str)

                if LOSSES in inp:
                    df = df.join(inp[LOSSES].frame.rename(columns=lambda c: f'{LOSSES}{sep}{c}'))
                df = df.join(inp[VERTICES].geo_series)
            with Timer(sec + ' to_file'):
                # GeoDataFrame(df).to_file(gpkg_fn, driver=driver, layer=sec)
                GeoDataFrame(df).to_file(gpkg_fn + '_' + sec + end, driver=driver)

        # print(f'{"done":^{len(sec)}s}', end=' | ')

    if SUBCATCHMENTS in inp:
        with Timer(SUBCATCHMENTS):
            GeoDataFrame(inp[SUBCATCHMENTS].frame.rename(columns=lambda c: f'{SUBCATCHMENTS}{sep}{c}').join(inp[SUBAREAS].frame.rename(columns=lambda c: f'{SUBAREAS}{sep}{c}')).join(inp[INFILTRATION].frame.rename(columns=lambda c: f'{INFILTRATION}{sep}{c}')).join(
                inp[POLYGONS].geo_series)).to_file(gpkg_fn + '_' + SUBCATCHMENTS + end, driver=driver)#, layer=SUBCATCHMENTS)

    # print(f'{"done":^{len(SUBCATCHMENTS)}s}')
