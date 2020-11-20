from geopandas import GeoDataFrame

from ..inp_macros import update_vertices
from ..inp_reader import read_inp_file
from ..inp_sections import labels as s
from ..inp_sections.map_geodata import VerticesGeo, CoordinateGeo, PolygonGeo

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
 
# end = '.json'
# end = '.shp'
# end = '.gpkg'
"""


def convert_inp_to_geo_package(inp_fn, gpkg_fn=None, driver='GPKG', label_sep='.'):
    """

    Args:
        inp_fn (str):
        gpkg_fn (str):
        driver (str):
        label_sep (str): separator for attribute label between section header and object attribute.
            I.e. "JUNCTIONS.Elevation" with label_sep='.'
    """
    if gpkg_fn is None:
        gpkg_fn = inp_fn.replace('.inp', '.gpkg')

    todo_sections = ['read_inp_file', s.JUNCTIONS, s.STORAGE, s.OUTFALLS, s.CONDUITS, s.WEIRS, s.OUTLETS, s.ORIFICES, s.PUMPS,
                     s.SUBCATCHMENTS]
    print(*todo_sections, sep=' | ')

    inp = read_inp_file(inp_fn, custom_converter={s.VERTICES: VerticesGeo,
                                                  s.COORDINATES: CoordinateGeo,
                                                  s.POLYGONS: PolygonGeo})
    update_vertices(inp)

    print(f'{"done":^{len("read_inp_file")}s}', end=' | ')

    for sec in [s.JUNCTIONS, s.STORAGE, s.OUTFALLS]:
        if sec in inp:
            df = inp[sec].frame.rename(columns=lambda c: f'{sec}{label_sep}{c}')

            if sec == s.STORAGE:
                df[f'{s.STORAGE}{label_sep}Curve'] = df[f'{s.STORAGE}{label_sep}Curve'].astype(str)

            for sub_sec in [s.DWF, s.INFLOWS]:
                if sub_sec in inp:
                    x = inp[sub_sec].frame.unstack(1)
                    x.columns = [f'{label_sep}'.join([sub_sec, c[1], c[0]]) for c in x.columns]
                    df = df.join(x)
            df = df.join(inp[s.COORDINATES].geo_series)
            GeoDataFrame(df).to_file(gpkg_fn, driver=driver, layer=sec)
        print(f'{"done":^{len(sec)}s}', end=' | ')

    for sec in [s.CONDUITS, s.WEIRS, s.OUTLETS, s.ORIFICES, s.PUMPS]:
        if sec in inp:
            df = inp[sec].frame.rename(columns=lambda c: f'{sec}{label_sep}{c}').join(
                inp[s.XSECTIONS].frame.rename(columns=lambda c: f'{s.XSECTIONS}{label_sep}{c}'))

            if sec == s.OUTLETS:
                df[f'{s.OUTLETS}{label_sep}Curve'] = df[f'{s.OUTLETS}{label_sep}Curve'].astype(str)

            if s.LOSSES in inp:
                df = df.join(inp[s.LOSSES].frame.rename(columns=lambda c: f'{s.LOSSES}{label_sep}{c}'))
            df = df.join(inp[s.VERTICES].geo_series)
            GeoDataFrame(df).to_file(gpkg_fn, driver=driver, layer=sec)

        print(f'{"done":^{len(sec)}s}', end=' | ')

    if s.SUBCATCHMENTS in inp:
        GeoDataFrame(inp[s.SUBCATCHMENTS].frame.rename(columns=lambda c: f'{s.SUBCATCHMENTS}{label_sep}{c}').join(
            inp[s.SUBAREAS].frame.rename(columns=lambda c: f'{s.SUBAREAS}{label_sep}{c}')).join(
            inp[s.INFILTRATION].frame.rename(columns=lambda c: f'{s.INFILTRATION}{label_sep}{c}')).join(
            inp[s.POLYGONS].geo_series)).to_file(gpkg_fn, driver=driver, layer=s.SUBCATCHMENTS)

    print(f'{"done":^{len(s.SUBCATCHMENTS)}s}')
