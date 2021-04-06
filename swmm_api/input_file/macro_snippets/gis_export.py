from geopandas import GeoDataFrame

from ..macros import update_vertices, filter_nodes, filter_links
from ... import read_inp_file
from .. import section_labels as s
from ..sections.map_geodata import (VerticesGeo, CoordinateGeo, PolygonGeo, InpSectionGeo,
                                    convert_section_to_geosection, )

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

    inp = read_inp_file(inp_fn, custom_converter={s.VERTICES: VerticesGeo,
                                                  s.COORDINATES: CoordinateGeo,
                                                  s.POLYGONS: PolygonGeo})

    write_geo_package(inp, gpkg_fn, driver=driver, label_sep=label_sep)


def write_geo_package(inp, gpkg_fn, driver='GPKG', label_sep='.'):

    todo_sections = [s.JUNCTIONS, s.STORAGE, s.OUTFALLS, s.CONDUITS, s.WEIRS, s.OUTLETS, s.ORIFICES, s.PUMPS,
                     s.SUBCATCHMENTS]
    print(*todo_sections, sep=' | ')

    for sec in [s.VERTICES, s.COORDINATES, s.POLYGONS]:
        if (sec in inp) and not isinstance(inp[sec], InpSectionGeo):
            inp[sec] = convert_section_to_geosection(inp[sec])

    update_vertices(inp)

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


def problems_to_gis(inp, gpkg_fn, nodes=None, links=None, **kwargs):
    if nodes is not None:
        inp = filter_nodes(inp, nodes)

    if links is not None:
        inp = filter_links(inp, links)

    write_geo_package(inp, gpkg_fn, **kwargs)
