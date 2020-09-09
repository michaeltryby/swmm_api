import networkx as nx
import matplotlib.pyplot as plt

from ..helpers.sections import *
from ..inp_sections_generic import CoordinatesSection
from ..inp_sections import Outfall

def inp_to_graph(inp):
    g = nx.Graph()
    for edge_kind in [CONDUITS,
                      WEIRS,
                      PUMPS,
                      ORIFICES,
                      OUTLETS]:
        if edge_kind in inp:
            for e in inp[edge_kind].values():
                g.add_edge(str(e.FromNode), str(e.ToNode))
    return g


def get_path(g, start, end):
    return list(nx.all_simple_paths(g, start, end))[0]


def plot_network(inp, g, ax=None, **kwargs):
    """

    Args:
        inp:
        g:
        ax:
        **kwargs:

    Returns:
        (plt.Figure, plt.Axes):
    """
    coords = None

    if COORDINATES in inp:
        coords_sec = inp[COORDINATES]
        if isinstance(coords_sec, list):
            coords = dict()
            for name, x, y in inp[COORDINATES]:
                coords[name] = (float(x), float(y))
        elif isinstance(coords_sec, CoordinatesSection):
            coords = dict()
            for name, c in inp[COORDINATES].items():
                coords[name] = (float(c['x']), float(c['y']))

    if ax is None:
        fig, ax = plt.subplots()
    nx.draw(g, coords, ax=ax, **kwargs)
    return ax.get_figure(), ax  # type: plt.Figure, plt.Axes


class COLS:
    INVERT_ELEV = 'SOK'
    CROWN_ELEV = 'BUK'
    GROUND_ELEV = 'GOK'  # rim elevation
    STATION = 'x'
    WATER = 'water'


def get_plot_longitudinal_data(inp, start_node, end_node, out=None):
    g = inp_to_graph(inp)
    sub_list = get_path(g, start=start_node, end=end_node)

    following_conduit = {conduit.FromNode: conduit for _, conduit in inp[CONDUITS].items()}
    prior_conduit = {conduit.ToNode: conduit for _, conduit in inp[CONDUITS].items()}

    keys = [COLS.STATION,
            COLS.INVERT_ELEV,
            COLS.CROWN_ELEV,
            COLS.GROUND_ELEV,
            COLS.WATER]

    res = {k: list() for k in keys}

    def _update_res(*args):
        for k, v in zip(keys, args):
            res[k].append(v)

    nodes_dict = dict()
    for s in [JUNCTIONS, OUTFALLS, STORAGE]:
        nodes_dict.update(inp[s])

    x = 0
    profile_height = 0
    for node in sub_list:
        n = nodes_dict[node]
        sok = n.Elevation

        gok = sok
        if isinstance(n, Outfall):
            gok += profile_height
        else:
            gok += n.MaxDepth

        if out is not None:
            water = sok + out.get_part('node', node, 'Depth_above_invert').mean()
        else:
            water = None

        # ------------------
        if node in prior_conduit:
            profile_height = inp[XSECTIONS][prior_conduit[node].Name].Geom1
            buk = profile_height + sok
            _update_res(x, sok, buk, gok, water)

        # ------------------
        if node in following_conduit:
            profile_height = inp[XSECTIONS][following_conduit[node].Name].Geom1
            buk = profile_height + sok
            _update_res(x, sok, buk, gok, water)

            x += following_conduit[node].Length

    # ------------------------------------
    return res


def plot_longitudinal(inp, start_node, end_node, out=None, ax=None):
    res = get_plot_longitudinal_data(inp, start_node, end_node, out)

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
    else:
        # Conduit Fill
        ax.fill_between(res[COLS.STATION], res[COLS.CROWN_ELEV], res[COLS.INVERT_ELEV], color='#B0B0B0', alpha=0.5)

    ax.set_xlim(0, res[COLS.STATION][-1])
    ax.set_ylim(bottom=bottom)
    return fig, ax
