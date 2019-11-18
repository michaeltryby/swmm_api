import networkx as nx
import matplotlib.pyplot as plt
from ..helpers.sections import *


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
    coords = dict()
    for name, x, y in inp[COORDINATES]:
        coords[name] = (float(x), float(y))

    if ax is None:
        fig, ax = plt.subplots()
    nx.draw(g, coords, ax=ax, **kwargs)
    return ax.get_figure(), ax
