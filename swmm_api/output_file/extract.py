# from: https://timcera.bitbucket.io/swmmtoolbox/docsrc/index.html
# https://bitbucket.org/timcera/swmmtoolbox/src/master/swmmtoolbox/swmmtoolbox.py
# copied to reduce dependencies
# ORIGINAL Author Tim Cera with BSD License
# Rewritten for custom use

# SWMM Version > 5.10.10
# Python Version >= 3.7

import copy
import datetime
import struct
# from collections import OrderedDict as dict


class OBJECTS:
    SUBCATCHMENT = "subcatchment"
    NODE = "node"
    LINK = "link"
    POLLUTANT = "pollutant"
    SYSTEM = "system"

    LIST_ = [SUBCATCHMENT, NODE, LINK, POLLUTANT, SYSTEM]


class VARIABLES:
    class SUBCATCHMENT:
        RAINFALL = "Rainfall"
        SNOW_DEPTH = "Snow_depth"
        EVAPORATION_LOSS = "Evaporation_loss"
        INFILTRATION_LOSS = "Infiltration_loss"
        RUNOFF_RATE = "Runoff_rate"
        GROUNDWATER_OUTFLOW = "Groundwater_outflow"
        GROUNDWATER_ELEVATION = "Groundwater_elevation"
        SOIL_MOISTURE = "Soil_moisture"

        LIST_ = [RAINFALL, SNOW_DEPTH, EVAPORATION_LOSS, INFILTRATION_LOSS, RUNOFF_RATE, GROUNDWATER_OUTFLOW,
                 GROUNDWATER_ELEVATION, SOIL_MOISTURE]

    class NODE:
        DEPTH_ABOVE_INVERT = 'Depth_above_invert'
        HYDRAULIC_HEAD = 'Hydraulic_head'
        VOLUME_STORED_PONDED = 'Volume_stored_ponded'
        LATERAL_INFLOW = 'Lateral_inflow'
        TOTAL_INFLOW = 'Total_inflow'
        FLOW_LOST_FLOODING = 'Flow_lost_flooding'

        LIST_ = [DEPTH_ABOVE_INVERT, HYDRAULIC_HEAD, VOLUME_STORED_PONDED, LATERAL_INFLOW, TOTAL_INFLOW,
                 FLOW_LOST_FLOODING]

    class LINK:
        FLOW_RATE = 'Flow_rate'
        FLOW_DEPTH = 'Flow_depth'
        FLOW_VELOCITY = 'Flow_velocity'
        FROUDE_NUMBER = 'Froude_number'
        CAPACITY = 'Capacity'

        LIST_ = [FLOW_RATE, FLOW_DEPTH, FLOW_VELOCITY, FROUDE_NUMBER, CAPACITY]

    class SYSTEM:
        AIR_TEMPERATURE = 'Air_temperature'
        RAINFALL = 'Rainfall'
        SNOW_DEPTH = 'Snow_depth'
        EVAPORATION_INFILTRATION = 'Evaporation_infiltration'
        RUNOFF = 'Runoff'
        DRY_WEATHER_INFLOW = 'Dry_weather_inflow'
        GROUNDWATER_INFLOW = 'Groundwater_inflow'
        RDII_INFLOW = 'RDII_inflow'
        USER_DIRECT_INFLOW = 'User_direct_inflow'
        TOTAL_LATERAL_INFLOW = 'Total_lateral_inflow'
        FLOW_LOST_TO_FLOODING = 'Flow_lost_to_flooding'
        FLOW_LEAVING_OUTFALLS = 'Flow_leaving_outfalls'
        VOLUME_STORED_WATER = 'Volume_stored_water'
        EVAPORATION_RATE = 'Evaporation_rate'
        POTENTIAL_PET = 'Potential_PET'

        LIST_ = [AIR_TEMPERATURE, RAINFALL, SNOW_DEPTH, EVAPORATION_INFILTRATION, RUNOFF, DRY_WEATHER_INFLOW,
                 GROUNDWATER_INFLOW, RDII_INFLOW, USER_DIRECT_INFLOW, TOTAL_LATERAL_INFLOW, FLOW_LOST_TO_FLOODING,
                 FLOW_LEAVING_OUTFALLS, VOLUME_STORED_WATER, EVAPORATION_RATE, POTENTIAL_PET]


VARIABLES_DICT = {
    OBJECTS.SUBCATCHMENT: VARIABLES.SUBCATCHMENT.LIST_,
    OBJECTS.NODE: VARIABLES.NODE.LIST_,
    OBJECTS.LINK: VARIABLES.LINK.LIST_,
    OBJECTS.POLLUTANT: [],
    OBJECTS.SYSTEM: VARIABLES.SYSTEM.LIST_,
}

_RECORDSIZE = 4
_FLOW_UNITS = ['CFS', 'GPM', 'MGD', 'CMS', 'LPS', 'MLD', None]
_CONCENTRATION_UNITS = ['MG', 'UG', 'COUNTS']
_MAGIC_NUMBER = 516114522
_PROPERTY_LABELS = ['type', 'area', 'invert', 'max_depth', 'offset', 'length']
_PROPERTY_FORMAT = lambda p: {'type': 'i'}.get(p, 'f')
_NODES_TYPES = ['JUNCTION', 'OUTFALL', 'STORAGE', 'DIVIDER']
_LINK_TYPES = ['CONDUIT', 'PUMP', 'ORIFICE', 'WEIR', 'OUTLET']


