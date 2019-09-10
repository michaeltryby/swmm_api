import pandas as pd
from sww.libs.timeseries.stats import remove_following_duplicates, remove_following_zeros


def to_swmm_dat(series, fn, drop_duplicates=True):
    """external files in swmm ie. timeseries"""
    if drop_duplicates:
        ts = remove_following_duplicates(series).dropna().to_frame()
    else:
        ts = series.dropna().to_frame()

    ts[';date      time'] = ts.index.strftime('%m/%d/%Y %H:%M')
    ts[[';date      time', series.name]].to_string(open(fn + '.dat', 'w'), index=False)


def read_swmm_data(file):
    """file if you export a timeseries-result in swmm to a text file"""
    df = pd.read_fwf(file, skiprows=2, header=1, names=['Date', 'Time', 'Q'])  # , index_col=[0,1])
    ts = pd.Series(index=pd.to_datetime(df['Date'] + ' ' + df['Time']), data=df['Q'].values)
    return ts
