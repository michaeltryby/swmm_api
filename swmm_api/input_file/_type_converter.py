import datetime
from datetime import date, time, timedelta
from pandas import isna, to_datetime, Timedelta, Timestamp, to_timedelta
from pandas.tseries.frequencies import to_offset
from numpy import ndarray, NaN


def to_bool(x):
    if isinstance(x, bool):
        return x
    else:
        if x == 'YES':
            return True
        elif x == 'NO':
            return False
        else:
            raise NotImplemented('x not a bool: {}'.format(x))


def infer_type(x):
    """
    infer generic type of inp-file-string

    Args:
        x (str | list[str]):

    Returns:
        object: object depending on string
    """
    if isinstance(x, (list, ndarray)):
        return [infer_type(i) for i in x]
    elif not isinstance(x, str):
        return x
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


def str_to_datetime(date=None, time=None):
    if date:
        if '-' in date:
            date = date.replace('-', '/')

        month = date.split('/')[0]
        if len(month) <= 2:
            month_format = '%m'
        elif len(month) == 3:
            month_format = '%b'
        else:
            raise NotImplementedError(date)

        if date.count('/') == 2:
            date_format2 = '/%d/%Y'
        else:
            raise NotImplementedError(date)
    else:
        date = ''
        month_format = ''
        date_format2 = ''

    if time:
        if date == '':
            parts = time.split(':')
            if len(parts) == 1:
                return float(parts[0])
            elif len(parts) == 2:
                return float(parts[0]) + float(parts[1])/60
            elif len(parts) == 3:
                return float(parts[0]) + float(parts[1])/60 + float(parts[2])/60/60
        else:
            if time.count(':') == 1:
                time_format = '%H:%M'
            elif time.count(':') == 2:
                time_format = '%H:%M:%S'
            elif time.count(':') == 0:
                hours = float(time)
                h = int(hours)
                minutes = (hours - h)*60
                m = int(minutes)
                s = int((minutes - m)*60)
                time = f'{h:02d}:{m:02d}:{s:02d}'
                time_format = '%H:%M:%S'
            else:
                raise NotImplementedError(time)

    else:
        time = ''
        time_format = ''

    return to_datetime(date + ' ' + time,
                       format=month_format + date_format2 + ' ' + time_format)


def datetime_to_str(dt):
    if isinstance(dt, float):
        hours = dt
        h = int(round(hours, 4))
        minutes = (hours - h) * 60
        m = int(round(minutes, 4))
        t = f'{h:02d}:{m:02d}'
        second = (minutes - m) * 60
        s = int(round(second, 4))
        if s:
            t += f':{s:02d}'
        return t
    elif isinstance(dt, str):
        return dt
    elif isinstance(dt, datetime.datetime):
        return dt.strftime(format='%b/%d/%Y %H:%M:%S')



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
        if ' ' in x:
            return f'"{x}"'
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

import numpy as np


def is_equal(x1, x2, precision=3):
    if isinstance(x1, float) and np.isnan(x1) and isinstance(x2, float) and np.isnan(x2):
        return True
    else:
        if isinstance(x1, float):
            x1 = round(x1, precision)
        if isinstance(x2, float):
            x2 = round(x2, precision)
        return x1 == x2


def convert_string(x) -> str:
    if isna(x):
        return x
    x = str(x)
    if ' ' in x:
        return f'"{x}"'
    else:
        s = x.strip('"')
        if s == '':
            return NaN
        else:
            return s


GIS_FLOAT_FORMAT = '0.03f'
