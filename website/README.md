© [Institute of Urban Water Management and Landscape Water Engineering](https://www.sww.tugraz.at), [Graz University of Technology](https://www.tugraz.at/home/) and [Markus Pichler](mailto:markus.pichler@tugraz.at)

# This is an API for reading, manipulating and running SWMM-Projects

[![PyPI](https://img.shields.io/pypi/v/swmm-api.svg)](https://pypi.python.org/pypi/swmm-api)
[![pipeline status](https://gitlab.com/markuspichler/swmm_api/badges/master/pipeline.svg)](https://gitlab.com/markuspichler/swmm_api/-/commits/master)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![docs](https://img.shields.io/static/v1.svg?label=sphinx&message=documentation&color=blue)](https://markuspichler.gitlab.io/swmm_api)

[![PyPI - Downloads](https://img.shields.io/pypi/dd/swmm-api)](https://pypi.python.org/pypi/swmm-api)
[![PyPI - Downloads](https://img.shields.io/pypi/dw/swmm-api)](https://pypi.python.org/pypi/swmm-api)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/swmm-api)](https://pypi.python.org/pypi/swmm-api)


With this package you can read INP-files, manipulate them and write new ones.
You can run swmm within the python api.
And you can read the OUT-file as a pandas DataFrame for further analysis.

This package is based on the command line SWMM syntax. ([see Appendix D in the SWMM User Manual 5.1](https://www.epa.gov/water-research/storm-water-management-model-swmm-version-51-users-manual))

## Install the package:
```bash
pip install swmm-api
```

## Read, manipulate and write the INP-File

### Read the INP-File

```python
from swmm_api.input_file.section_labels import TIMESERIES
from swmm_api import read_inp_file

inp = read_inp_file('inputfile.inp', convert_sections=[TIMESERIES])  # type: swmm_api.SwmmInput

# convert_sections limits the convertions during the reading of the file to the following section
# remove "convert_sections" to convert all sections 
# converting sections helps manipulating the inp file
# unconverted sections will be loaded as the raw string

sec_timeseries = inp[TIMESERIES]  # type: swmm_api.input_file.helpers.InpSection
ts = inp[TIMESERIES]['regenseries'].frame  # type: pandas.Series
```

### Manipulate the INP-File

```python
from swmm_api import read_inp_file, SwmmInput
from swmm_api.input_file.section_labels import JUNCTIONS

inp = read_inp_file('inputfile.inp')  # type: swmm_api.SwmmInput
# or 
inp = SwmmInput.read_file('inputfile.inp')

inp[JUNCTIONS]['J01'].Elevation = 210
```

### Write the manipulated INP-File
```python
inp.write_file('new_inputfile.inp')
```

see [examples/inp_file_reader.ipynb](https://gitlab.com/markuspichler/swmm_api/-/blob/master/examples/inp_file_reader.ipynb)

see [examples/inp_file_structure.ipynb](https://gitlab.com/markuspichler/swmm_api/-/blob/master/examples/inp_file_structure.ipynb)

see [examples/inp_file_macros.ipynb](https://gitlab.com/markuspichler/swmm_api/-/blob/master/examples/inp_file_macros.ipynb)




## Run SWMM
```python
from swmm_api import swmm5_run
swmm5_run('new_inputfile.inp')
```

## Read the OUT-File
```python
from swmm_api import read_out_file
out = read_out_file('new_inputfile.out')   # type: swmm_api.SwmmOut
df = out.to_frame()  # type: pandas.DataFrame
```
see [examples/out_file_reader.ipynb](https://gitlab.com/markuspichler/swmm_api/-/blob/master/examples/out_file_reader.ipynb)


## Read the RPT-File
```python
from swmm_api import read_rpt_file
rpt = read_rpt_file('new_inputfile.rpt')  # type: swmm_api.SwmmReport
node_flooding_summary = rpt.node_flooding_summary  # type: pandas.DataFrame
```
see [examples/rpt_file_reader.ipynb](https://gitlab.com/markuspichler/swmm_api/-/blob/master/examples/rpt_file_reader.ipynb)

MORE INFORMATIONS COMMING SOON
