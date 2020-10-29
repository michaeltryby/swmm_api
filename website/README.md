© [Institute of Urban Water Management and Landscape Water Engineering](https://www.sww.tugraz.at), [Graz University of Technology](https://www.tugraz.at/home/) and [Markus Pichler](mailto:markus.pichler@tugraz.at)

# This is an API for reading, manipulating and running SWMM-Projects

[![PyPI](https://img.shields.io/pypi/v/swmm-api.svg)](https://pypi.python.org/pypi/swmm-api)
[![pipeline status](https://gitlab.com/markuspichler/swmm_api/badges/master/pipeline.svg)](https://gitlab.com/markuspichler/swmm_api/-/commits/master)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![docs](https://img.shields.io/static/v1.svg?label=sphinx&message=documentation&color=blue)](https://markuspichler.gitlab.io/swmm_api)

With this package you can read INP-files, manipulate them and write new ones.
You can run swmm within the python api.
And you can read the OUT-file as a pandas DataFrame for further analysis.


## Install the package:
```bash
pip install swmm-api
```

## Read the INP-File
```python
from swmm_api.input_file.inp_sections.labels import TIMESERIES
from swmm_api.input_file import read_inp_file
from swmm_api.input_file.inp_sections import TimeseriesSection
inp = read_inp_file('inputfile.inp', convert_sections=[TIMESERIES])

# convert_sections limits the convertions during the reading of the file to the following section
# remove "convert_sections" to convert all sections 
# converting sections helps manipulating the inp file
# unconverted sections will be loaded as the raw string

sec_timeseries = inp[TIMESERIES]  # type: TimeseriesSection
timeseries_dict = sec_timeseries.to_pandas  # type: Dict[str, pandas.Series]
ts = timeseries_dict['regenseries']
```
see [examples/inp_file_reader.ipynb](https://gitlab.com/markuspichler/swmm_api/-/blob/master/examples/inp_file_reader.ipynb)

## Write the manipulated INP-File
```python
from swmm_api.input_file import write_inp_file
write_inp_file(inp, 'new_inputfile.inp')
```


## Run SWMM
```python
from swmm_api.run import swmm5_run
swmm5_run('new_inputfile.inp')
```

## Read the OUT-File
```python
from swmm_api.output_file import out2frame
df = out2frame('new_inputfile.out')  # type: pandas.DataFrame
```
see [examples/out_file_reader.ipynb](https://gitlab.com/markuspichler/swmm_api/-/blob/master/examples/out_file_reader.ipynb)


## Read the RPT-File
see [examples/rpt_file_reader.ipynb](https://gitlab.com/markuspichler/swmm_api/-/blob/master/examples/rpt_file_reader.ipynb)

MORE INFORMATIONS COMMING SOON
