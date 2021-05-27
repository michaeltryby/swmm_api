import matplotlib.pyplot as plt
from matplotlib import patches

from ..macros import update_vertices, links_connected, links_dict, nodes_dict, get_path_subgraph
from ..sections import Outfall, Polygon, SubCatchment
from ..section_labels import *

def set_inp_dimensions(inp, ax):
    map_dim = inp[MAP]['DIMENSIONS']
    x_min, x_max = map_dim['lower-left X'], map_dim['upper-right X']
    delta_x = x_max - x_min
    y_min, y_max = map_dim['lower-left Y'], map_dim['upper-right Y']
    delta_y = y_max - y_min
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)


def plot_map(inp):  # TODO
    """

    Args:
        inp ():

    Returns:
        matplotlib.Figure, matplotlib.Axes:
    """
    fig, ax = plt.subplots()

    # for name, node in coords[::80].iterrows():
    #     ax.text(node.x, node.y, name, horizontalalignment='center', verticalalignment='baseline')

    ax.set_axis_off()
    ax.set_aspect(1.0)

    # ---------------------
    update_vertices(inp)

    for link, vertices in inp[VERTICES].items():
        x, y = zip(*vertices.vertices)
        ax.plot(x, y, 'y-')

    # ---------------------

    points = dict(inp[COORDINATES])
    from shapely import geometry as shp
    points.update({poly.Subcatch: shp.Polygon(poly.polygon).centroid for poly in inp[POLYGONS].values()})

    if POLYGONS in inp:
        for poly in inp[POLYGONS].values():  # type: Polygon

            # ----------------
            # sub-catchment polygon
            ax.add_patch(patches.Polygon(poly.polygon, closed=True, fill=False, hatch='/'))

            # ----------------
            # center point of sub-catchment
            center = points[poly.Subcatch]

            ax.scatter(x=center.x, y=center.y, marker='s', c='k', zorder=999)

            subcatch = inp[SUBCATCHMENTS][poly.Subcatch]  # type: SubCatchment
            outlet_point = points[subcatch.Outlet]
            ax.plot([center.x, outlet_point.x], [center.y, outlet_point.y], 'r--')

    # ---------------------
    coords = inp[COORDINATES].frame
    node_style = {
        JUNCTIONS: {'marker': '.', 'color': 'b'},
        STORAGE: {'marker': 's', 'color': 'g'},
        OUTFALLS: {'marker': '^', 'color': 'r'},

    }
    ax.scatter(x=coords.x, y=coords.y,
               marker=node_style[JUNCTIONS]['marker'], c=node_style[JUNCTIONS]['color'],
               edgecolors='k', zorder=999)

    for section in [STORAGE, OUTFALLS]:
        if section in inp:
            is_in_sec = coords.index.isin(inp[section].keys())
            ax.scatter(x=coords[is_in_sec].x, y=coords[is_in_sec].y,
                       marker=node_style[section]['marker'], c=node_style[section]['color'],
                       edgecolors='k', zorder=9999)

    # ---------------------
    fig.tight_layout()
    return fig, ax


class COLS:
    INVERT_ELEV = 'SOK'
    CROWN_ELEV = 'BUK'
    GROUND_ELEV = 'GOK'  # rim elevation
    STATION = 'x'
    WATER = 'water'
    # NODE_STATION = 'node'


def get_longitudinal_data(inp, start_node, end_node, out=None, zero_node=None):
    sub_list, sub_graph = get_path_subgraph(inp, start=start_node, end=end_node)

    if zero_node is None:
        zero_node = start_node

    keys = [COLS.STATION, COLS.INVERT_ELEV, COLS.CROWN_ELEV, COLS.GROUND_ELEV, COLS.WATER]

    res = {k: list() for k in keys}

    def _update_res(*args):
        for k, v in zip(keys, args):
            res[k].append(v)

    # ---------------
    nodes = nodes_dict(inp)
    # ---------------
    profile_height = 0
    # ---------------
    nodes_depth = None
    if out is not None:
        nodes_depth = out.get_part('node', sub_list, 'Depth_above_invert').mean().to_dict()
    # ---------------
    stations_ = list(iter_over_inp_(inp, sub_list, sub_graph))
    stations = dict(stations_)
    for node, x in stations_:
        n = nodes[node]
        sok = n.Elevation
        # ---------------
        gok = sok
        if isinstance(n, Outfall):
            gok += profile_height
        else:
            gok += n.MaxDepth
        # ---------------
        if out is not None:
            water = sok + nodes_depth[node]
        else:
            water = None
        # ------------------
        prior_conduit, following_conduit = links_connected(inp, node, sub_graph)

        if prior_conduit:
            prior_conduit = prior_conduit[0]
            profile_height = inp[XSECTIONS][prior_conduit.Name].Geom1
            sok_ = sok + prior_conduit.OutOffset
            buk = profile_height + sok_
            _update_res(x - stations[zero_node], sok_, buk, gok, water)

        if following_conduit:
            following_conduit = following_conduit[0]
            profile_height = inp[XSECTIONS][following_conduit.Name].Geom1
            sok_ = sok + following_conduit.InOffset
            buk = profile_height + sok_
            _update_res(x - stations[zero_node], sok_, buk, gok, water)

    return res


