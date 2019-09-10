from os import path, remove
from warnings import warn

from swmm_api import swmm5_run
from swmm_api.output_file.out import SwmmOutHandler
from sww.libs.timeseries.io import parquet
from .inp_reader import read_inp_file
from .inp_writer import write_inp_file, inp2string
from swmm_api.type_converter import offset2delta
from .inp_helpers import MyUserDict
import networkx as nx
from pandas import Series, DataFrame


class InpMacros(MyUserDict):
    """
    'REPORT'
    'TITLE'
    'OPTIONS'
    'EVAPORATION'
    'JUNCTIONS'
    'OUTFALLS'
    'STORAGE'
    'CONDUITS'
    'WEIRS'
    'XSECTIONS'
    'INFLOWS'
    'CURVES'
    'TIMESERIES'
    'RAINGAGES'
    'SUBCATCHMENTS'
    'SUBAREAS'
    'INFILTRATION'
    'POLLUTANTS'
    'LOADINGS'
    'DWF'
    'PATTERNS'
    'ORIFICES'
    """

    def __init__(self):
        MyUserDict.__init__(self, {})
        self.filename = None
        self.basename = None
        self.dirname = None

    def set_name(self, name):
        self.filename = name
        self.basename = '.'.join(path.basename(name).split('.')[:-1])
        self.dirname = path.dirname(name)

    @property
    def report_filename(self):
        return path.join(self.dirname, self.basename + '.rpt')

    @property
    def out_filename(self):
        return path.join(self.dirname, self.basename + '.out')

    @property
    def parquet_filename(self):
        return path.join(self.dirname, self.basename + '.parquet')

    def __repr__(self):
        return str(self)

    def __str__(self):
        return inp2string(self)

    def _read_inp(self, drop_gui_part=True):
        MyUserDict.__init__(self, **read_inp_file(self.filename, drop_gui_part=drop_gui_part))

    @classmethod
    def from_file(cls, filename, drop_gui_part=True):
        inp = cls()
        inp.set_name(filename)
        inp._read_inp(drop_gui_part=drop_gui_part)
        return inp

    # @class_timeit
    def write(self):
        write_inp_file(self, self.filename)

    # ------------------------------------------------------------------------------------------------------------------
    # @class_timeit
    def execute_swmm(self, rpt_dir=None, out_dir=None, init_print=False):
        swmm5_run(self.filename, rpt_dir=rpt_dir, out_dir=out_dir, init_print=init_print)

    def delete_report_file(self):
        remove(self.report_filename)

    def delete_inp_file(self):
        remove(self.filename)

    # @class_timeit
    def run(self, rpt_dir=None, out_dir=None, init_print=False):
        self.execute_swmm(rpt_dir=rpt_dir, out_dir=out_dir, init_print=init_print)
        self.convert_out()

    # ------------------------------------------------------------------------------------------------------------------
    # @class_timeit
    def get_out(self):
        return SwmmOutHandler(self.out_filename)

    # @class_timeit
    def get_out_frame(self):
        out = self.get_out()
        df = out.to_frame()
        # TODO check if file can be deleted
        out.fp.close()
        del out
        return df

    # @class_timeit
    def convert_out(self):
        out = self.get_out()
        out.to_parquet()
        if out.filename:
            try:
                remove(out.filename)
            except PermissionError as e:
                warn(str(e))

    def delete_out_file(self):
        remove(self.out_filename)

    # @class_timeit
    def get_result_frame(self):
        if not path.isfile(self.parquet_filename):
            self.convert_out()
        return parquet.read(self.parquet_filename)

    ####################################################################################################################
    @property
    def report(self):
        if 'REPORT' in self:
            return self['REPORT']
        else:
            return None

    @property
    def options(self):
        if 'OPTIONS' in self:
            return self['OPTIONS']
        else:
            return None

    @property
    def curves(self):
        if 'CURVES' in self:
            return self['CURVES']
        else:
            return None

    @property
    def timeseries(self):
        if 'TIMESERIES' in self:
            return self['TIMESERIES']
        else:
            return None

    @property
    def inflows(self):
        if 'INFLOWS' in self:
            return self['INFLOWS']
        else:
            return None

    ####################################################################################################################
    def reset_section(self, cat, cls):
        if cat in self:
            del self[cat]
        self[cat] = cls

    def check_section(self, cat, cls):
        if cat not in self:
            self[cat] = cls

    def set_start(self, start, incl_report=True):
        self.check_section('OPTIONS', Series())
        self['OPTIONS'].loc['START_DATE'] = start.date()
        self['OPTIONS'].loc['START_TIME'] = start.time()

        if incl_report:
            self.set_start_report(start)

    def set_start_report(self, start):
        self.check_section('OPTIONS', Series())
        self['OPTIONS'].loc['REPORT_START_DATE'] = start.date()
        self['OPTIONS'].loc['REPORT_START_TIME'] = start.time()

    def set_end(self, end):
        self.check_section('OPTIONS', Series())
        self['OPTIONS'].loc['END_DATE'] = end.date()
        self['OPTIONS'].loc['END_TIME'] = end.time()

    def set_threads(self, num):
        self.check_section('OPTIONS', Series())
        self['OPTIONS'].loc['THREADS'] = num

    def ignore_rainfall(self, on=True):
        self.check_section('OPTIONS', Series())
        self['OPTIONS'].loc['IGNORE_RAINFALL'] = on

    def ignore_snowmelt(self, on=True):
        self.check_section('OPTIONS', Series())
        self['OPTIONS'].loc['IGNORE_SNOWMELT'] = on

    def ignore_groundwater(self, on=True):
        self.check_section('OPTIONS', Series())
        self['OPTIONS'].loc['IGNORE_GROUNDWATER'] = on

    def ignore_quality(self, on=True):
        self.check_section('OPTIONS', Series())
        self['OPTIONS'].loc['IGNORE_QUALITY'] = on

    def set_intervals(self, freq):
        self.check_section('OPTIONS', Series())
        new_step = offset2delta(freq)
        self['OPTIONS']['REPORT_STEP'] = new_step
        self['OPTIONS']['WET_STEP'] = new_step
        self['OPTIONS']['DRY_STEP'] = new_step

    def activate_report(self, input=False, continuity=True, flowstats=True, controls=False):
        self.check_section('REPORT', Series())
        self['REPORT'].loc['INPUT'] = input
        self['REPORT'].loc['CONTINUITY'] = continuity
        self['REPORT'].loc['FLOWSTATS'] = flowstats
        self['REPORT'].loc['CONTROLS'] = controls

    def reduce_curves(self):  # TODO no frame
        curves = set(self['XSECTIONS']['Curve'].dropna().unique().tolist())
        # curves |= set(self['OUTFALLS']['Data'].dropna().unique().tolist())

        # self['CURVES']['shape'].update(self['CURVES']['Shape'])

        old_shapes = self['CURVES'].pop('shape')

        new_curves = {}
        for c in curves:
            if c in old_shapes:
                new_curves.update({c: old_shapes[c]})

        self['CURVES'].update({'shape': new_curves})

    def add_obj_to_report(self, new_obj, obj_kind):
        if isinstance(new_obj, str):
            new_obj = [new_obj]
        elif isinstance(new_obj, list):
            pass
        else:
            raise NotImplementedError('Type: {} not implemented!'.format(type(new_obj)))

        old_obj = self.report[obj_kind]
        if isinstance(old_obj, str):
            old_obj = [old_obj]
        elif isinstance(old_obj, (int, float)):
            old_obj = [str(old_obj)]
        elif isinstance(old_obj, list):
            pass
        elif old_obj is None:
            old_obj = []
        else:
            raise NotImplementedError('Type: {} not implemented!'.format(type(old_obj)))

        self.report[obj_kind] = old_obj + new_obj

    def add_nodes_to_report(self, new_nodes):
        self.add_obj_to_report(new_nodes, 'NODES')

    def add_links_to_report(self, new_links):
        self.add_obj_to_report(new_links, 'LINKS')

    def add_timeseries_file(self, fn):
        self.check_section('TIMESERIES', dict())
        if 'Files' not in self['TIMESERIES']:
            self['TIMESERIES']['Files'] = DataFrame(columns=['Type', 'Fname'])

        self['TIMESERIES']['Files'] = self['TIMESERIES']['Files'].append(
            Series({'Fname': '"' + fn + '.dat"'}, name=path.basename(fn)))
        self['TIMESERIES']['Files']['Type'] = 'FILE'

    ####################################################################################################################
    def print_map(self):  # TODO
        if 'COORDINATES' in self:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            coords = self['COORDINATES']
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
        g = nx.Graph()
        for edge_kind in ['CONDUITS',
                          'WEIRS',
                          'PUMPS',
                          'ORIFICES',
                          'OUTLETS']:
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


import numpy as np


def append_na(x, every=3):
    every_index = every - 1
    return np.reshape(np.insert(np.reshape(x, (-1, every_index)), every_index, None, axis=1), (1, -1))[0]
