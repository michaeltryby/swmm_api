from mp.helpers.check_time import Timer
from swmm_api.run import swmm5_run, get_result_filenames
from swmm_api.run_py import run_progress, run
from swmm_api import SwmmOutput, SwmmReport, SwmmInput


def main():

    # run_progress(fn_inp_new, n_total=1000)
    fn_inp = '/home/markus/Downloads/test//Example9.inp'
    fn_rpt, fn_out = get_result_filenames(fn_inp)
    inp = SwmmInput.read_file(fn_inp)
    out = SwmmOutput(fn_out)
    rpt = SwmmReport(fn_rpt)
    df = out.to_frame()

    rpt.rainfall_file_summary
    rpt.highest_continuity_errors

    run_progress('/home/markus/Downloads/test//Example9.inp')

    exit()
    swmm5_run('/home/markus/Documents/SWMM_source/cmake-build-debug/Example9.inp', init_print=True,
              swmm_path='/home/markus/Downloads/swmm5')  # 42 s

    exit()

    with Timer('run'):  # 51s
        swmm5_run('/home/markus/Documents/SWMM_source/cmake-build-debug/Example9.inp', init_print=True,
                  swmm_path='swmm5-1-15')
    exit()

    with Timer('run'):  # 47 s  # 41s
        swmm5_run('/home/markus/Documents/SWMM_source/cmake-build-debug/Example9.inp', init_print=True,
                  swmm_path='swmm5-1-13')

    with Timer('run'):  # 27 s
        run('/home/markus/Documents/SWMM_source/cmake-build-debug/Example9.inp')

    # with Timer('run'):  # 29 s
    exit()
    # SWMM 5.1.15 Wine ... 3min 46s


if __name__ == '__main__':
    main()