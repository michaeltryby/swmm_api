# from: https://timcera.bitbucket.io/swmmtoolbox/docsrc/index.html
# https://bitbucket.org/timcera/swmmtoolbox/src/master/swmmtoolbox/swmmtoolbox.py
# copied to reduce dependencies
# ORIGINAL Author Tim Cera with BSD License
# Rewritten for custom use

# SWMM Version > 5.10.10
# Python Version >= 3.7

import copy
from os import remove

import datetime
import struct
from io import SEEK_END, SEEK_SET
from tqdm.auto import tqdm
from warnings import warn

from .definitions import OBJECTS, VARIABLES
from .._read_bin import BinaryReader

VARIABLES_DICT = {
    OBJECTS.SUBCATCHMENT: VARIABLES.SUBCATCHMENT.LIST_,
    OBJECTS.NODE        : VARIABLES.NODE.LIST_,
    OBJECTS.LINK        : VARIABLES.LINK.LIST_,
    OBJECTS.POLLUTANT   : [],
    OBJECTS.SYSTEM      : VARIABLES.SYSTEM.LIST_,
}

_RECORDSIZE = 4
_FLOW_UNITS_METRIC = ['CMS', 'LPS', 'MLD']
_FLOW_UNITS_IMPERIAL = ['CFS', 'GPM', 'MGD']
_FLOW_UNITS = _FLOW_UNITS_IMPERIAL + _FLOW_UNITS_METRIC + [None]
_CONCENTRATION_UNITS = ['MG', 'UG', 'COUNTS']
_MAGIC_NUMBER = 516114522
_PROPERTY_LABELS = ['type', 'area', 'invert', 'max_depth', 'offset', 'length']
_NODES_TYPES = ['JUNCTION', 'OUTFALL', 'STORAGE', 'DIVIDER']
_LINK_TYPES = ['CONDUIT', 'PUMP', 'ORIFICE', 'WEIR', 'OUTLET']


class SwmmExtractValueError(Exception):
    def __init__(self, message):
        super().__init__("\n*\n*   {}\n*\n".format(message))


class SwmmOutExtractWarning(UserWarning):
    pass


