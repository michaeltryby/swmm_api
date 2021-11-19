import inspect
import time

import fiona
from geopandas import GeoDataFrame, GeoSeries, read_file
from numpy import NaN
from pandas import MultiIndex

from .filter import filter_nodes, filter_links
from .geo import update_vertices
from .reduce_unneeded import reduce_vertices
from .tags import get_node_tags, get_link_tags, get_subcatchment_tags
from .. import section_labels as s
from ..inp import SwmmInput
from ..section_lists import LINK_SECTIONS, NODE_SECTIONS
from ..section_types import SECTION_TYPES
from ..sections import Tag
from ..sections.map_geodata import (add_geo_support, InpSectionGeo, convert_section_to_geosection,
                                    geo_section_converter, CoordinateGeo, VerticesGeo, PolygonGeo, )

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

    inp = SwmmInput.read_file(inp_fn, custom_converter=geo_section_converter)

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
    todo_sections = NODE_SECTIONS + LINK_SECTIONS + [s.SUBCATCHMENTS]
    print(*todo_sections, sep=' | ')

    add_geo_support(inp, crs=crs)

    # ---------------------------------
    t0 = time.perf_counter()
    nodes_tags = get_node_tags(inp)
    for sec in NODE_SECTIONS:
        if sec in inp:
            df = inp[sec].frame.rename(columns=lambda c: f'{sec}{label_sep}{c}')

            if sec == s.STORAGE:
                df[f'{s.STORAGE}{label_sep}Curve'] = df[f'{s.STORAGE}{label_sep}Curve'].astype(str)

            for sub_sec in [s.DWF, s.INFLOWS]:
                if sub_sec in inp:
                    x = inp[sub_sec].frame.unstack(1)
                    x.columns = [f'{label_sep}'.join([sub_sec, c[1], c[0]]) for c in x.columns]
                    df = df.join(x)

            df = df.join(inp[s.COORDINATES].geo_series).join(nodes_tags)

            GeoDataFrame(df).to_file(gpkg_fn, driver=driver, layer=sec)
        print(f'{f"{time.perf_counter() - t0:0.1f}s":^{len(sec)}s}', end=' | ')
        t0 = time.perf_counter()

    # ---------------------------------
    links_tags = get_link_tags(inp)
    update_vertices(inp)
    for sec in LINK_SECTIONS:
        if sec in inp:
            df = inp[sec].frame.rename(columns=lambda c: f'{sec}{label_sep}{c}').join(
                inp[s.XSECTIONS].frame.rename(columns=lambda c: f'{s.XSECTIONS}{label_sep}{c}'))

            if sec == s.OUTLETS:
                df[f'{s.OUTLETS}{label_sep}Curve'] = df[f'{s.OUTLETS}{label_sep}Curve'].astype(str)

            if s.LOSSES in inp:
                df = df.join(inp[s.LOSSES].frame.rename(columns=lambda c: f'{s.LOSSES}{label_sep}{c}'))

            df = df.join(inp[s.VERTICES].geo_series).join(links_tags)

            GeoDataFrame(df).to_file(gpkg_fn, driver=driver, layer=sec)

        print(f'{f"{time.perf_counter() - t0:0.1f}s":^{len(sec)}s}', end=' | ')
        t0 = time.perf_counter()

    # ---------------------------------
    if s.SUBCATCHMENTS in inp:
        df = inp[s.SUBCATCHMENTS].frame.rename(columns=lambda c: f'{s.SUBCATCHMENTS}{label_sep}{c}').join(
            inp[s.SUBAREAS].frame.rename(columns=lambda c: f'{s.SUBAREAS}{label_sep}{c}')).join(
            inp[s.INFILTRATION].frame.rename(columns=lambda c: f'{s.INFILTRATION}{label_sep}{c}')).join(
            inp[s.POLYGONS].geo_series).join(get_subcatchment_tags(inp))

        GeoDataFrame(df).to_file(gpkg_fn, driver=driver, layer=s.SUBCATCHMENTS)
        gs_connector = get_subcatchment_connectors(inp)
        GeoDataFrame(gs_connector).to_file(gpkg_fn, driver=driver, layer=s.SUBCATCHMENTS + '_connector')

    print(f'{f"{time.perf_counter() - t0:0.1f}s":^{len(s.SUBCATCHMENTS)}s}')


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
    res = dict()
    from shapely.geometry import LineString
    for p in inp[s.POLYGONS]:
        c = inp[s.POLYGONS][p].geo.centroid
        o = inp[s.SUBCATCHMENTS][p].Outlet
        if o not in inp[s.COORDINATES]:
            print(inp[s.SUBCATCHMENTS][p])
            continue
        res[p] = LineString([inp[s.COORDINATES][o].point, (c.x, c.y)])
    gs = GeoSeries(res, crs=inp[s.POLYGONS]._crs)
    gs.index.name = 'Subcatchment'
    gs.name = 'geometry'
    return gs


