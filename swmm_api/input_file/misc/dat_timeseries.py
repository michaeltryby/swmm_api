__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

import pandas as pd
from .following_values import remove_following_zeros


def to_swmm_dat(series, fn, drop_zeros=True):
    """
    external files in swmm ie. timeseries

    Args:
        series (pandas.Series): timeseries
        fn (str): path where the file gets written
        drop_zeros (bool): remove all 0 (zero, null) entries in timeseries (SWMM will understand)
    """
    if drop_zeros:
        ts = remove_following_zeros(series).dropna().to_frame()
    else:
        ts = series.dropna().to_frame()

    ts[';date      time'] = ts.index.strftime('%m/%d/%Y %H:%M')
    ts[[';date      time', series.name]].to_string(open(fn + '.dat', 'w'), index=False)


def read_swmm_data(file):
    """
    read text-file of exported timeseries from the EPA-SWMM-GUI

    Args:
        file (str): path to file

    Returns:
        pandas.Series: timeseries
    """
    df = pd.read_fwf(file, skiprows=2, header=1, names=['Date', 'Time', 'Q'])  # , index_col=[0,1])
    ts = pd.Series(index=pd.to_datetime(df['Date'] + ' ' + df['Time']), data=df['Q'].values)
    return ts
