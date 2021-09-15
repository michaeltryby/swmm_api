import geopandas as gpd
from pandas import MultiIndex
import numpy as np
from ..inp import SwmmInput
from .. import section_labels as s
from ..macros import reduce_vertices
from ..section_types import SECTION_TYPES
import fiona
import inspect

from ..sections import Tag
from ..sections.map_geodata import CoordinateGeo, VerticesGeo, PolygonGeo


# inspect.getargspec(SECTION_TYPES[sec]).args[1:]


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

    for sec in [s.JUNCTIONS, s.STORAGE, s.OUTFALLS]:
        if sec not in fiona.listlayers(fn):
            continue
        gdf = gpd.read_file(fn, layer=sec).set_index('Name')

        cols = gdf.columns[gdf.columns.str.startswith(sec)]
        inp[sec] = SECTION_TYPES[sec].create_section(gdf[cols].reset_index().fillna(np.NaN).values)

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
    for sec in [s.CONDUITS, s.WEIRS, s.OUTLETS, s.ORIFICES, s.PUMPS]:
        if sec not in fiona.listlayers(fn):
            continue
        gdf = gpd.read_file(fn, layer=sec).set_index('Name')

        cols = gdf.columns[gdf.columns.str.startswith(sec)]
        inp[sec] = SECTION_TYPES[sec].create_section(gdf[cols].reset_index().fillna(np.NaN).values)

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
        gdf = gpd.read_file(fn, layer=s.SUBCATCHMENTS).set_index('Name')

        for sec in [s.SUBCATCHMENTS, s.SUBAREAS, s.INFILTRATION]:
            cols = gdf.columns[gdf.columns.str.startswith(sec)]
            inp[sec] = SECTION_TYPES[sec].create_section(gdf[cols].reset_index().fillna(np.NaN).values)

        inp[s.POLYGONS] = SECTION_TYPES[s.POLYGONS].create_section_from_geoseries(gdf.geometry)

    return inp
