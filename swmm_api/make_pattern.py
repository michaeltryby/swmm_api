from matplotlib import use as mpl_use
from numpy import NaN

from sww.libs.timeseries.plots.axes import weekly_x_axes

mpl_use('TkAgg')

from mp.helpers import my_output_path
from sww.apps.cst_monitoring.data_processing import get_cst_client
from sww.apps.wet_weather_analysis import AnalyseData
import pandas as pd

temp_file = True
file_path = my_output_path()


def daily_pattern(series):
    ts = series.copy()
    q = ts.resample('H').mean()
    data7 = AnalyseData(q, kind=0, limit=3, day_kind_detail=8, temp_file=temp_file, est_best_shift_time=False,
                        file_path=file_path)
    data7.set_number_day_labels()
    data7_mean = data7.agg_dry_mean(smooth=None)
    del data7_mean['8 Holiday']
    data7_mean['0 Sunday'] = data7_mean['7 Sunday']
    del data7_mean['7 Sunday']
    data7_mean = data7_mean.sort_index(axis=1)
    mean = data7_mean.mean().mean()
    daily_ = data7_mean.mean() / mean
    daily = daily_.round(3).agg(list)
    return {'{}_Daily'.format(ts.name): {'Type': 'DAILY',
                                         'Pattern': daily}}


def hourly_pattern(series):
    ts = series.copy()
    q = ts.resample('H').mean()
    data3 = AnalyseData(q, kind=0, limit=3, day_kind_detail=3, temp_file=temp_file, est_best_shift_time=False,
                        file_path=file_path)
    data3_mean = data3.agg_dry_mean(smooth=None)
    del data3_mean['Holiday']
    hourly_ = data3_mean / data3_mean.mean()
    hourly = hourly_.round(3).T.agg(list, axis=1)
    return {'{}_Hourly'.format(ts.name): {'Type': 'HOURLY',
                                          'Pattern': hourly['Workday']},
            '{}_Weekend'.format(ts.name): {'Type': 'WEEKEND',
                                           'Pattern': hourly['Weekend']}}


def monthly_pattern(series):
    ts = series.copy()
    q = ts.resample('H').mean()
    data7 = AnalyseData(q, kind=0, limit=3, day_kind_detail=8, temp_file=temp_file, est_best_shift_time=False,
                        file_path=file_path)

    crit = data7.get_criterion_level()
    # crit[crit > 150] = NaN

    # month = data7.get_criterion().resample('M').mean()
    month = crit.resample('M').median() / 100 + 1

    df = pd.DataFrame()
    df['val'] = month
    df['year'] = month.index.year
    df['month'] = month.index.strftime('%m %B')
    # df['month'] = month.index.strftime('%m-%d')

    piv = pd.pivot(index='month', columns='year', values='val', data=df)

    piv2 = pd.DataFrame()
    piv2['median'] = piv.median(axis=1)
    # piv2['mean'] = piv.mean(axis=1)

    if 1:
        ax = piv.plot()
        ax = piv2.plot(ax=ax, lw=5)
        fig = ax.get_figure()
        fig.set_size_inches(h=5, w=8)
        fig.tight_layout()
        fig.savefig(file_path + 'Jahrestrend.png')

    monthly = piv2['median'].round(3).agg(list)
    return {'{}_Monthly'.format(ts.name): {'Type': 'MONTHLY',
                                           'Pattern': monthly}}


def add_pattern(series, set_back=pd.Timedelta(minutes=0)):
    res = {}
    ts = series.copy()
    ts.index = ts.index - set_back
    res.update(hourly_pattern(ts))
    res.update(daily_pattern(ts))
    control_pattern(ts, res)

    res.update(monthly_pattern(ts))
    return pd.DataFrame.from_dict(res).T[['Type', 'Pattern']].rename_axis('Name', axis='columns')


def control_pattern(series, res):
    ts = series.copy()
    q = ts.resample('H').mean()
    data7 = AnalyseData(q, kind=0, limit=3, day_kind_detail=8, temp_file=temp_file, est_best_shift_time=False,
                        file_path=file_path)
    data7.set_number_day_labels()
    data7_mean = data7.agg_dry_mean(smooth=None).copy()
    del data7_mean['8 Holiday']
    data7_mean['0 Sunday'] = data7_mean['7 Sunday']
    del data7_mean['7 Sunday']
    data7_mean = data7_mean.sort_index(axis=1)
    meas = data7_mean.stack(0).sort_index(level=1)

    # -----------------------------
    import numpy as np
    # m = 40.7  # L/s
    h = pd.Series(
        res['{}_Weekend'.format(ts.name)]['Pattern'] + res['{}_Hourly'.format(ts.name)]['Pattern'] * 5 +
        res['{}_Weekend'.format(ts.name)]['Pattern'], name='h')
    d = pd.Series(np.repeat(res['{}_Daily'.format(ts.name)]['Pattern'], 24), name='d')
    # df = pd.DataFrame()
    # df = df.join(d, how='outer').join(h, how='outer')
    # df['v'] = m
    # df.index = pd.timedelta_range(start='00:00:00', freq='H', periods=24 * 7)  # .astype(str)
    # meas.index = df.index
    # df['q'] = df.prod(axis=1)

    pattern = pd.Series(index=pd.timedelta_range(start='00:00:00', freq='H', periods=24 * 7),
                        data=(h*d).values,
                        name='Pattern')

    # PLOT

    # -----------------------------
    from sww.apps.cst_monitoring.data_analysis.plots.figures import weekly_density_plot

    fig, ax = weekly_density_plot(data7)
    # -----------------------------
    ax = pattern.plot(ax=ax, legend=True, secondary_y=True, color='green', lw=2)
    ax = weekly_x_axes(ax)

    ax.set_ylim(0, ax.left_ax.get_ylim()[1] / meas.mean())

    # ax = meas.rename('MEAN').plot(ax=ax, legend=True)
    # fig = ax.get_figure()
    fig.set_size_inches(h=8, w=13)
    fig.tight_layout()
    import matplotlib.pyplot as plt
    # plt.show()
    fig.savefig(file_path + 'Wochentrend.png')
    # fig.show()
    plt.close(fig)


if __name__ == '__main__':
    CLIENT = get_cst_client()
    q = CLIENT.read('graz-wwtp-scada', fields='Q_grit_sum', start=pd.to_datetime('2014'),
                    end=pd.to_datetime('2018'),
                    timezone='Etc/GMT-1')['Q_grit_sum'].rename('Q')

    # from tempest.definitions import MISCHWASSER
    # from tempest.stats import Stats
    # s = Stats(MISCHWASSER)
    # q = s.q

    res = add_pattern(q)
    pd.set_option('display.max_colwidth', 1000)
    res.to_string(open(file_path + 'pattern.inp', 'w+'))
