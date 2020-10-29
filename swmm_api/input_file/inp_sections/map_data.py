from pandas import DataFrame

from .indices import Indices
from ..inp_helpers import InpSectionGeneric, UserDict_, dataframe_to_inp_string, txt_to_lines


class CoordinatesSection(UserDict_, InpSectionGeneric):
    index = Indices.Node
    """
    Section:
        [COORDINATES]

    Purpose:
        Assigns X,Y coordinates to drainage system nodes.

    Format:
        Node Xcoord Ycoord

    Remarks:
        Node
            name of node.
        Xcoord
            horizontal coordinate relative to origin in lower left of map.
        Ycoord
            vertical coordinate relative to origin in lower left of map.
    """

    @classmethod
    def from_lines(cls, lines):
        if isinstance(lines, str):
            lines = txt_to_lines(lines)

        new = cls()
        for line in lines:
            node, x, y = line
            new._data[node] = {'x': float(x), 'y': float(y)}
        return new

    def __repr__(self):
        return self.data_frame.__repr__()

    def __str__(self):
        return self.to_inp()

    def to_inp(self, fast=False):
        if self.empty:
            return '; NO data'
        if fast:
            f = ''
            max_len_name = len(max(self._data.keys(), key=len)) + 2
            f += '{name} {x} {y}\n'.format(name='; {}'.format(self.INDEX.capitalize()).ljust(max_len_name), x='x', y='y')
            for node, coords in self._data.items():
                f += '{name} {x} {y}\n'.format(name=node.ljust(max_len_name), **coords)
        else:
            f = dataframe_to_inp_string(self.data_frame)
        return f

    @property
    def data_frame(self):
        return DataFrame.from_dict(self._data, orient='index')

    @classmethod
    def from_pandas(cls, data, x_name='x', y_name='y'):
        new = cls()
        df = data[[x_name, y_name]].rename({x_name: 'x', y_name: 'y'})
        new._data = df[['x', 'y']].to_dict(orient='index')
        return new


class SymbolSection(CoordinatesSection):
    index = Indices.Gage
    """
    Section:
        [SYMBOLS]

    Purpose:
        Assigns X,Y coordinates to rain gage symbols.

    Format:
        Gage Xcoord Ycoord

    Remarks:
        Gage
            name of rain gage.
        Xcoord
            horizontal coordinate relative to origin in lower left of map.
        Ycoord
            vertical coordinate relative to origin in lower left of map.
    """


class VerticesSection(UserDict_, InpSectionGeneric):
    """
    Section:
        [VERTICES]

    Purpose:
        Assigns X,Y coordinates to interior vertex points of curved drainage system links.

    Format:
        Link Xcoord Ycoord

    Remarks:
        Node
            name of link.
        Xcoord
            horizontal coordinate of vertex relative to origin in lower left of map.
        Ycoord
            vertical coordinate of vertex relative to origin in lower left of map.

        Include a separate line for each interior vertex of the link, ordered from the inlet node to the outlet node.

        Straight-line links have no interior vertices and therefore are not listed in this section.
    """

    @classmethod
    def from_lines(cls, lines):
        if isinstance(lines, str):
            lines = txt_to_lines(lines)

        new = cls()
        for line in lines:
            link, x, y = line
            if link not in new._data:
                new._data[link] = list()

            new._data[link].append({'x': float(x), 'y': float(y)})
        return new

    def __repr__(self):
        return self.data_frame.__repr__()

    def __str__(self):
        return self.to_inp()

    def to_inp(self, fast=False):
        if self.empty:
            return '; NO data'

        if fast:
            f = ''
            max_len_name = len(max(self._data.keys(), key=len)) + 2
            f += '{name} {x} {y}\n'.format(name='; Link'.ljust(max_len_name), x='x', y='y')
            for link, vertices in self._data.items():
                for v in vertices:
                    f += '{name} {x} {y}\n'.format(name=link.ljust(max_len_name), **v)
        else:
            f = dataframe_to_inp_string(self.data_frame)
        return f

    @property
    def data_frame(self):
        rec = list()
        for link, vertices in self._data.items():
            for v in vertices:
                rec.append([link, v['x'], v['y']])

        return DataFrame.from_records(rec).rename(columns={0: 'Link',
                                                           1: 'x',
                                                           2: 'y'}).set_index('Link', drop=True)

    @classmethod
    def from_pandas(cls, data, x_name='x', y_name='y'):
        new = cls()
        df = data[[x_name, y_name]].rename({x_name: 'x', y_name: 'y'})
        new._data = df[['x', 'y']].groupby(df.index).apply(lambda x: x.to_dict('records')).to_dict()
        return new


class PolygonSection(VerticesSection):
    """
    Section:
        [POLYGONS]

    Purpose:
        Assigns X,Y coordinates to vertex points of polygons that define a subcatchment boundary.

    Format:
        Link Xcoord Ycoord

    Remarks:
        Subcat
            name of subcatchment.
        Xcoord
            horizontal coordinate of vertex relative to origin in lower left of map.
        Ycoord
            vertical coordinate of vertex relative to origin in lower left of map.

        Include a separate line for each vertex of the subcatchment polygon, ordered in a
        consistent clockwise or counter-clockwise sequence.
    """


class MapSection(InpSectionGeneric):
    """
    Section:
        [MAP]

    Purpose:
        Provides dimensions and distance units for the map.

    Formats:
        DIMENSIONS X1 Y1 X2 Y2
        UNITS FEET / METERS / DEGREES / NONE

    Remarks:
    X1
        lower-left X coordinate of full map extent
    Y1
        lower-left Y coordinate of full map extent
    X2
        upper-right X coordinate of full map extent
    Y2
         upper-right Y coordinate of full map extent
    """
    class Parts:
        DIMENSIONS = 'DIMENSIONS'
        UNITS = 'UNITS'

    def __init__(self, dimensions, units='Meters'):
        self.lower_left_x = dimensions[0]
        self.lower_left_y = dimensions[1]
        self.upper_right_x = dimensions[2]
        self.upper_right_y = dimensions[3]
        self.units = units

    def copy(self):
        return type(self)([self.lower_left_x,
                           self.lower_left_y,
                           self.upper_right_x,
                           self.upper_right_y], self.units)

    @classmethod
    def from_lines(cls, lines):
        if isinstance(lines, str):
            lines = txt_to_lines(lines)

        args = list()
        for line in lines:
            name = line[0]
            if name == cls.Parts.DIMENSIONS:
                args.append(line[1:])

            elif name == cls.Parts.UNITS:
                args.append(line[1])
            else:
                pass
        new_map = cls(*args)
        return new_map

    # def __repr__(self):
    #     pass
    #
    # def __str__(self):
    #     return self.to_inp()
    #     pass

    def to_inp(self, fast=False):
        s = '{} {}\n'.format(self.Parts.DIMENSIONS, ' '.join([str(i) for i in [self.lower_left_x, self.lower_left_y,
                                                                             self.upper_right_x, self.upper_right_y]]))
        s += '{} {}'.format(self.Parts.UNITS, self.units)
        return s
