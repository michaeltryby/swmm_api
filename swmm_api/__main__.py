from os import path
from pandas import to_datetime, Timedelta
from datetime import datetime
# from pandas.errors import UnsortedIndexError

from swmm_api import read_inp_file, write_inp_file

"""
2009-10-11 00:30:00
2011-08-02 13:25:00
"""

if __name__ == '__main__':
    # from mp.helpers import OUTPUT_PATH

    # out = SwmmOutHandler('test.out')
    # print(out.to_frame())
    # exit()

    if 0:
        check()
        q = pd.read_parquet(path.join(DATA_PATH, 'calore', 'r05_2009-11-01.parquet'), columns='Q')['Q']
        check('READ')
        to_swmm_dat(q, path.join(OUTPUT_PATH, 'r05', 'q_in'), name='Q_inflow')
        check('WROTE')
        exit()

    if 1:
        pth = path.join(OUTPUT_PATH, 'r05', 'inp')
        fn = '20180418_Graz_R05_20.inp'

        nw = read_inp_file(filename=path.join(pth, fn))
        dt = datetime.combine(nw['OPTIONS'].loc['START_DATE'], nw['OPTIONS'].loc['START_TIME'])
        print(dt)
        dt = datetime.combine(nw['OPTIONS'].loc['END_DATE'], nw['OPTIONS'].loc['END_TIME'])
        print(dt)

        exit()
        print()
        if 1:
            start = to_datetime('2011-08-01 00:00:00')
            end = start + Timedelta(days=1)
            nw['OPTIONS'].loc['START_DATE'] = start.date()
            nw['OPTIONS'].loc['START_TIME'] = start.time()

            nw['OPTIONS'].loc['REPORT_START_DATE'] = start.date()
            nw['OPTIONS'].loc['REPORT_START_TIME'] = start.time()

            nw['OPTIONS'].loc['END_DATE'] = end.date()
            nw['OPTIONS'].loc['END_TIME'] = end.time()

            nw['OPTIONS'].loc['IGNORE_RAINFALL'] = True
            nw['OPTIONS'].loc['IGNORE_SNOWMELT'] = True
            nw['OPTIONS'].loc['IGNORE_GROUNDWATER'] = True
            nw['OPTIONS'].loc['IGNORE_QUALITY'] = True
            nw['OPTIONS'].loc['THREADS'] = 4

            nw['REPORTS'].loc['CONTINUITY'] = False
            nw['REPORTS'].loc['FLOWSTATS'] = False
            nw['REPORTS'].loc['CONTINUITY'] = False

            nw['INFLOWS'].loc[6500058, 'Baseline'] = 10

        if 1:
            write_inp_file(nw, 'test.inp')

    if 0:
        swmm5_run('test.inp')
