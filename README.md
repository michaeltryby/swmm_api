# swmm_api

## Installieren das Pakets:
```bash
pip install swmm-api
```

## Einlesen vom INP-File
```python
from swmm_api.input_file.helpers.sections import TIMESERIES
from swmm_api.input_file import read_inp_file, write_inp_file
from swmm_api.input_file.inp_sections_generic import TimeseriesSection
inp = read_inp_file('inputfile.inp', convert_sections=[TIMESERIES])

sec_timeseries = inp[TIMESERIES]  # type: TimeseriesSection
timeseries_dict = sec_timeseries.to_pandas  # type: Dict[str, pandas.Series]
ts = timeseries_dict['regenseries']
```

Falls du das inp-File bearbeiten möchtest, kannst du anschließend mit:
## Schreiben von manipolierten INP-File
```python
write_inp_file(inp, 'new_inputfile.inp')
```
ein neues Inp-File erstellen.

## Ausführen von SWMM
```python
from swmm_api.run import swmm5_run
swmm5_run('new_inputfile.inp')
```

## Lesen vom OUT-File
```python
from swmm_api.output_file import out2frame
df = out2frame('new_inputfile.out')  # type: pandas.DataFrame
```


MORE INFORMATIONS COMMING SOON
