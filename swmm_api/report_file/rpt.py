__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

from pandas import to_datetime
from pandas._libs.tslibs.timedeltas import Timedelta

from .helpers import _get_title_of_part, _remove_lines, _part_to_frame, _continuity_part_to_dict, UNIT

"""
not ready to use
experimental

reading generated report (*.rpt) files
"""


class SwmmReport:
    def __init__(self, filename):
        """
        create Report instance to read an .rpt-file


        Args:
            filename (str): path to .rpt file
        """
        self.raw_parts = dict()
        self.converted_parts = dict()
        self._filename = filename
        self._report_to_dict()

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

    def __repr__(self):
        return f'SwmmReport(file="{self._filename}")'

    @property
    def flow_unit(self):
        return self.analysis_options['Flow Units']

    @property
    def UNIT(self):
        return UNIT(self.flow_unit)

    def _report_to_dict(self):
        """
        convert the report file into a dictionary depending of the different parts

        Args:
            fn (str): path to the report file

        Returns:
            dict: dictionary of parts of the report file
        """
        with open(self._filename, 'r') as file:
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
            if key not in self.raw_parts:
                return ''
            self.converted_parts[key] = _remove_lines(self.raw_parts[key], title=True, empty=False)

        return self.converted_parts[key]

    @property
    def analysis_options(self):
        """
        get the Analysis Options

        Returns:
            dict: Analysis Options
        """
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
        """
        get the Flow Routing Continuity

        Returns:
            dict: Flow Routing Continuity
        """
        if self._flow_routing_continuity is None:
            raw = self.raw_parts.get('Flow Routing Continuity', None)
            self._flow_routing_continuity = _continuity_part_to_dict(raw)
        return self._flow_routing_continuity

    @property
    def runoff_quantity_continuity(self):
        """
        get the Runoff Quantity Continuity

        Returns:
            dict: Runoff Quantity Continuity
        """
        if self._runoff_quantity_continuity is None:
            raw = self.raw_parts.get('Runoff Quantity Continuity', None)
            self._runoff_quantity_continuity = _continuity_part_to_dict(raw)
        return self._runoff_quantity_continuity

    @property
    def subcatchment_runoff_summary(self):
        """
        get the Subcatchment Runoff Summary

        Returns:
            pandas.DataFrame: Subcatchment Runoff Summary
        """
        if self._subcatchment_runoff_summary is None:
            p = self.converted('Subcatchment Runoff Summary')
            self._subcatchment_runoff_summary = _part_to_frame(p)
        return self._subcatchment_runoff_summary

    @property
    def node_depth_summary(self):
        """
        get the Node Depth Summary

        Returns:
            pandas.DataFrame: Node Depth Summary
        """
        if self._node_depth_summary is None:
            p = self.converted('Node Depth Summary')
            self._node_depth_summary = _part_to_frame(p)
        return self._node_depth_summary

    @property
    def node_inflow_summary(self):
        """
        get the Node Inflow Summary

        Returns:
            pandas.DataFrame: Node Inflow Summary
        """
        if self._node_inflow_summary is None:
            p = self.converted('Node Inflow Summary')
            self._node_inflow_summary = _part_to_frame(p)
        return self._node_inflow_summary

    @property
    def node_surcharge_summary(self):
        """
        get the Node Surcharge Summary

        Returns:
            pandas.DataFrame: Node Surcharge Summary
        """
        if self._node_surcharge_summary is None:
            p = self.converted('Node Surcharge Summary')
            # if 'No nodes were surcharged.' in p:
            #     self._node_surcharge_summary = pd.DataFrame()
            # else:
            self._node_surcharge_summary = _part_to_frame(p)
        return self._node_surcharge_summary

    @property
    def node_flooding_summary(self):
        """
        get the Node Flooding Summary

        Returns:
            pandas.DataFrame: Node Flooding Summary
        """
        if self._node_flooding_summary is None:
            p = self.converted('Node Flooding Summary')
            # if 'No nodes were flooded.' in p:
            #     self._node_flooding_summary = pd.DataFrame()
            # else:
            self._node_flooding_summary = _part_to_frame(p)
        return self._node_flooding_summary

    @property
    def storage_volume_summary(self):
        """
        get the Storage Volume Summary

        Returns:
            pandas.DataFrame: Storage Volume Summary
        """
        if self._storage_volume_summary is None:
            p = self.converted('Storage Volume Summary')

            # for reading the table and accepting names shorten than 8 characters
            p = p.replace('Storage Unit', 'Storage_Unit')

            self._storage_volume_summary = _part_to_frame(p)
        return self._storage_volume_summary

    @property
    def outfall_loading_summary(self):
        """
        get the Outfall Loading Summary

        Returns:
            pandas.DataFrame: Outfall Loading Summary
        """
        if self._outfall_loading_summary is None:
            p = self.converted('Outfall Loading Summary')
            self._outfall_loading_summary = _part_to_frame(p.replace('Outfall Node', 'Outfall_Node '))
        return self._outfall_loading_summary

    @property
    def link_flow_summary(self):
        """
        get the Link Flow Summary

        Returns:
            pandas.DataFrame: Link Flow Summary
        """
        if self._link_flow_summary is None:
            p = self.converted('Link Flow Summary')
            self._link_flow_summary = _part_to_frame(p)
        return self._link_flow_summary

    @property
    def flow_classification_summary(self):
        """
        get the Flow Classification Summary

        Returns:
            pandas.DataFrame: Flow Classification Summary
        """
        if self._flow_classification_summary is None:
            p = self.converted('Flow Classification Summary')
            t = '---------- Fraction of Time in Flow Class ----------'
            p = p.replace(t, ' ' * len(t))
            self._flow_classification_summary = _part_to_frame(p)
        return self._flow_classification_summary

    @property
    def conduit_surcharge_summary(self):
        """
        get the Conduit Surcharge Summary

        Returns:
            pandas.DataFrame: Conduit Surcharge Summary
        """
        if self._conduit_surcharge_summary is None:
            p = self.converted('Conduit Surcharge Summary')

            # --------------------------------------------
            # if 'No conduits were surcharged.' in p:
            #     self._conduit_surcharge_summary = pd.DataFrame()
            #
            # else:
            p = p.replace('--------- Hours Full -------- ', 'HoursFull Hours Full HoursFull')
            p = p.replace('Both Ends', 'Both_Ends')
            self._conduit_surcharge_summary = _part_to_frame(p)
        return self._conduit_surcharge_summary

    def get_simulation_info(self):
        t = self.raw_parts.get('Simulation Infos', None)
        if t:
            return dict(line.strip().split(':', 1) for line in t.split('\n'))

    @property
    def analyse_start(self):
        v = self.get_simulation_info()['Analysis begun on']
        if v:
            return to_datetime(v)

    @property
    def analyse_end(self):
        v = self.get_simulation_info()['Analysis ended on']
        if v:
            return to_datetime(v)

    @property
    def analyse_duration(self):
        v = self.get_simulation_info()['Total elapsed time']
        if v:
            if '< 1 sec' in v:
                return Timedelta(seconds=1)

            return Timedelta(v)

    @staticmethod
    def _pprint(di):
        if not di:
            print('{}')
            return
        f = ''
        max_len = len(max(di.keys(), key=len)) + 5
        for key, value in di.items():
            if isinstance(value, (list, tuple, set)):
                key += f' ({len(value)})'
            key += ':'
            if isinstance(value, list) and len(value) > 20:
                start = 0
                for end in range(20, len(value), 20):
                    f += f'{key:<{max_len}}{", ".join(value[start:end])}\",\n'
                    key = ''
                    start = end
            else:
                f += f'{key:<{max_len}}{value}\n'
        print(f)

    def get_errors(self):
        t = self.raw_parts.get('Version+Title', None)
        di = dict()
        if t:
            for line in t.split('\n'):
                line = line.strip()
                if line.startswith('ERROR'):
                    label, txt = line.split(':', 1)
                    if label in di:
                        di[label].append(txt)
                    else:
                        di[label] = [txt]
        return di

    def print_errors(self):
        self._pprint(self.get_errors())

    def get_warnings(self):
        """
        WARNING 01: wet weather time step reduced to recording interval for Rain Gage xxx.
            The wet weather time step was automatically reduced so that no period with rainfall would be skipped
            during a simulation.
        WARNING 02: maximum depth increased for Node xxx.
            The maximum depth for the node was automatically increased to match the top of the highest connecting
            conduit.
        WARNING 03: negative offset ignored for Link xxx.
            The link’s stipulated offset was below the connecting node's invert so its actual offset was set to 0.
        WARNING 04: minimum elevation drop used for Conduit xxx.
            The elevation drop between the end nodes of the conduit was below 0.001 ft (0.00035 m) so the latter
            value was used instead to calculate its slope.
        WARNING 05: minimum slope used for Conduit xxx.
            The conduit's computed slope was below the user-specified Minimum Conduit Slope so the latter value was
            used instead.
        WARNING 06: dry weather time step increased to wet weather time step.
            The user-specified time step for computing runoff during dry weather periods was lower than that set for
            wet weather periods and was automatically increased to the wet weather value.
        WARNING 07: routing time step reduced to wet weather time step.
            The user-specified time step for flow routing was larger than the wet weather runoff time step and was
            automatically reduced to the runoff time step to prevent loss of accuracy.
        WARNING 08: elevation drop exceeds length for Conduit xxx.
            The elevation drop across the ends of a conduit exceeds its length. The program computes the conduit's
            slope as the elevation drop divided by the length instead of using the more accurate right triangle
            method. The user should check for errors in the length and in both the invert elevations and offsets at
            the conduit's upstream and downstream nodes.
        WARNING 09: time series interval greater than recording interval for Rain Gage xxx.
            The smallest time interval between entries in the precipitation time series used by the rain gage is
            greater than the recording time interval specified for the gage. If this was not actually intended then
            what appear to be continuous periods of rainfall in the time series will instead be read with time gaps
            in between them.
        WARNING 10: crest elevation is below downstream invert for regulator Link xxx.
            The height of the opening on an orifice, weir, or outlet is below the invert elevation of its downstream
            node. Users should check to see if the regulator's offset height or the downstream node's invert
            elevation is in error.
        WARNING 11: non-matching attributes in Control Rule xxx.
            The premise of a control is comparing two different types of attributes to one another (for example,
            conduit flow and junction water depth).
        """
        t = self.raw_parts.get('Version+Title', None)
        di = dict()
        if t:
            for line in t.split('\n'):
                line = line.strip()
                if line.startswith('WARNING'):

                    if ('WARNING 06' in line) or ('WARNING 07' in line):
                        di[line] = True
                    else:
                        *message, object_label = line.split()
                        message = ' '.join(message)
                        if message in di:
                            di[message].append(object_label)
                        else:
                            di[message] = [object_label]
        return di

    def print_warnings(self):
        self._pprint(self.get_warnings())


def read_rpt_file(report_filename):
    return SwmmReport(report_filename)
