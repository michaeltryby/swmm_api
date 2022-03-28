import inspect
import time

from numpy import NaN
from pandas import MultiIndex
from tqdm.auto import tqdm

from .geo import complete_vertices, simplify_vertices, reduce_vertices
from .tags import get_node_tags, get_link_tags, get_subcatchment_tags
from ..inp import SwmmInput
from ..section_labels import *
from ..section_lists import LINK_SECTIONS, NODE_SECTIONS
from ..section_types import SECTION_TYPES
from ..sections import Tag

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


def set_crs(inp, crs="EPSG:32633"):
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
        if sec in inp:
            inp[sec].set_crs(crs=crs)


def convert_inp_to_geo_package(inp_fn, gpkg_fn=None, driver='GPKG', label_sep='.', crs="EPSG:32633"):
    """
    convert inp file data from an .inp-file to a GIS database

    Args:
        inp_fn (str): filename of the SWMM inp file
        gpkg_fn (str): filename of the new geopackage file
        driver (str): The OGR format driver used to write the vector file. (see: fiona.supported_drivers)
        label_sep (str): separator for attribute label between section header and object attribute.
            I.e. "JUNCTIONS.Elevation" with label_sep='.'
        crs (str): Coordinate Reference System of the geometry objects.
                    Can be anything accepted by pyproj.CRS.from_user_input(),
                    such as an authority string (eg “EPSG:4326”) or a WKT string.
    """
    if gpkg_fn is None:
        gpkg_fn = inp_fn.replace('.inp', '.gpkg')

    inp = SwmmInput.read_file(inp_fn)

    write_geo_package(inp, gpkg_fn, driver=driver, label_sep=label_sep, crs=crs)


def write_geo_package(inp, gpkg_fn, driver='GPKG', label_sep='.', crs="EPSG:32633"):
    """
    write the inp file data to a GIS database

    Args:
        inp (SwmmInput): inp file data
        gpkg_fn (str): filename of the new geopackage file
        driver (str): The OGR format driver used to write the vector file. (see: fiona.supported_drivers)
        label_sep (str): separator for attribute label between section header and object attribute.
            I.e. "JUNCTIONS.Elevation" with label_sep='.'
        crs (str): Coordinate Reference System of the geometry objects.
                    Can be anything accepted by pyproj.CRS.from_user_input(),
                    such as an authority string (eg “EPSG:4326”) or a WKT string.
    """
    from geopandas import GeoDataFrame

    todo_sections = NODE_SECTIONS + LINK_SECTIONS + [SUBCATCHMENTS]
    print(*todo_sections, sep=' | ')

    set_crs(inp, crs=crs)

    # ---------------------------------
    t0 = time.perf_counter()
    nodes_tags = get_node_tags(inp)
    if COORDINATES in inp:
        for sec in NODE_SECTIONS:
            if sec in inp:
                df = inp[sec].frame.rename(columns=lambda c: f'{sec}{label_sep}{c}')

                if sec == STORAGE:
                    df[f'{STORAGE}{label_sep}Curve'] = df[f'{STORAGE}{label_sep}Curve'].astype(str)

                for sub_sec in [DWF, INFLOWS]:
                    if sub_sec in inp:
                        x = inp[sub_sec].frame.unstack(1)
                        x.columns = [f'{label_sep}'.join([sub_sec, c[1], c[0]]) for c in x.columns]
                        df = df.join(x)

                df = df.join(inp[COORDINATES].geo_series).join(nodes_tags)

                GeoDataFrame(df).to_file(gpkg_fn, driver=driver, layer=sec)
                print(f'{f"{time.perf_counter() - t0:0.1f}s":^{len(sec)}s}', end=' | ')
            else:
                print(f'{f"-":^{len(sec)}s}', end=' | ')
            t0 = time.perf_counter()

        # ---------------------------------
        links_tags = get_link_tags(inp)
        complete_vertices(inp)
        simplify_vertices(inp)
        for sec in LINK_SECTIONS:
            if sec in inp:
                df = inp[sec].frame.rename(columns=lambda c: f'{sec}{label_sep}{c}').join(
                    inp[XSECTIONS].frame.rename(columns=lambda c: f'{XSECTIONS}{label_sep}{c}'))

                if sec == OUTLETS:
                    df[f'{OUTLETS}{label_sep}Curve'] = df[f'{OUTLETS}{label_sep}Curve'].astype(str)

                if LOSSES in inp:
                    df = df.join(inp[LOSSES].frame.rename(columns=lambda c: f'{LOSSES}{label_sep}{c}'))

                df = df.join(inp[VERTICES].geo_series).join(links_tags)

                GeoDataFrame(df).to_file(gpkg_fn, driver=driver, layer=sec)

                print(f'{f"{time.perf_counter() - t0:0.1f}s":^{len(sec)}s}', end=' | ')
            else:
                print(f'{f"-":^{len(sec)}s}', end=' | ')
            t0 = time.perf_counter()
    else:
        for sec in NODE_SECTIONS + LINK_SECTIONS:
            print(f'{f"-":^{len(sec)}s}', end=' | ')
    # ---------------------------------
    if POLYGONS in inp:
        df = inp[SUBCATCHMENTS].frame.rename(columns=lambda c: f'{SUBCATCHMENTS}{label_sep}{c}').join(
            inp[SUBAREAS].frame.rename(columns=lambda c: f'{SUBAREAS}{label_sep}{c}')).join(
            inp[INFILTRATION].frame.rename(columns=lambda c: f'{INFILTRATION}{label_sep}{c}')).join(
            inp[POLYGONS].geo_series).join(get_subcatchment_tags(inp))

        GeoDataFrame(df).to_file(gpkg_fn, driver=driver, layer=SUBCATCHMENTS)
        gs_connector = get_subcatchment_connectors(inp)
        GeoDataFrame(gs_connector).to_file(gpkg_fn, driver=driver, layer=SUBCATCHMENTS + '_connector')

        print(f'{f"{time.perf_counter() - t0:0.1f}s":^{len(SUBCATCHMENTS)}s}')
    else:
        print(f'{f"-":^{len(SUBCATCHMENTS)}s}', end=' | ')


