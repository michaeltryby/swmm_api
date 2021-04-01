# from: https://timcera.bitbucket.io/swmmtoolbox/docsrc/index.html
# copied to reduce dependencies
# copyright (c) Author Tim Cera with BSD License

import copy
import datetime
import struct


VARCODE = {
    0: {
        0: "Rainfall",
        1: "Snow_depth",
        2: "Evaporation_loss",
        3: "Infiltration_loss",
        4: "Runoff_rate",
        5: "Groundwater_outflow",
        6: "Groundwater_elevation",
        7: "Soil_moisture",
    },
    1: {
        0: "Depth_above_invert",
        1: "Hydraulic_head",
        2: "Volume_stored_ponded",
        3: "Lateral_inflow",
        4: "Total_inflow",
        5: "Flow_lost_flooding",
    },
    2: {
        0: "Flow_rate",
        1: "Flow_depth",
        2: "Flow_velocity",
        3: "Froude_number",
        4: "Capacity",
    },
    4: {
        0: "Air_temperature",
        1: "Rainfall",
        2: "Snow_depth",
        3: "Evaporation_infiltration",
        4: "Runoff",
        5: "Dry_weather_inflow",
        6: "Groundwater_inflow",
        7: "RDII_inflow",
        8: "User_direct_inflow",
        9: "Total_lateral_inflow",
        10: "Flow_lost_to_flooding",
        11: "Flow_leaving_outfalls",
        12: "Volume_stored_water",
        13: "Evaporation_rate",
        14: "Potential_PET",
    },
}


