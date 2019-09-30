__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

import pandas as pd
from io import StringIO
from .helpers import _get_title_of_part, _remove_lines, _part_to_frame, _continuity_part_to_dict

"""
not ready to use
experimental

reading generated report (*.rpt) files
"""


class Report:
    def __init__(self, filename):
        self.raw_parts = dict()
        self.converted_parts = dict()
        self._report_to_dict(filename)

        # ________________
        # TODO
        self._version_title = None
        self._note = None
        self._analysis_options = None
        self._runoff_quantity_continuity = None
        self._flow_routing_continuity = None
        self._time_step_critical_elements = None
        self._highest_flow_instability_indexes = None

        self._routing_time_step_summary = None

        # ________________
        self._subcatchment_runoff_summary = None
        self._node_depth_summary = None
        self._node_inflow_summary = None
        self._node_surcharge_summary = None
        self._node_flooding_summary = None
        self._storage_volume_summary = None
        self._outfall_loading_summary = None
        self._link_flow_summary = None
        self._flow_classification_summary = None
        self._conduit_surcharge_summary = None

    def _report_to_dict(self, fn):
        """
        convert the report file into a dictionary depending of the different parts

        Args:
            fn (str): path to the report file

        Returns:
            dict: dictionary of parts of the report file
        """
        with open(fn, 'r') as file:
            lines = file.readlines()

        self.raw_parts['Simulation Infos'] = ''.join(lines[-3:])
        lines = lines[:-3]
        parts0 = ''.join(lines).split('\n  \n  ****')

        for i, part in enumerate(parts0):
            if part.startswith('*'):
                part = '  ****' + part

            self.raw_parts[_get_title_of_part(part, str(i))] = _remove_lines(part, title=False, empty=True, sep=False)

    def converted(self, key):
        if key not in self.converted_parts:
            self.converted_parts[key] = _remove_lines(self.raw_parts[key], title=True, empty=False)

        return self.converted_parts[key]

    @property
    def analysis_options(self):
        if self._analysis_options is None:
            p = self.converted('Analysis Options')

            res = dict()
            last_key = None
            last_initial_spaces = 0

            for line in p.split('\n'):
                initial_spaces = len(line) - len(line.lstrip())

                if '..' in line:
                    key = line[:line.find('..')].strip()
                    value = line[line.rfind('..') + 2:].strip()

                    if last_initial_spaces > initial_spaces:
                        last_key = None

                    if last_key is not None:
                        res[last_key].update({key: value})
                    else:
                        res[key] = value

                    last_initial_spaces = initial_spaces

                else:
                    last_key = line.replace(':', '').strip()
                    res[last_key] = dict()

            self._analysis_options = res
        return self._analysis_options

    @property
    def flow_routing_continuity(self):
        if self._flow_routing_continuity is None:
            raw = self.raw_parts['Flow Routing Continuity']
            self._flow_routing_continuity = _continuity_part_to_dict(raw)
        return self._flow_routing_continuity

    @property
    def runoff_quantity_continuity(self):
        if self._runoff_quantity_continuity is None:
            raw = self.raw_parts['Runoff Quantity Continuity']
            self._runoff_quantity_continuity = _continuity_part_to_dict(raw)
        return self._runoff_quantity_continuity

    @property
    def subcatchment_runoff_summary(self):
        if self._subcatchment_runoff_summary is None:
            p = self.converted('Subcatchment Runoff Summary')
            self._subcatchment_runoff_summary = _part_to_frame(p)
        return self._subcatchment_runoff_summary

    @property
    def node_depth_summary(self):
        if self._node_depth_summary is None:
            p = self.converted('Node Depth Summary')
            self._node_depth_summary = _part_to_frame(p)
        return self._node_depth_summary

    @property
    def node_inflow_summary(self):
        if self._node_inflow_summary is None:
            p = self.converted('Node Inflow Summary')
            self._node_inflow_summary = _part_to_frame(p)
        return self._node_inflow_summary

    @property
    def node_surcharge_summary(self):
        if self._node_surcharge_summary is None:
            p = self.converted('Node Surcharge Summary')
            self._node_surcharge_summary = _part_to_frame(p)
        return self._node_surcharge_summary

    @property
    def node_flooding_summary(self):
        # parts = report_to_dict(fn)
        if self._node_flooding_summary is None:
            # --------------------------------------------
            p = self.converted('Node Flooding Summary')

            # --------------------------------------------
            if 'No nodes were flooded.' in p:
                self._node_flooding_summary = pd.DataFrame()

            # --------------------------------------------
            else:
                self._node_flooding_summary = _part_to_frame(p)
        return self._node_flooding_summary

    @property
    def storage_volume_summary(self):
        if self._storage_volume_summary is None:
            p = self.converted('Storage Volume Summary')

            # for reading the table and accepting names shorten than 8 characters
            p = p.replace('Storage Unit', 'Storage_Unit')

            self._storage_volume_summary = _part_to_frame(p)
        return self._storage_volume_summary

    @property
    def outfall_loading_summary(self):
        if self._outfall_loading_summary is None:
            p = self.converted('Outfall Loading Summary')
            self._outfall_loading_summary = _part_to_frame(p)
        return self._outfall_loading_summary

    @property
    def link_flow_summary(self):
        if self._link_flow_summary is None:
            p = self.converted('Link Flow Summary')
            self._link_flow_summary = _part_to_frame(p)
        return self._link_flow_summary

    @property
    def flow_classification_summary(self):
        if self._flow_classification_summary is None:
            p = self.converted('Flow Classification Summary')
            self._flow_classification_summary = _part_to_frame(p)
        return self._flow_classification_summary

    @property
    def conduit_surcharge_summary(self):
        if self._conduit_surcharge_summary is None:
            p = self.converted('Conduit Surcharge Summary')
            self._conduit_surcharge_summary = _part_to_frame(p)
        return self._conduit_surcharge_summary


def get_item_in_line(line, item):
    return float([v.strip() for v in line.split()][item])
