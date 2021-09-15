import pandas as pd

from swmm_api import SwmmInput
from swmm_api.input_file import section_labels as sections
from swmm_api.input_file.helpers import InpSection
from swmm_api.input_file.sections import Junction, Coordinate

df1 = pd.DataFrame(columns=[['Sohlhöhe[m NN]', 'Deckelhöhe[m NN]', 'X-Koordinate[m]', 'Y-Koordinate[m]']])
df1.index.name = 'Label'

inp = SwmmInput()
inp[sections.JUNCTIONS] = InpSection(Junction)
inp[sections.COORDINATES] = InpSection(Coordinate)
for index, row in df1.iterrows():
    inp[sections.JUNCTIONS].add_obj(Junction(str(row.Name), Elevation=row['Sohlhöhe[m NN]'], MaxDepth=row['Deckelhöhe[m NN]']-row['Sohlhöhe[m NN]']))
    inp[sections.COORDINATES].add_obj(Coordinate(str(row.Name), row['X-Koordinate[m]'], row['Y-Koordinate[m]']))

# ODER
df1 = df1.reset_index(drop=False)
df1['MaxDepth'] = df1['Deckelhöhe[m NN]']-df1['Sohlhöhe[m NN]']

inp[sections.JUNCTIONS] = Junction.create_section(df1[['Label', 'Sohlhöhe[m NN]', 'MaxDepth']].values)
inp[sections.COORDINATES] = Coordinate.create_section(df1[['Label', 'X-Koordinate[m]', 'Y-Koordinate[m]']].values)
