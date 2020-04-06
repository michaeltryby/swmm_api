# swmm_api

## Install the package:
```bash
pip install swmm-api
```

## Read the INP-File
```python
from swmm_api.input_file.helpers.sections import TIMESERIES
from swmm_api.input_file import read_inp_file, write_inp_file
from swmm_api.input_file.inp_sections_generic import TimeseriesSection
inp = read_inp_file('inputfile.inp', convert_sections=[TIMESERIES])

# convert_sections limits the convertions during the reading of the file to the following section
# remove "convert_sections" to convert all sections 
# converting sections helps manipulating the inp file
# unconverted sections will be loaded as the raw string

sec_timeseries = inp[TIMESERIES]  # type: TimeseriesSection
timeseries_dict = sec_timeseries.to_pandas  # type: Dict[str, pandas.Series]
ts = timeseries_dict['regenseries']
```

## Write the manipulated INP-File
```python
write_inp_file(inp, 'new_inputfile.inp')
```
ein neues Inp-File erstellen.

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


MORE INFORMATIONS COMMING SOON
