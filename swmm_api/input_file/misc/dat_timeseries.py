__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

import pandas as pd
from .following_values import remove_following_zeros


def write_swmm_timeseries_data(series, fn, drop_zeros=True):
    """
    external files in swmm ie. timeseries

    Args:
        series (pandas.Series): timeseries
        fn (str): path where the file gets written
        drop_zeros (bool): remove all 0 (zero, null) entries in timeseries (SWMM will understand for precipitation)
    """
    if drop_zeros:
        ts = remove_following_zeros(series).dropna()
    else:
        ts = series.dropna()

    if not fn.endswith('.dat'):
        fn += '.dat'

    with open(fn, 'w') as file:
        file.write(';;EPA SWMM Time Series Data\n')
        ts.index.name = ';date      time'
        ts.to_csv(file, sep='\t', index=True, header=True, date_format='%m/%d/%Y %H:%M', line_terminator='\n')


def read_swmm_timeseries_data(file):
    """
    read text-file of exported timeseries from the EPA-SWMM-GUI

    Args:
        file (str): path to file

    Returns:
        pandas.Series: timeseries
    """
    sep = r'\s+'  # space or tab
    df = pd.read_csv(file, comment=';', header=None, sep=sep, names=['date', 'time', 'values'])
    df.index = pd.to_datetime(df.pop('date') + ' ' + df.pop('time'))
    return df['values'].copy()


def peak_swmm_timeseries_data(file, indices):
    """
    take a peak in a text-file of exported timeseries from the EPA-SWMM-GUI

    Args:
        file (str): path to file
        indices (list[int]): list of indices to return

    Returns:
        pandas.Series: timeseries
    """
    df = pd.read_csv(file, comment=';', header=None, sep=r'\s+', names=['date', 'time', 'values'])
    try:
        df = df.iloc[indices]
    except:
        pass
    df.index = pd.to_datetime(df.pop('date') + ' ' + df.pop('time'))
    return df['values'].copy()


def read_swmm_rainfall_file(file):
    """
    read text-file of exported timeseries from the EPA-SWMM-GUI

    SWMM 5.1 User Manual | 11.3 Rainfall Files | S. 165

    Args:
        file (str): path to file

    Returns:
        pandas.Series: timeseries with a mulitindex (Datetime, Station)
    """
    sep = r'\s+'  # space or tab
    df = pd.read_csv(file, comment=';', header=None, sep=sep,
                     names=['station', 'year', 'month', 'day', 'hour', 'minute', 'values'],
                     )
    df.index = pd.to_datetime(df[['year', 'month', 'day', 'hour', 'minute']])
    return df.set_index('station', append=True)['values'].copy()