def problems_to_gis(inp, gpkg_fn, nodes=None, links=None, **kwargs):
    """
    filter inp data by nodes and links and write objects to a gis database

    Args:
        inp:
        gpkg_fn:
        nodes:
        links:
        **kwargs:
    """
    if nodes is not None:
        inp = filter_nodes(inp, nodes)

    if links is not None:
        inp = filter_links(inp, links)

    write_geo_package(inp, gpkg_fn, **kwargs)


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
    if (s.VERTICES in inp) and not isinstance(inp[s.VERTICES], InpSectionGeo):
        inp[s.VERTICES] = convert_section_to_geosection(inp[s.VERTICES])
    links_tags = get_link_tags(inp)
    update_vertices(inp)
    res = None
    for sec in LINK_SECTIONS:
        if sec in inp:
            df = inp[sec].frame.rename(columns=lambda c: f'{sec}{label_sep}{c}').join(
                inp[s.XSECTIONS].frame.rename(columns=lambda c: f'{s.XSECTIONS}{label_sep}{c}'))

            if sec == s.OUTLETS:
                df[f'{s.OUTLETS}{label_sep}Curve'] = df[f'{s.OUTLETS}{label_sep}Curve'].astype(str)

            if s.LOSSES in inp:
                df = df.join(inp[s.LOSSES].frame.rename(columns=lambda c: f'{s.LOSSES}{label_sep}{c}'))

            df = df.join(inp[s.VERTICES].geo_series).join(links_tags)
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
    if (s.COORDINATES in inp) and not isinstance(inp[s.COORDINATES], InpSectionGeo):
        inp[s.COORDINATES] = convert_section_to_geosection(inp[s.COORDINATES])
    nodes_tags = get_node_tags(inp)
    res = None
    for sec in NODE_SECTIONS:
        if sec in inp:
            df = inp[sec].frame.rename(columns=lambda c: f'{sec}{label_sep}{c}')

            if sec == s.STORAGE:
                df[f'{s.STORAGE}{label_sep}Curve'] = df[f'{s.STORAGE}{label_sep}Curve'].astype(str)

            for sub_sec in [s.DWF, s.INFLOWS]:
                if sub_sec in inp:
                    x = inp[sub_sec].frame.unstack(1)
                    x.columns = [f'{label_sep}'.join([sub_sec, c[1], c[0]]) for c in x.columns]
                    df = df.join(x)

            df = df.join(inp[s.COORDINATES].geo_series).join(nodes_tags)

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
    inp = SwmmInput()

    SECTION_TYPES.update({s.COORDINATES: CoordinateGeo,
                          s.VERTICES: VerticesGeo,
                          s.POLYGONS: PolygonGeo})

    def _check_sec(sec):
        if sec not in inp:
            inp[sec] = SECTION_TYPES[sec].create_section()

    for sec in NODE_SECTIONS:
        if sec not in fiona.listlayers(fn):
            continue
        gdf = read_file(fn, layer=sec).set_index('Name')

        cols = gdf.columns[gdf.columns.str.startswith(sec)]
        inp[sec] = SECTION_TYPES[sec].create_section(gdf[cols].reset_index().fillna(NaN).values)

        for sub_sec in [s.DWF, s.INFLOWS]:
            _check_sec(sub_sec)
            cols = gdf.columns[gdf.columns.str.startswith(sub_sec)]
            gdf_sub = gdf[cols].copy()
            gdf_sub.columns = MultiIndex.from_tuples([col.split(label_sep) for col in gdf_sub.columns])
            cols_order = gdf_sub.columns.droplevel(1)
            gdf_sub = gdf_sub.stack(1)[cols_order]
            inp[sub_sec].update(SECTION_TYPES[sub_sec].create_section(gdf_sub.reset_index().values))

        _check_sec(s.COORDINATES)
        inp[s.COORDINATES].update(SECTION_TYPES[s.COORDINATES].create_section_from_geoseries(gdf.geometry))

        tags = gdf[['tag']].copy()
        tags['type'] = Tag.TYPES.Node
        _check_sec(s.TAGS)
        inp[s.TAGS].update(SECTION_TYPES[s.TAGS].create_section(tags[['type', 'tag']].reset_index().values))

    for i in inp[s.STORAGE]:
        c = inp[s.STORAGE][i].Curve
        if isinstance(c, list):
            inp[s.STORAGE][i].Curve = [float(j) for j in c[0][1:-1].split(',')]

    # ---------------------------------
    for sec in LINK_SECTIONS:
        if sec not in fiona.listlayers(fn):
            continue
        gdf = read_file(fn, layer=sec).set_index('Name')

        cols = gdf.columns[gdf.columns.str.startswith(sec)]
        inp[sec] = SECTION_TYPES[sec].create_section(gdf[cols].reset_index().fillna(NaN).values)

        for sub_sec in [s.XSECTIONS, s.LOSSES]:
            _check_sec(sub_sec)
            cols = gdf.columns[gdf.columns.str.startswith(sub_sec)].to_list()
            if cols:
                if sub_sec == s.XSECTIONS:
                    cols = [f'{sub_sec}{label_sep}{i}' for i in inspect.getargspec(SECTION_TYPES[sub_sec]).args[2:]]
                gdf_sub = gdf[cols].copy().dropna(how='all')
                if sub_sec == s.LOSSES:
                    gdf_sub[f'{s.LOSSES}{label_sep}FlapGate'] = gdf_sub[f'{s.LOSSES}{label_sep}FlapGate'] == 1
                inp[sub_sec].update(SECTION_TYPES[sub_sec].create_section(gdf_sub.reset_index().values))

        _check_sec(s.VERTICES)
        inp[s.VERTICES].update(SECTION_TYPES[s.VERTICES].create_section_from_geoseries(gdf.geometry))

        tags = gdf[['tag']].copy()
        tags['type'] = Tag.TYPES.Link
        _check_sec(s.TAGS)
        inp[s.TAGS].update(SECTION_TYPES[s.TAGS].create_section(tags[['type', 'tag']].reset_index().values))

    if s.OUTLETS in inp:
        for i in inp[s.OUTLETS]:
            c = inp[s.OUTLETS][i].Curve
            if isinstance(c, list):
                inp[s.OUTLETS][i].Curve = [float(j) for j in c[0][1:-1].split(',')]

    reduce_vertices(inp)

    # ---------------------------------
    if s.SUBCATCHMENTS in fiona.listlayers(fn):
        gdf = read_file(fn, layer=s.SUBCATCHMENTS).set_index('Name')

        for sec in [s.SUBCATCHMENTS, s.SUBAREAS, s.INFILTRATION]:
            cols = gdf.columns[gdf.columns.str.startswith(sec)]
            inp[sec] = SECTION_TYPES[sec].create_section(gdf[cols].reset_index().fillna(NaN).values)

        inp[s.POLYGONS] = SECTION_TYPES[s.POLYGONS].create_section_from_geoseries(gdf.geometry)

    return inp


def update_length(inp):
    add_geo_support(inp, crs="EPSG:32633")
    for c in inp.CONDUITS.values():
        c.Length = inp.VERTICES[c.Name].geo.length