def get_subcatchment_connectors(inp):
    """
    create connector line objects between subcatchment outlets and centroids

    Args:
        inp (SwmmInput): inp file data

    Returns:
        geopandas.GeoSeries: line objects between subcatchment outlets and centroids
    """
    # centroids = inp[s.POLYGONS].geo_series.centroid
    # outlets = inp[s.SUBCATCHMENTS].frame.Outlet
    # junctions = inp[s.COORDINATES].geo_series.reindex(outlets.values)
    # junctions.index = outlets.index
    from geopandas import GeoSeries
    from shapely.geometry import LineString

    res = {}
    for p in tqdm(inp[POLYGONS], total=len(inp[POLYGONS].keys()), desc='get_subcatchment_connectors'):
        c = inp[POLYGONS][p].geo.centroid
        o = inp[SUBCATCHMENTS][p].Outlet
        if o not in inp[COORDINATES]:
            print(inp[SUBCATCHMENTS][p])
            continue
        res[p] = LineString([inp[COORDINATES][o].point, (c.x, c.y)])

    gs = GeoSeries(res, crs=inp[POLYGONS]._crs)
    gs.index.name = 'Subcatchment'
    gs.name = 'geometry'
    return gs


def links_geo_data_frame(inp, label_sep='.'):
    """
    convert link data in inp file to geo-data-frame

    Args:
        inp (SwmmInput): inp file data
        label_sep (str): separator for attribute label between section header and object attribute.
            I.e. "JUNCTIONS.Elevation" with label_sep='.'

    Returns:
        geopandas.GeoDataFrame: links as geo-data-frame
    """
    from geopandas import GeoDataFrame

    links_tags = get_link_tags(inp)
    complete_vertices(inp)
    res = None
    for sec in LINK_SECTIONS:
        if sec in inp:
            df = inp[sec].frame.rename(columns=lambda c: f'{sec}{label_sep}{c}').join(
                inp[XSECTIONS].frame.rename(columns=lambda c: f'{XSECTIONS}{label_sep}{c}'))

            if sec == OUTLETS:
                df[f'{OUTLETS}{label_sep}Curve'] = df[f'{OUTLETS}{label_sep}Curve'].astype(str)

            if LOSSES in inp:
                df = df.join(inp[LOSSES].frame.rename(columns=lambda c: f'{LOSSES}{label_sep}{c}'))

            df = df.join(inp[VERTICES].geo_series).join(links_tags)
            if res is None:
                res = df
            else:
                res = res.append(df)
    return GeoDataFrame(res)


def nodes_geo_data_frame(inp, label_sep='.'):
    """
    convert nodes data in inp file to geo-data-frame

    Args:
        inp (SwmmInput): inp file data
        label_sep (str): separator for attribute label between section header and object attribute.
            I.e. "JUNCTIONS.Elevation" with label_sep='.'

    Returns:
        geopandas.GeoDataFrame: nodes as geo-data-frame
    """
    from geopandas import GeoDataFrame

    nodes_tags = get_node_tags(inp)
    res = None
    for sec in NODE_SECTIONS:
        if sec in inp:
            df = inp[sec].frame.rename(columns=lambda c: f'{sec}{label_sep}{c}')

            if sec == STORAGE:
                df[f'{STORAGE}{label_sep}Curve'] = df[f'{STORAGE}{label_sep}Curve'].astype(str)

            for sub_sec in [DWF, INFLOWS]:
                if sub_sec in inp:
                    x = inp[sub_sec].frame.unstack(1)
                    x.columns = [f'{label_sep}'.join([sub_sec, c[1], c[0]]) for c in x.columns]
                    df = df.join(x)

            df = df.join(inp[COORDINATES].geo_series).join(nodes_tags)

            if res is None:
                res = df
            else:
                res = res.append(df)

    return GeoDataFrame(res)


