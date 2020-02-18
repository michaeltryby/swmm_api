import networkx as nx
import matplotlib.pyplot as plt
from ..helpers.sections import *
from ..inp_sections_generic import CoordinatesSection


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
