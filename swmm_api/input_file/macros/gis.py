import inspect
import time

from numpy import NaN
from pandas import MultiIndex
from tqdm.auto import tqdm

from .filter import filter_nodes, filter_links
from .geo import complete_vertices, simplify_vertices, reduce_vertices
from .tags import get_node_tags, get_link_tags, get_subcatchment_tags
from ..section_abr import SEC

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
    from geopandas import GeoDataFrame

    todo_sections = NODE_SECTIONS + LINK_SECTIONS + [SEC.SUBCATCHMENTS]
    print(*todo_sections, sep=' | ')

    add_geo_support(inp, crs=crs)

    # ---------------------------------
    t0 = time.perf_counter()
    nodes_tags = get_node_tags(inp)
    for sec in NODE_SECTIONS:
        if sec in inp:
            df = inp[sec].frame.rename(columns=lambda c: f'{sec}{label_sep}{c}')

            if sec == SEC.STORAGE:
                df[f'{SEC.STORAGE}{label_sep}Curve'] = df[f'{SEC.STORAGE}{label_sep}Curve'].astype(str)

            for sub_sec in [SEC.DWF, SEC.INFLOWS]:
                if sub_sec in inp:
                    x = inp[sub_sec].frame.unstack(1)
                    x.columns = [f'{label_sep}'.join([sub_sec, c[1], c[0]]) for c in x.columns]
                    df = df.join(x)

            df = df.join(inp[SEC.COORDINATES].geo_series).join(nodes_tags)

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
                inp[SEC.XSECTIONS].frame.rename(columns=lambda c: f'{SEC.XSECTIONS}{label_sep}{c}'))

            if sec == SEC.OUTLETS:
                df[f'{SEC.OUTLETS}{label_sep}Curve'] = df[f'{SEC.OUTLETS}{label_sep}Curve'].astype(str)

            if SEC.LOSSES in inp:
                df = df.join(inp[SEC.LOSSES].frame.rename(columns=lambda c: f'{SEC.LOSSES}{label_sep}{c}'))

            df = df.join(inp[SEC.VERTICES].geo_series).join(links_tags)

            GeoDataFrame(df).to_file(gpkg_fn, driver=driver, layer=sec)

            print(f'{f"{time.perf_counter() - t0:0.1f}s":^{len(sec)}s}', end=' | ')
        else:
            print(f'{f"-":^{len(sec)}s}', end=' | ')
        t0 = time.perf_counter()

    # ---------------------------------
    if SEC.SUBCATCHMENTS in inp:
        df = inp[SEC.SUBCATCHMENTS].frame.rename(columns=lambda c: f'{SEC.SUBCATCHMENTS}{label_sep}{c}').join(
            inp[SEC.SUBAREAS].frame.rename(columns=lambda c: f'{SEC.SUBAREAS}{label_sep}{c}')).join(
            inp[SEC.INFILTRATION].frame.rename(columns=lambda c: f'{SEC.INFILTRATION}{label_sep}{c}')).join(
            inp[SEC.POLYGONS].geo_series).join(get_subcatchment_tags(inp))

        GeoDataFrame(df).to_file(gpkg_fn, driver=driver, layer=SEC.SUBCATCHMENTS)
        gs_connector = get_subcatchment_connectors(inp)
        GeoDataFrame(gs_connector).to_file(gpkg_fn, driver=driver, layer=SEC.SUBCATCHMENTS + '_connector')

        print(f'{f"{time.perf_counter() - t0:0.1f}s":^{len(SEC.SUBCATCHMENTS)}s}')
    else:
        print(f'{f"-":^{len(SEC.SUBCATCHMENTS)}s}', end=' | ')


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

    res = dict()
    for p in tqdm(inp[SEC.POLYGONS], total=len(inp[SEC.POLYGONS].keys()), desc='get_subcatchment_connectors'):
        c = inp[SEC.POLYGONS][p].geo.centroid
        o = inp[SEC.SUBCATCHMENTS][p].Outlet
        if o not in inp[SEC.COORDINATES]:
            print(inp[SEC.SUBCATCHMENTS][p])
            continue
        res[p] = LineString([inp[SEC.COORDINATES][o].point, (c.x, c.y)])

    gs = GeoSeries(res, crs=inp[SEC.POLYGONS]._crs)
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
    from geopandas import GeoDataFrame

    if (SEC.VERTICES in inp) and not isinstance(inp[SEC.VERTICES], InpSectionGeo):
        inp[SEC.VERTICES] = convert_section_to_geosection(inp[SEC.VERTICES])
    links_tags = get_link_tags(inp)
    complete_vertices(inp)
    res = None
    for sec in LINK_SECTIONS:
        if sec in inp:
            df = inp[sec].frame.rename(columns=lambda c: f'{sec}{label_sep}{c}').join(
                inp[SEC.XSECTIONS].frame.rename(columns=lambda c: f'{SEC.XSECTIONS}{label_sep}{c}'))

            if sec == SEC.OUTLETS:
                df[f'{SEC.OUTLETS}{label_sep}Curve'] = df[f'{SEC.OUTLETS}{label_sep}Curve'].astype(str)

            if SEC.LOSSES in inp:
                df = df.join(inp[SEC.LOSSES].frame.rename(columns=lambda c: f'{SEC.LOSSES}{label_sep}{c}'))

            df = df.join(inp[SEC.VERTICES].geo_series).join(links_tags)
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

    if (SEC.COORDINATES in inp) and not isinstance(inp[SEC.COORDINATES], InpSectionGeo):
        inp[SEC.COORDINATES] = convert_section_to_geosection(inp[SEC.COORDINATES])
    nodes_tags = get_node_tags(inp)
    res = None
    for sec in NODE_SECTIONS:
        if sec in inp:
            df = inp[sec].frame.rename(columns=lambda c: f'{sec}{label_sep}{c}')

            if sec == SEC.STORAGE:
                df[f'{SEC.STORAGE}{label_sep}Curve'] = df[f'{SEC.STORAGE}{label_sep}Curve'].astype(str)

            for sub_sec in [SEC.DWF, SEC.INFLOWS]:
                if sub_sec in inp:
                    x = inp[sub_sec].frame.unstack(1)
                    x.columns = [f'{label_sep}'.join([sub_sec, c[1], c[0]]) for c in x.columns]
                    df = df.join(x)

            df = df.join(inp[SEC.COORDINATES].geo_series).join(nodes_tags)

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

    SECTION_TYPES.update({SEC.COORDINATES: CoordinateGeo,
                          SEC.VERTICES   : VerticesGeo,
                          SEC.POLYGONS   : PolygonGeo})

    def _check_sec(sec):
        if sec not in inp:
            inp[sec] = SECTION_TYPES[sec].create_section()

    for sec in NODE_SECTIONS:
        if sec not in fiona.listlayers(fn):
            continue
        gdf = read_file(fn, layer=sec).set_index('Name')

        cols = gdf.columns[gdf.columns.str.startswith(sec)]
        inp[sec] = SECTION_TYPES[sec].create_section(gdf[cols].reset_index().fillna(NaN).values)

        for sub_sec in [SEC.DWF, SEC.INFLOWS]:
            _check_sec(sub_sec)
            cols = gdf.columns[gdf.columns.str.startswith(sub_sec)]
            gdf_sub = gdf[cols].copy()
            gdf_sub.columns = MultiIndex.from_tuples([col.split(label_sep) for col in gdf_sub.columns])
            cols_order = gdf_sub.columns.droplevel(1)
            gdf_sub = gdf_sub.stack(1)[cols_order]
            inp[sub_sec].update(SECTION_TYPES[sub_sec].create_section(gdf_sub.reset_index().values))

        _check_sec(SEC.COORDINATES)
        inp[SEC.COORDINATES].update(SECTION_TYPES[SEC.COORDINATES].create_section_from_geoseries(gdf.geometry))

        tags = gdf[['tag']].copy()
        tags['type'] = Tag.TYPES.Node
        _check_sec(SEC.TAGS)
        inp[SEC.TAGS].update(SECTION_TYPES[SEC.TAGS].create_section(tags[['type', 'tag']].reset_index().values))

    for i in inp[SEC.STORAGE]:
        c = inp[SEC.STORAGE][i].Curve
        if isinstance(c, list):
            inp[SEC.STORAGE][i].Curve = [float(j) for j in c[0][1:-1].split(',')]

    # ---------------------------------
    for sec in LINK_SECTIONS:
        if sec not in fiona.listlayers(fn):
            continue
        gdf = read_file(fn, layer=sec).set_index('Name')

        cols = gdf.columns[gdf.columns.str.startswith(sec)]
        inp[sec] = SECTION_TYPES[sec].create_section(gdf[cols].reset_index().fillna(NaN).values)

        for sub_sec in [SEC.XSECTIONS, SEC.LOSSES]:
            _check_sec(sub_sec)
            cols = gdf.columns[gdf.columns.str.startswith(sub_sec)].to_list()
            if cols:
                if sub_sec == SEC.XSECTIONS:
                    cols = [f'{sub_sec}{label_sep}{i}' for i in inspect.getargspec(SECTION_TYPES[sub_sec]).args[2:]]
                gdf_sub = gdf[cols].copy().dropna(how='all')
                if sub_sec == SEC.LOSSES:
                    gdf_sub[f'{SEC.LOSSES}{label_sep}FlapGate'] = gdf_sub[f'{SEC.LOSSES}{label_sep}FlapGate'] == 1
                inp[sub_sec].update(SECTION_TYPES[sub_sec].create_section(gdf_sub.reset_index().values))

        _check_sec(SEC.VERTICES)
        inp[SEC.VERTICES].update(SECTION_TYPES[SEC.VERTICES].create_section_from_geoseries(gdf.geometry))

        tags = gdf[['tag']].copy()
        tags['type'] = Tag.TYPES.Link
        _check_sec(SEC.TAGS)
        inp[SEC.TAGS].update(SECTION_TYPES[SEC.TAGS].create_section(tags[['type', 'tag']].reset_index().values))

    if SEC.OUTLETS in inp:
        for i in inp[SEC.OUTLETS]:
            c = inp[SEC.OUTLETS][i].Curve
            if isinstance(c, list):
                inp[SEC.OUTLETS][i].Curve = [float(j) for j in c[0][1:-1].split(',')]

    simplify_vertices(inp)
    reduce_vertices(inp)

    # ---------------------------------
    if SEC.SUBCATCHMENTS in fiona.listlayers(fn):
        gdf = read_file(fn, layer=SEC.SUBCATCHMENTS).set_index('Name')

        for sec in [SEC.SUBCATCHMENTS, SEC.SUBAREAS, SEC.INFILTRATION]:
            cols = gdf.columns[gdf.columns.str.startswith(sec)]
            inp[sec] = SECTION_TYPES[sec].create_section(gdf[cols].reset_index().fillna(NaN).values)

        inp[SEC.POLYGONS] = SECTION_TYPES[SEC.POLYGONS].create_section_from_geoseries(gdf.geometry)

    return inp


def update_length(inp):
    inp[SEC.VERTICES] = convert_section_to_geosection(inp[SEC.VERTICES], crs="EPSG:32633")
    for c in inp.CONDUITS.values():
        c.Length = inp.VERTICES[c.Name].geo.length