class SwmmExtract:
    """The class that handles all extraction of data from the out file."""

    def __init__(self, filename):

        self.RECORDSIZE = 4

        self.fp = open(filename, "rb")

        self.fp.seek(-6 * self.RECORDSIZE, 2)

        (
            self.Namesstartpos,
            self.offset0,
            self.startpos,
            self.swmm_nperiods,
            errcode,
            magic2,
        ) = struct.unpack("6i", self.fp.read(6 * self.RECORDSIZE))

        self.fp.seek(0, 0)
        magic1 = struct.unpack("i", self.fp.read(self.RECORDSIZE))[0]

        if magic1 != 516114522:
            raise ValueError(
                """
*
*   Beginning magic number incorrect.
*
"""
            )
        if magic2 != 516114522:
            raise ValueError(
                """
*
*   Ending magic number incorrect.
*
"""
            )
        if errcode != 0:
            raise ValueError(
                """
*
*   Error code "{0}" in output file indicates a problem with the run.
*
""".format(
                    errcode
                )
            )
        if self.swmm_nperiods == 0:
            raise ValueError(
                """
*
*   There are zero time periods in the output file.
*
"""
            )

        # --- otherwise read additional parameters from start of file
        (
            version,
            self.swmm_flowunits,
            self.swmm_nsubcatch,
            self.swmm_nnodes,
            self.swmm_nlinks,
            self.swmm_npolluts,
        ) = struct.unpack("6i", self.fp.read(6 * self.RECORDSIZE))

        self.itemlist = ["subcatchment", "node", "link", "pollutant", "system"]

        # Read in the names
        self.fp.seek(self.Namesstartpos, 0)
        self.names = {0: [], 1: [], 2: [], 3: [], 4: []}
        number_list = [
            self.swmm_nsubcatch,
            self.swmm_nnodes,
            self.swmm_nlinks,
            self.swmm_npolluts,
        ]
        for i, j in enumerate(number_list):
            for _ in range(j):
                stringsize = struct.unpack("i", self.fp.read(self.RECORDSIZE))[0]
                self.names[i].append(
                    struct.unpack("{0}s".format(stringsize), self.fp.read(stringsize))[
                        0
                    ]
                )

        # Stupid Python 3
        for key in self.names:
            collect_names = []
            for name in self.names[key]:
                # Why would SWMM allow spaces in names?  Anyway...
                try:
                    rname = str(name, "ascii", "replace")
                except TypeError:
                    rname = name.decode("ascii", "replace")
                try:
                    collect_names.append(rname.decode())
                except AttributeError:
                    collect_names.append(rname)
            self.names[key] = collect_names

        # Update self.varcode to add pollutant names to subcatchment,
        # nodes, and links.
        self.varcode = copy.deepcopy(VARCODE)
        for itemtype in ["subcatchment", "node", "link"]:
            typenumber = self.type_check(itemtype)
            start = len(VARCODE[typenumber])
            end = start + len(self.names[3])
            nlabels = list(range(start, end))
            ndict = dict(list(zip(nlabels, self.names[3])))
            self.varcode[typenumber].update(ndict)

        # Read pollutant concentration codes
        # = Number of pollutants * 4 byte integers
        self.pollutant_codes = struct.unpack(
            "{0}i".format(self.swmm_npolluts),
            self.fp.read(self.swmm_npolluts * self.RECORDSIZE),
        )

        self.propcode = {}

        # self.prop[0] contain property codes and values for
        # subcatchments
        # self.prop[1] contain property codes and values for nodes
        # self.prop[2] contain property codes and values for links
        self.prop = {0: [], 1: [], 2: []}

        # subcatchments
        nsubprop = struct.unpack("i", self.fp.read(self.RECORDSIZE))[0]
        self.propcode[0] = struct.unpack(
            "{0}i".format(nsubprop), self.fp.read(nsubprop * self.RECORDSIZE)
        )
        for i in range(self.swmm_nsubcatch):
            rprops = struct.unpack(
                "{0}f".format(nsubprop), self.fp.read(nsubprop * self.RECORDSIZE)
            )
            self.prop[0].append(list(zip(self.propcode[0], rprops)))

        # nodes
        nnodeprop = struct.unpack("i", self.fp.read(self.RECORDSIZE))[0]
        self.propcode[1] = struct.unpack(
            "{0}i".format(nnodeprop), self.fp.read(nnodeprop * self.RECORDSIZE)
        )
        for i in range(self.swmm_nnodes):
            rprops = struct.unpack(
                "{0}f".format(nnodeprop), self.fp.read(nnodeprop * self.RECORDSIZE)
            )
            self.prop[1].append(list(zip(self.propcode[1], rprops)))

        # links
        nlinkprop = struct.unpack("i", self.fp.read(self.RECORDSIZE))[0]
        self.propcode[2] = struct.unpack(
            "{0}i".format(nlinkprop), self.fp.read(nlinkprop * self.RECORDSIZE)
        )
        for i in range(self.swmm_nlinks):
            rprops = struct.unpack(
                "{0}f".format(nlinkprop), self.fp.read(nlinkprop * self.RECORDSIZE)
            )
            self.prop[2].append(list(zip(self.propcode[2], rprops)))

        self.vars = {}
        self.swmm_nsubcatchvars = struct.unpack("i", self.fp.read(self.RECORDSIZE))[0]
        self.vars[0] = struct.unpack(
            "{0}i".format(self.swmm_nsubcatchvars),
            self.fp.read(self.swmm_nsubcatchvars * self.RECORDSIZE),
        )

        self.nnodevars = struct.unpack("i", self.fp.read(self.RECORDSIZE))[0]
        self.vars[1] = struct.unpack(
            "{0}i".format(self.nnodevars),
            self.fp.read(self.nnodevars * self.RECORDSIZE),
        )

        self.nlinkvars = struct.unpack("i", self.fp.read(self.RECORDSIZE))[0]
        self.vars[2] = struct.unpack(
            "{0}i".format(self.nlinkvars),
            self.fp.read(self.nlinkvars * self.RECORDSIZE),
        )

        self.vars[3] = [0]

        self.nsystemvars = struct.unpack("i", self.fp.read(self.RECORDSIZE))[0]
        self.vars[4] = struct.unpack(
            "{0}i".format(self.nsystemvars),
            self.fp.read(self.nsystemvars * self.RECORDSIZE),
        )

        # System vars do not have names per se, but made names = number labels
        self.names[4] = [self.varcode[4][i] for i in self.vars[4]]

        self.startdate = struct.unpack("d", self.fp.read(2 * self.RECORDSIZE))[0]
        days = int(self.startdate)
        seconds = (self.startdate - days) * 86400
        self.startdate = datetime.datetime(1899, 12, 30) + datetime.timedelta(
            days=days, seconds=seconds
        )

        self.reportinterval = struct.unpack("i", self.fp.read(self.RECORDSIZE))[0]
        self.reportinterval = datetime.timedelta(seconds=self.reportinterval)

        # Calculate the bytes for each time period when
        # reading the computed results
        self.bytesperperiod = self.RECORDSIZE * (
            2
            + self.swmm_nsubcatch * self.swmm_nsubcatchvars
            + self.swmm_nnodes * self.nnodevars
            + self.swmm_nlinks * self.nlinkvars
            + self.nsystemvars
        )

    def type_check(self, itemtype):
        if itemtype in [0, 1, 2, 3, 4]:
            return itemtype
        try:
            typenumber = self.itemlist.index(itemtype)
        except ValueError:
            raise ValueError("""
*
*   Type argument "{0}" is incorrect.
*   Must be in "{1}".
*""".format(itemtype, list(range(5)) + self.itemlist))
        return typenumber

    def name_check(self, itemtype, itemname):
        self.itemtype = self.type_check(itemtype)
        try:
            itemindex = self.names[self.itemtype].index(str(itemname))
        except (ValueError, KeyError):
            raise ValueError("""
*
*   {0} was not found in "{1}" list.
*
""".format(itemname, itemtype))
        return (itemname, itemindex)

    def get_swmm_results(self, itemtype, name, variableindex, period):
        if itemtype not in [0, 1, 2, 4]:
            raise ValueError("Type must be one of subcatchment (0), node (1). link (2), or system (4).\n"
                             "You gave \"{0}\".".format(itemtype))

        _, itemindex = self.name_check(itemtype, name)

        date_offset = self.startpos + period * self.bytesperperiod

        # Rewind
        self.fp.seek(date_offset, 0)

        date = struct.unpack("d", self.fp.read(2 * self.RECORDSIZE))[0]

        offset = date_offset + 2 * self.RECORDSIZE  # skip the date

        if itemtype == 0:
            offset = offset + self.RECORDSIZE * (itemindex * self.swmm_nsubcatchvars)
        elif itemtype == 1:
            offset = offset + self.RECORDSIZE * (
                self.swmm_nsubcatch * self.swmm_nsubcatchvars
                + itemindex * self.nnodevars
            )
        elif itemtype == 2:
            offset = offset + self.RECORDSIZE * (
                self.swmm_nsubcatch * self.swmm_nsubcatchvars
                + self.swmm_nnodes * self.nnodevars
                + itemindex * self.nlinkvars
            )
        elif itemtype == 4:
            offset = offset + self.RECORDSIZE * (
                self.swmm_nsubcatch * self.swmm_nsubcatchvars
                + self.swmm_nnodes * self.nnodevars
                + self.swmm_nlinks * self.nlinkvars
            )
        offset = offset + self.RECORDSIZE * variableindex

        self.fp.seek(offset, 0)
        value = struct.unpack("f", self.fp.read(self.RECORDSIZE))[0]
        return (date, value)

    # def get_dates(self):
    #     """Return start and end date tuple."""
    #     begindate = datetime.datetime(1899, 12, 30)
    #     ntimes = list(range(self.swmm_nperiods))
    #     periods = [ntimes[0], ntimes[-1]]
    #     st_end = []
    #     for period in periods:
    #         date_offset = self.startpos + period * self.bytesperperiod
    #         self.fp.seek(date_offset, 0)
    #         day = struct.unpack("d", self.fp.read(2 * self.RECORDSIZE))[0]
    #         st_end.append(begindate + datetime.timedelta(days=int(day)))
    #     return st_end
