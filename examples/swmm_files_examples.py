from swmm_api.input_file.misc.dat_timeseries import read_swmm_rainfall_file
from io import StringIO

if __name__ == '__main__':
    f = StringIO("""
STA01 2004 6 12 00 00 0.12
STA01 2004 6 12 01 00 0.04
STA01 2004 6 22 16 00 0.07
""")
    df = read_swmm_rainfall_file(f)
    print(df)
