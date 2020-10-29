from ..inp_macros import InpMacros
from swmm_api.input_file.inp_sections.labels import *
import numpy as np


def append_na(x, every=3):
    every_index = every - 1
    return np.reshape(np.insert(np.reshape(x, (-1, every_index)), every_index, None, axis=1), (1, -1))[0]


class InpMacrosAlpha(InpMacros):
    ####################################################################################################################
    def print_map(self):  # TODO
        if COORDINATES in self:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            coords = self[COORDINATES]
            ax.scatter(x=coords.x, y=coords.y)
            for name, node in coords[::80].iterrows():
                ax.text(node.x, node.y, name, horizontalalignment='center', verticalalignment='baseline')

            map_dim = self['MAP']['DIMENSIONS']
            x_min, x_max = map_dim['lower-left X'], map_dim['upper-right X']
            delta_x = x_max - x_min
            y_min, y_max = map_dim['lower-left Y'], map_dim['upper-right Y']
            delta_y = y_max - y_min
            ax.set_axis_off()
            fig.set_size_inches(w=118.0 / 2.51, h=(118.0 * delta_y / delta_x) / 2.51)
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)

            for name, line in self['CONDUITS'].iterrows():
                line_coords = coords.loc[[line['FromNode'], line['ToNode']]].copy()
                ax.plot(line_coords['x'], line_coords['y'], 'k-')
                # print()
                # pass

            fig.tight_layout()
            # ax.set_aspect(1.0)
            fig.savefig('map.pdf')
            # fig.show()
            # print()

    def networkx(self, draw=True):  # TODO
        import networkx as nx
        g = nx.Graph()
        for edge_kind in [CONDUITS,
                          WEIRS,
                          PUMPS,
                          ORIFICES,
                          OUTLETS]:
            if edge_kind not in self:
                continue
            edges = self[edge_kind][['FromNode', 'ToNode']]
            g.add_edges_from(edges.apply(tuple, axis=1).tolist())

        from networkx.algorithms.components import node_connected_component
        g.remove_node(6500062)
        sub = nx.subgraph(g, node_connected_component(g, 'R05'))
        print()

        if draw:
            coords = self['COORDINATES']
            pos = coords.apply(tuple, axis=1).to_dict()
            nx.draw(sub, pos)

    def plotly_map(self, fn):  # TODO
        if 'COORDINATES' in self:
            coords = self['COORDINATES']
            from sww.libs.timeseries.plots.plotly_interface import PlotlyAxes, Ax
            from plotly.graph_objs import Scatter
            axes = PlotlyAxes()

            for edge_kind, color in [('CONDUITS', 'black'),
                                     ('WEIRS', 'red'),
                                     ('PUMPS', 'blue'),
                                     ('ORIFICES', 'orange'),
                                     ('OUTLETS', 'cyan')]:
                if edge_kind not in self:
                    continue

                nodes = self[edge_kind][['FromNode', 'ToNode']].stack().values
                x = coords.lookup(nodes, ['x'] * len(nodes))
                y = coords.lookup(nodes, ['y'] * len(nodes))

                x = append_na(x, 3)
                y = append_na(y, 3)

                edge_scatter = Scatter(x=x, y=y, hoverinfo='none',  # hovertext=[],
                                       showlegend=True, line=dict(color=color),
                                       mode='lines', name=edge_kind)

                axes.append(Ax(edge_scatter))

            axes.append(Ax(Scatter(x=coords.x, y=coords.y, hoverinfo='text', hovertext=coords.index,
                                   mode='markers',
                                   name='JUNCTIONS', marker=dict(color='grey'))))

            # https://plot.ly/python/igraph-networkx-comparison/
            fig = axes.get_figure(vertical_spacing=0.02, spaces=[4, 4, 1.5], bg=None)
            # fig.set_title(self.station)

            fig.turn_axes_off()
            fig.set_size_auto()
            fig.set_hover_mode("closest")
            fig.save(fn, auto_open=True)

    def plotly_mapX(self, fn):

        # TODO keine ahnung wie man koordinaten umrechnet

        if 'COORDINATES' in self:
            coords = self['COORDINATES']
            from sww.libs.timeseries.plots.plotly_interface import PlotlyAxes, Ax
            from plotly.graph_objs import Scatter, Scattergeo
            axes = PlotlyAxes()

            # for edge_kind, color in [('CONDUITS', 'black'),
            #                          ('WEIRS', 'red'),
            #                          ('PUMPS', 'blue'),
            #                          ('ORIFICES', 'orange'),
            #                          ('OUTLETS', 'cyan')]:
            #     if edge_kind not in self:
            #         continue
            #
            #     nodes = self[edge_kind][['FromNode', 'ToNode']].stack().values
            #     x = coords.lookup(nodes, ['x'] * len(nodes))
            #     y = coords.lookup(nodes, ['y'] * len(nodes))
            #
            #     x = append_na(x, 3)
            #     y = append_na(y, 3)
            #
            #     edge_scatter = Scatter(x=x, y=y, hoverinfo='none',  # hovertext=[],
            #                            showlegend=True, line=dict(color=color),
            #                            mode='lines', name=edge_kind)
            #
            #     axes.append(Ax(edge_scatter))

            axes.append(
                Ax(Scattergeo(lon=coords.x, lat=coords.y, hoverinfo='lon+lat',  # 'text', hovertext=coords.index,
                              mode='markers',
                              name='JUNCTIONS', marker=dict(color='grey'))))

            # https://plot.ly/python/igraph-networkx-comparison/
            fig = axes.get_figure(bg=None)
            fig.figure.layout.update(dict(geo=dict(
                scope="europe",
                projection=dict(type="transverse mercator"),
                showland=True,
                lonaxis=dict(
                    showgrid=True,
                    gridwidth=0.5,
                    # range=[-140.0, -55.0],
                    dtick=5
                ),
                lataxis=dict(
                    showgrid=True,
                    gridwidth=0.5,
                    # range=[20.0, 60.0],
                    dtick=5
                )
                # rotation=dict(
                #     lon=-34/2
                # )
                # landcolor='rgb(243, 243, 243)',
                # countrycolor='rgb(204, 204, 204)',
            ), ))
            # fig.set_title(self.station)
            # fig.turn_axes_off()
            # fig.set_size_auto()
            # fig.set_hover_mode("closest")
            fig.save(fn, auto_open=True)
