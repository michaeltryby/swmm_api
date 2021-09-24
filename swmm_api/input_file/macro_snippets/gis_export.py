import time

from geopandas import GeoDataFrame, GeoSeries

from ..macros import update_vertices, filter_nodes, filter_links, get_node_tags, get_link_tags, get_subcatchment_tags
from ..inp import SwmmInput
from .. import section_labels as s
from ..section_lists import LINK_SECTIONS, NODE_SECTIONS
from ..sections.map_geodata import (add_geo_support, InpSectionGeo, convert_section_to_geosection,
                                    geo_section_converter, )

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
    t0 = time.time()
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
        print(f'{f"{time.time() - t0:0.1f}s":^{len(sec)}s}', end=' | ')
        t0 = time.time()

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

        print(f'{f"{time.time() - t0:0.1f}s":^{len(sec)}s}', end=' | ')
        t0 = time.time()

    # ---------------------------------
    if s.SUBCATCHMENTS in inp:
        df = inp[s.SUBCATCHMENTS].frame.rename(columns=lambda c: f'{s.SUBCATCHMENTS}{label_sep}{c}').join(
            inp[s.SUBAREAS].frame.rename(columns=lambda c: f'{s.SUBAREAS}{label_sep}{c}')).join(
            inp[s.INFILTRATION].frame.rename(columns=lambda c: f'{s.INFILTRATION}{label_sep}{c}')).join(
            inp[s.POLYGONS].geo_series).join(get_subcatchment_tags(inp))

        GeoDataFrame(df).to_file(gpkg_fn, driver=driver, layer=s.SUBCATCHMENTS)
        gs_connector = get_subcatchment_connectors(inp)
        GeoDataFrame(gs_connector).to_file(gpkg_fn, driver=driver, layer=s.SUBCATCHMENTS + '_connector')

    print(f'{f"{time.time() - t0:0.1f}s":^{len(s.SUBCATCHMENTS)}s}')


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
