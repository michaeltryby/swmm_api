from datetime import date, time, timedelta
from pandas import isna, to_datetime, Timedelta, Timestamp, to_timedelta
from pandas.tseries.frequencies import to_offset


def infer_type(x):
    """
    infer generic type of inp-file-string

    Args:
        x (str | list[str]):

    Returns:
        object: object depending on string
    """
    if isinstance(x, list):
        return [infer_type(i) for i in x]
    elif x == 'YES':
        return True
    elif x == 'NO':
        return False
    elif x == 'NONE':
        return None
    elif x.replace('-', '').isdecimal():
        return int(x)
    elif ('.' in x) and (x.lower().replace('.', '').replace('-', '').replace('e', '').isdecimal()):
        return float(x)
    elif x.count('/') == 2:
        return to_datetime(x, format='%m/%d/%Y').date()
    # elif x.count('/') == 1:
    #     return to_datetime(x, format='%m/%d').date()
    elif (x.count(':') == 2) and (len(x) == 8):
        return to_datetime(x, format='%H:%M:%S').time()
    elif (x.count(':') == 1) and (len(x) == 5):
        return to_datetime(x, format='%H:%M').time()
    else:
        return x


def time2delta(t):
    return Timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)


def delta2time(d):
    return Timestamp(2000, 1, 1, d.components.hours, d.components.minutes, d.components.seconds).time()


def delta2offset(d):
    return to_offset(d)


def offset2delta(o):
    return to_timedelta(o)


def delta2str(d):
    """

    Args:
        d (pandas.Timedelta):

    Returns:
        str: HH:MM:SS
    """
    hours, remainder = divmod(d.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    return '{:02.0f}:{:02.0f}:{:02.0f}'.format(hours, minutes, seconds)


def type2str(x):
    """
    convert any type to a string

    Args:
        x (any):

    Returns:
        str:
    """
    if isinstance(x, str):
        return x
    elif isinstance(x, list):
        return ' '.join([type2str(i) for i in x])
    elif isinstance(x, bool):
        return 'YES' if x else 'NO'
    elif x is None:
        return 'NONE'
    elif isinstance(x, int):
        return str(x)
    elif isinstance(x, float):
        if isna(x):
            return ''
        if x == 0.0:
            return '0'
        return '{:0.7G}'.format(x)  # .rstrip('0').rstrip('.')
    elif isinstance(x, date):
        return x.strftime(format='%m/%d/%Y')
    elif isinstance(x, time):
        return x.strftime(format='%H:%M:%S')
    elif isinstance(x, (Timedelta, timedelta)):
        return delta2str(x)
    else:
        return str(x)
