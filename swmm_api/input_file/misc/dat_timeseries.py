__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

import pandas as pd
from .following_values import remove_following_zeros


def write_swmm_timeseries_data(series, filename, drop_zeros=True):
    """
    external files in swmm ie. timeseries. (often with the `.dat`-extension)

    Args:
        series (pandas.Series): time-series-data
        filename (str): path and filename for the new file
        drop_zeros (bool): remove all 0 (zero, null) entries in timeseries (SWMM will understand for precipitation)
    """
    if drop_zeros:
        ts = remove_following_zeros(series).dropna()
    else:
        ts = series.dropna()

    if not filename.endswith('.dat'):
        filename += '.dat'

    with open(filename, 'w') as file:
        file.write(';;EPA SWMM Time Series Data\n')
        ts.index.name = ';date      time'
        ts.to_csv(file, sep='\t', index=True, header=True, date_format='%m/%d/%Y %H:%M', line_terminator='\n')


def read_swmm_timeseries_data(filename):
    """
    read text-file of exported timeseries from the EPA-SWMM-GUI

    Args:
        filename (str): path and filename of the file to be read

    Returns:
        pandas.Series: time-series-data
    """
    sep = r'\s+'  # space or tab
    df = pd.read_csv(filename, comment=';', header=None, sep=sep, names=['date', 'time', 'values'])
    df.index = pd.to_datetime(df.pop('date') + ' ' + df.pop('time'))
    return df['values'].copy()


def peek_swmm_timeseries_data(filename, indices):
    """
    take a peek in a text-file of exported timeseries from the EPA-SWMM-GUI

    Args:
        filename (str): path and filename of the file to be read
        indices (list[int]): list of indices to return

    Returns:
        pandas.Series: time-series-data
    """
    df = pd.read_csv(filename, comment=';', header=None, sep=r'\s+', names=['date', 'time', 'values'])
    try:
        df = df.iloc[indices]
    except:
        pass
    df.index = pd.to_datetime(df.pop('date') + ' ' + df.pop('time'))
    return df['values'].copy()


def read_swmm_rainfall_file(filename):
    """
    read text-file of exported timeseries from the EPA-SWMM-GUI

    SWMM 5.1 User Manual | 11.3 Rainfall Files | S. 165

    Args:
        filename (str): path and filename of the file to be read

    Returns:
        pandas.Series: time-series-data with a mulitindex (Datetime, Station)
    """
    sep = r'\s+'  # space or tab
    df = pd.read_csv(filename, comment=';', header=None, sep=sep,
                     names=['station', 'year', 'month', 'day', 'hour', 'minute', 'values'],
                     )
    df.index = pd.to_datetime(df[['year', 'month', 'day', 'hour', 'minute']])
    return df.set_index('station', append=True)['values'].copy()


def read_swmm_tsf(filename, sep='\t'):
    """
    read a swmm .tsf-file (TimeSeriesFile).
    An ASCII-file used in PCSWMM to compare simulations results with measured data, or to export simulation results.

    Args:
        filename (str): path and filename of the file to be read
        sep (str): separator of the columns in the file

    Returns:
        pandas.DataFrame: time-series-data-frame
    """
    df = pd.read_csv(filename, comment=';', header=[0, 1, 2], sep=sep, index_col=0)
    # 5/24/2019 12:00:00 AM
    df.index = pd.to_datetime(df.index, format='%m/%d/%Y %I:%M:%S %p')
    df.columns = ['|'.join(c) for c in df.columns]
    return df