def _add_index(l):
    counts = {}
    for i, name in enumerate(l):
         if name in counts:
             counts[name] += 1
             l[i] = f"{name}_{counts[name]}"
         else:
             counts[name] = 1
    return l


class SwmmExtractValueError(Exception):
    def __init__(self, message):
        super().__init__("\n*\n*   {}\n*\n".format(message))


class SwmmOutExtract:
    """The class that handles all extraction of data from the out file."""
    def __init__(self, filename):
        self.fp = open(filename, "rb")

        # ____
        self.fp.seek(-6 * _RECORDSIZE, 2)
        (
            _pos_start_labels,  # starting file position of ID names
            _pos_start_input,  # starting file position of input data
            self.pos_start_output,  # starting file position of output data
            self.n_periods,  # Number of reporting periods
            error_code,
            magic_num_end,
        ) = self._next(6)

        # ____
        self.fp.seek(0, 0)
        magic_num_start = self._next()

        # ____
        # check errors
        if magic_num_start != _MAGIC_NUMBER:
            raise SwmmExtractValueError('Beginning magic number incorrect.')
        if magic_num_end != _MAGIC_NUMBER:
            raise SwmmExtractValueError('Ending magic number incorrect.')
        if error_code != 0:
            raise SwmmExtractValueError(f'Error code "{error_code}" in output file indicates a problem with the run.')
        if self.n_periods == 0:
            raise SwmmExtractValueError('There are zero time periods in the output file.')

        # ---
        # read additional parameters from start of file
        # Version number i.e. "51015"
        self.swmm_version, self.flow_unit, n_subcatch, n_nodes, n_links, n_pollutants = self._next(6)
        self.flow_unit = _FLOW_UNITS[self.flow_unit]

        # ____
        # Read in the names
        # get the dictionary of the object labels for each object type (link, node, subcatchment)
        self.fp.seek(_pos_start_labels, 0)
        self.labels = dict()
        for kind, n in zip(OBJECTS.LIST_, [n_subcatch, n_nodes, n_links, n_pollutants, 0]):
            self.labels[kind] = [self._next(n=self._next(), dtype='s') for _ in range(n)]

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
        self.pollutant_units = dict(zip(self.labels[OBJECTS.POLLUTANT],
                                        [_CONCENTRATION_UNITS[p] for p in self._next(n_pollutants, flat=False)]))

        # ____
        # property values for subcatchments, nodes and links
        #   subcatchment
        #     area
        #   node
        #     type, invert, & max. depth
        #   link
        #     type, offsets [ht. above start node invert (ft), ht. above end node invert (ft)], max. depth, & length
        self.model_properties = dict()
        for kind in [OBJECTS.SUBCATCHMENT, OBJECTS.NODE, OBJECTS.LINK]:
            self.model_properties[kind] = dict()
            # ------
            # read the property labels per object type
            property_labels = list()
            for i in list(self._next(self._next(), flat=False)):
                property_label = _PROPERTY_LABELS[i]
                if property_label in property_labels:
                    property_label += '_2'
                property_labels.append(property_label)
            # ------
            # read the values per object and per property
            for label in self.labels[kind]:
                self.model_properties[kind][label] = dict()
                for property_label in property_labels:
                    value = self._next(dtype=_PROPERTY_FORMAT(property_label))
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
        self._bytes_per_period = None

    def __repr__(self):
        return f'SwmmOutExtract(file="{self.filename}")'

    @property
    def filename(self):
        return self.fp.name

    @property
    def bytes_per_period(self):
        # Calculate the bytes for each time period when
        # reading the computed results
        if self._bytes_per_period is None:
            self._bytes_per_period = 2  # for the datetime
            for obj in [OBJECTS.SUBCATCHMENT, OBJECTS.NODE, OBJECTS.LINK]:
                self._bytes_per_period += len(self.variables[obj]) * len(self.labels[obj])
            self._bytes_per_period += len(self.variables[OBJECTS.SYSTEM])
            self._bytes_per_period *= _RECORDSIZE

        return self._bytes_per_period

    def _next(self, n=1, dtype='i', flat=True):
        size = {'d': 2}.get(dtype, 1)
        if dtype == 's':
            s = self._next_base(f'{n}s', n)[0]
            return str(s, encoding="ascii", errors="replace")
        elif flat and (n == 1):
            return self._next_base(dtype, size * _RECORDSIZE)[0]
        else:
            return self._next_base(f'{n}{dtype}', n * size * _RECORDSIZE)

    def _next_base(self, fmt, size):
        return struct.unpack(fmt, self.fp.read(size))

    def _value_offset(self, kind, label, variable, period):
        itemindex = self.labels[kind].index(str(label))

        return (self.pos_start_output + period * self.bytes_per_period
                + _RECORDSIZE * (2 + variable
                                 + {0: itemindex * self.n_vars_subcatch,
                                    1: self.n_subcatch * self.n_vars_subcatch + itemindex * self.n_vars_node,
                                    2: self.n_subcatch * self.n_vars_subcatch + self.n_nodes * self.n_vars_node +
                                       itemindex * self.n_vars_link,
                                    4: self.n_subcatch * self.n_vars_subcatch + self.n_nodes * self.n_vars_node +
                                       self.n_links * self.n_vars_link
                                    }[kind]))

    def get_swmm_results(self, itemtype, name, variableindex, period):
        offset = self._value_offset(itemtype, name, variableindex, period)
        self.fp.seek(offset, 0)
        value = struct.unpack("f", self.fp.read(_RECORDSIZE))[0]
        return value