def gpkg_to_swmm(fn, label_sep='.'):
    """
    import inp data from GIS gpkg file created from the swmm_api.input_file.macro_snippets.gis_export.convert_inp_to_geo_package function

    Args:
        fn (str): filename to GPKG datebase file
        label_sep (str):  separator for attribute label between section header and object attribute.
            I.e. "JUNCTIONS.Elevation" with label_sep='.'

    Returns:
        SwmmInput: inp data
    """
    import fiona
    from geopandas import read_file

    inp = SwmmInput()

    for sec in NODE_SECTIONS:
        if sec not in fiona.listlayers(fn):
            continue
        gdf = read_file(fn, layer=sec).set_index('Name')

        cols = gdf.columns[gdf.columns.str.startswith(sec)]
        inp[sec] = SECTION_TYPES[sec].create_section(gdf[cols].reset_index().fillna(NaN).values)

        for sub_sec in [DWF, INFLOWS]:
            cols = gdf.columns[gdf.columns.str.startswith(sub_sec)]
            gdf_sub = gdf[cols].copy()
            gdf_sub.columns = MultiIndex.from_tuples([col.split(label_sep) for col in gdf_sub.columns])
            cols_order = gdf_sub.columns.droplevel(1)
            gdf_sub = gdf_sub.stack(1)[cols_order]
            inp[sub_sec].update(SECTION_TYPES[sub_sec].create_section(gdf_sub.reset_index().values))

        inp[COORDINATES].update(SECTION_TYPES[COORDINATES].create_section_from_geoseries(gdf.geometry))

        tags = gdf[['tag']].copy()
        tags['type'] = Tag.TYPES.Node
        inp[TAGS].update(SECTION_TYPES[TAGS].create_section(tags[['type', 'tag']].reset_index().values))

    for i in inp[STORAGE]:
        c = inp[STORAGE][i].Curve
        if isinstance(c, list):
            inp[STORAGE][i].Curve = [float(j) for j in c[0][1:-1].split(',')]

    # ---------------------------------
    for sec in LINK_SECTIONS:
        if sec not in fiona.listlayers(fn):
            continue
        gdf = read_file(fn, layer=sec).set_index('Name')

        cols = gdf.columns[gdf.columns.str.startswith(sec)]
        inp[sec] = SECTION_TYPES[sec].create_section(gdf[cols].reset_index().fillna(NaN).values)

        for sub_sec in [XSECTIONS, LOSSES]:
            cols = gdf.columns[gdf.columns.str.startswith(sub_sec)].to_list()
            if cols:
                if sub_sec == XSECTIONS:
                    cols = [f'{sub_sec}{label_sep}{i}' for i in inspect.getargspec(SECTION_TYPES[sub_sec]).args[2:]]
                gdf_sub = gdf[cols].copy().dropna(how='all')
                if sub_sec == LOSSES:
                    gdf_sub[f'{LOSSES}{label_sep}FlapGate'] = gdf_sub[f'{LOSSES}{label_sep}FlapGate'] == 1
                inp[sub_sec].update(SECTION_TYPES[sub_sec].create_section(gdf_sub.reset_index().values))

        inp[VERTICES].update(SECTION_TYPES[VERTICES].create_section_from_geoseries(gdf.geometry))

        tags = gdf[['tag']].copy()
        tags['type'] = Tag.TYPES.Link
        inp[TAGS].update(SECTION_TYPES[TAGS].create_section(tags[['type', 'tag']].reset_index().values))

    if OUTLETS in inp:
        for i in inp[OUTLETS]:
            c = inp[OUTLETS][i].Curve
            if isinstance(c, list):
                inp[OUTLETS][i].Curve = [float(j) for j in c[0][1:-1].split(',')]

    simplify_vertices(inp)
    reduce_vertices(inp)

    # ---------------------------------
    if SUBCATCHMENTS in fiona.listlayers(fn):
        gdf = read_file(fn, layer=SUBCATCHMENTS).set_index('Name')

        for sec in [SUBCATCHMENTS, SUBAREAS, INFILTRATION]:
            cols = gdf.columns[gdf.columns.str.startswith(sec)]
            inp[sec] = SECTION_TYPES[sec].create_section(gdf[cols].reset_index().fillna(NaN).values)

        inp[POLYGONS] = SECTION_TYPES[POLYGONS].create_section_from_geoseries(gdf.geometry)

    return inp


def update_length(inp):
    """
    Set the length of all conduits based on the length of the vertices.

    Args:
        inp (SwmmInput): inp data

    .. Important::
        Works inplace.
    """
    for c in inp.CONDUITS.values():
        c.Length = inp.VERTICES[c.Name].geo.length