class SwmmOutExtract(BinaryReader):
    """
    The class that handles all extraction of data from the out file.

    Attributes:
        flow_unit (str): Flow unit. One of ['CMS', 'LPS', 'MLD', 'CFS', 'GPM', 'MGD']
        labels (dict[str, list]): dictionary of the object labels as list (value) for each object type
            (keys are: ``'link'``, ``'node'``, ``'subcatchment'``)
        model_properties (dict[str, [dict[str, list]]]): property values for the subcatchments, nodes and links. 
            The Properties for the objects are.
        
                    - ``subcatchment``
                      - [area]
                    - ``node``
                      - [type, invert, max. depth]
                    - ``link``
                      - type, 
                      - offsets
                        - ht. above start node invert (ft), 
                        - ht. above end node invert (ft), 
                      - max. depth,
                      - length
        
        n_periods (int): number of periods (=index-values)
        pollutant_units (dict[str, str]): Units per pollutant.
        _pos_start_output (int): Start position of the data.
        report_interval (datetime.timedelta): Intervall of the index.
        start_date (datetime.datetime): Start date of the data.
        swmm_version (str): SWMM Version
        variables (dict[str, list]): variables per object-type inclusive the pollutants.
    """

    def __init__(self, filename):
        super().__init__(filename)

        # ____
        self.fp.seek(-6 * _RECORDSIZE, SEEK_END)
        (
            _pos_start_labels,  # starting file position of ID names
            _pos_start_input,  # starting file position of input data
            _pos_start_output,  # starting file position of output data
            _n_periods,  # Number of reporting periods
            error_code,
            magic_num_end,
        ) = self._next(6)

        # ____
        self.fp.seek(0, SEEK_SET)
        magic_num_start = self._next()

        # ____
        # check errors
        if magic_num_start != _MAGIC_NUMBER:
            raise SwmmExtractValueError('Beginning magic number incorrect.')

        if magic_num_end != _MAGIC_NUMBER:
            warn('Ending magic number incorrect.', SwmmOutExtractWarning)
            # raise SwmmExtractValueError('Ending magic number incorrect.')
            _n_periods = 0
        elif error_code != 0:
            warn(f'Error code "{error_code}" in output file indicates a problem with the run.', SwmmOutExtractWarning)
            # raise SwmmExtractValueError(f'Error code "{error_code}" in output file indicates a problem with the run.')

        # ---
        # read additional parameters from start of file
        # Version number i.e. "51015"
        self.swmm_version, self.flow_unit, n_subcatch, n_nodes, n_links, n_pollutants = self._next(6)
        self.flow_unit = _FLOW_UNITS[self.flow_unit]

        # ____
        # self.fp.seek(_pos_start_labels, SEEK_SET)  # not needed!
        # print(self.fp.tell(), _pos_start_labels)
        # assert _pos_start_labels == self.fp.tell()
        # ____
        # Read in the names
        # get the dictionary of the object labels for each object type (link, node, subcatchment)
        self.labels = {}
        for kind, n in zip(OBJECTS.LIST_, [n_subcatch, n_nodes, n_links, n_pollutants, 0]):
            self.labels[kind] = [self._next(n=self._next(), dtype='s') for _ in range(n)]

        # ____
        # print(self.fp.tell(), _pos_start_input)
        # assert _pos_start_input == self.fp.tell()
        # ____
        # Update variables to add pollutant names to subcatchment, nodes, and links.
        # get the dictionary of the object variables for each object type (link, node, subcatchment)
        self.variables = copy.deepcopy(VARIABLES_DICT)
        for kind in [OBJECTS.SUBCATCHMENT, OBJECTS.NODE, OBJECTS.LINK]:
            self.variables[kind] += self.labels[OBJECTS.POLLUTANT]

        # ____
        # System vars do not have names per se, but made names = number labels
        self.labels[OBJECTS.SYSTEM] = ['']  # self.variables[OBJECTS.SYSTEM]

        # ____
        # Read codes of pollutant concentration UNITS = Number of pollutants * 4 byte integers
        _pollutant_unit_labels = [_CONCENTRATION_UNITS[p] if p < len(_CONCENTRATION_UNITS) else 'NaN'
                                  for p in self._next(n_pollutants, flat=False)]
        self.pollutant_units = dict(zip(self.labels[OBJECTS.POLLUTANT], _pollutant_unit_labels))

        # ____
        # property values for subcatchments, nodes and links
        #   subcatchment
        #     area
        #   node
        #     type, invert, & max. depth
        #   link
        #     type, offsets [ht. above start node invert (ft), ht. above end node invert (ft)], max. depth, & length
        self.model_properties = {}
        for kind in [OBJECTS.SUBCATCHMENT, OBJECTS.NODE, OBJECTS.LINK]:
            self.model_properties[kind] = {}
            # ------
            # read the property labels per object type
            property_labels = []
            for i in list(self._next(self._next(), flat=False)):
                property_label = _PROPERTY_LABELS[i]
                if property_label in property_labels:
                    property_label += '_2'
                property_labels.append(property_label)
            # ------
            # read the values per object and per property
            for label in self.labels[kind]:
                self.model_properties[kind][label] = {}
                for property_label in property_labels:
                    value = self._next(dtype={'type': 'i'}.get(property_label, 'f'))
                    if property_label == 'type':
                        value = {OBJECTS.NODE: _NODES_TYPES, OBJECTS.LINK: _LINK_TYPES}[kind][value]
                    self.model_properties[kind][label][property_label] = value

        # ____
        # double check variables
        for kind in [OBJECTS.SUBCATCHMENT, OBJECTS.NODE, OBJECTS.LINK, OBJECTS.SYSTEM]:
            n_vars = self._next()
            assert n_vars == len(self.variables[kind])
            self._next(n_vars)

        # ____
        self.start_date = datetime.datetime(1899, 12, 30) + datetime.timedelta(days=self._next(dtype='d'))
        self.report_interval = datetime.timedelta(seconds=self._next())

        # ____
        self._bytes_per_period = self._infer_bytes_per_period()

        # ____
        # print(self.fp.tell(), _pos_start_output)
        # assert _pos_start_output == self.fp.tell()
        # if _pos_start_output == 0:
        # Out File not complete!
        self._pos_start_output = self.fp.tell()

        self.n_periods = _n_periods
        if _n_periods == 0:
            self._infer_n_periods()
            warn('Infer time periods of the output file due to an corrupt SWMM .out-file.', SwmmOutExtractWarning)

        if self.n_periods == 0:
            warn('There are zero time periods in the output file.', SwmmOutExtractWarning)
            # raise SwmmExtractValueError('There are zero time periods in the output file.')

    def __repr__(self):
        return f'SwmmOutExtract(file="{self.filename}")'

    def _infer_bytes_per_period(self):
        """
        Calculate the bytes for each time period when reading the computed results

        Returns:
            int: bytes per period
        """
        _bytes_per_period = 2  # for the datetime
        for obj in [OBJECTS.SUBCATCHMENT, OBJECTS.NODE, OBJECTS.LINK]:
            _bytes_per_period += len(self.variables[obj]) * len(self.labels[obj])
        _bytes_per_period += len(self.variables[OBJECTS.SYSTEM])
        _bytes_per_period *= _RECORDSIZE
        return _bytes_per_period

    def _get_selective_results(self, columns):
        """
        get results of selective columns in .out-file

        this function is due to its iterative reading slow,
        but has it advantages with out-files with many columns (>1000) and fewer time-steps

        Args:
            columns (list[tuple]): list of column identifier tuple with [(kind, label, variable), ...]

        Returns:
            dict[str, list]: dictionary where keys are the column names ('/' as separator) and values are the list of result values
        """
        n_vars_subcatch = len(self.variables[OBJECTS.SUBCATCHMENT])
        n_vars_node = len(self.variables[OBJECTS.NODE])
        n_vars_link = len(self.variables[OBJECTS.LINK])

        n_subcatch = len(self.labels[OBJECTS.SUBCATCHMENT])
        n_nodes = len(self.labels[OBJECTS.NODE])
        n_links = len(self.labels[OBJECTS.LINK])

        offset_list = []
        values = {}

        for kind, label, variable in columns:
            values['/'.join([kind, label, variable])] = []

            index_kind = OBJECTS.LIST_.index(kind)
            index_variable = self.variables[kind].index(variable)
            item_index = self.labels[kind].index(str(label))
            offset_list.append((2 + index_variable + {
                0: (item_index * n_vars_subcatch),
                1: (n_subcatch * n_vars_subcatch +
                    item_index * n_vars_node),
                2: (n_subcatch * n_vars_subcatch +
                    n_nodes * n_vars_node +
                    item_index * n_vars_link),
                4: (n_subcatch * n_vars_subcatch +
                    n_nodes * n_vars_node +
                    n_links * n_vars_link)
            }[index_kind])*_RECORDSIZE)

        # offset_list = [o*_RECORDSIZE for o in offset_list]
        # cols = list(values.keys())
        # cols_sorted = sorted(cols, key=lambda e: offset_list[cols.index(e)])
        # offset_sorted = sorted(offset_list)
        # iter_label_offset = tuple(zip(cols_sorted, offset_sorted))
        iter_label_offset = tuple(zip(values.keys(), offset_list))

        for period_offset in tqdm(range(self._pos_start_output,  # start
                                        self._pos_start_output + self.n_periods * self._bytes_per_period,  # stop
                                        self._bytes_per_period),
                                  desc=f'{repr(self)}.get_selective_results(n_cols={len(columns)})'):  # step
            # period_offset = self.pos_start_output + period * self.bytes_per_period
            for label, offset in iter_label_offset:
                self._set_position(offset + period_offset)
                values[label].append(self._next_float())

        return values

    def _infer_n_periods(self):
        not_done = True
        period = 0
        while not_done:
            self.fp.seek(self._pos_start_output + period * self._bytes_per_period, SEEK_SET)
            try:
                dt = self._next(dtype='d')
                # print(dt)
                # print(datetime.datetime(1899, 12, 30) + datetime.timedelta(days=dt))
                period += 1
            except:
                not_done = False

        self.n_periods = period - 1