def get_water_level(inp, start_node, end_node, out, zero_node=None, absolute=True):
    nodes_depth = out.get_part('node', None, 'Depth_above_invert').mean().to_dict()
    nodes = nodes_dict(inp)
    x_list = list()
    water_level_list = list()
    stations_ = list(iter_over_inp(inp, start_node, end_node))
    stations = dict(stations_)
    sok = 0
    for node, x in stations_:
        x_list.append(x - stations.get(zero_node, 0))
        if absolute:
            sok = nodes[node].Elevation
        water_level_list.append(sok + nodes_depth[node])

    return {COLS.WATER: water_level_list, COLS.STATION: x_list}


def iter_over_inp_(inp, sub_list, sub_graph):
    links = links_dict(inp)

    x = 0
    for node in sub_list:
        yield node, x
        # ------------------
        out_edges = list(sub_graph.out_edges(node))
        if out_edges:
            following_conduit = links[sub_graph.get_edge_data(*out_edges[0])['label']]
            x += following_conduit.Length


def iter_over_inp(inp, start_node, end_node):
    sub_list, sub_graph = get_path_subgraph(inp, start=start_node, end=end_node)
    return iter_over_inp_(inp, sub_list, sub_graph)


def get_node_station(inp, start_node, end_node, zero_node=None):
    stations = dict(iter_over_inp(inp, start_node, end_node))
    if zero_node:
        return set_zero_node(stations, zero_node)
    return stations


def set_zero_node(stations, zero_node):
    return {node: stations[node] - stations[zero_node] for node in stations}


def plot_longitudinal(inp, start_node, end_node, out=None, ax=None, zero_node=None):
    res = get_longitudinal_data(inp, start_node, end_node, out, zero_node=zero_node)

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()

    ax.plot(res[COLS.STATION], res[COLS.INVERT_ELEV], c='k')
    ax.plot(res[COLS.STATION], res[COLS.GROUND_ELEV], c='brown', lw=0.5)
    ax.plot(res[COLS.STATION], res[COLS.CROWN_ELEV], c='k')
    bottom = ax.get_ylim()[0]

    # Ground Fill
    ax.fill_between(res[COLS.STATION], res[COLS.GROUND_ELEV], res[COLS.CROWN_ELEV], color='#C49B98', alpha=0.5)
    ax.fill_between(res[COLS.STATION], res[COLS.INVERT_ELEV], bottom, color='#C49B98', alpha=0.5)

    if out is not None:
        # Water line
        ax.plot(res[COLS.STATION], res[COLS.WATER], c='b', lw=0.7)
        # Water fill
        ax.fill_between(res[COLS.STATION], res[COLS.WATER], res[COLS.INVERT_ELEV], color='#00D7FF', alpha=0.7)
        # Conduit Fill
        ax.fill_between(res[COLS.STATION], res[COLS.CROWN_ELEV], res[COLS.WATER], color='#B0B0B0', alpha=0.5)
        ax.set_ylim(top=max([max(res[COLS.WATER]), ax.get_ylim()[1]]))
    else:
        # Conduit Fill
        ax.fill_between(res[COLS.STATION], res[COLS.CROWN_ELEV], res[COLS.INVERT_ELEV], color='#B0B0B0', alpha=0.5)

    ax.set_xlim(res[COLS.STATION][0], res[COLS.STATION][-1])
    ax.set_ylim(bottom=bottom)
    return fig, ax
