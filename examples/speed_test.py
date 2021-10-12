from mp.helpers.check_time import Timer
from swmm_api.run import swmm5_run, get_result_filenames, _run_parallel
from swmm_api.run_py import run_progress, run
from swmm_api import SwmmOutput, SwmmReport, SwmmInput
import os


pth_parent = '/home/markus/Downloads/test/'
pth_parent = r'C:\Users\mp\PycharmProjects\swmm_api\examples\epaswmm5_apps_manual'


def main():

    # run_progress(fn_inp_new, n_total=1000)
    # fn_inp = '/home/markus/Downloads/test//Example9.inp'
    # fn_rpt, fn_out = get_result_filenames(fn_inp)
    # inp = SwmmInput.read_file(fn_inp)
    # out = SwmmOutput(fn_out)
    # rpt = SwmmReport(fn_rpt)
    # df = out.to_frame()

    swmm5_run(os.path.join(pth_parent, 'Example9.inp'), init_print=True)  # 42 s
    run_progress(os.path.join(pth_parent, 'Example9.inp'))
    exit()

    variable = [os.path.join(pth_parent, 'Example9.inp'),
                os.path.join(pth_parent, 'Example9a.inp'),
                os.path.join(pth_parent, 'Example9b.inp'),
                os.path.join(pth_parent, 'Example9c.inp')]
    _run_parallel(variable, func=run_progress, processes=1)
    exit()

    run_progress('/home/markus/Documents/SWMM_source/cmake-build-debug/Example9.inp')
    exit()

    with Timer('run'):  # 27 s  | 30s
        run('/home/markus/Documents/SWMM_source/cmake-build-debug/Example9.inp')


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

    # with Timer('run'):  # 29 s
    exit()
    # SWMM 5.1.15 Wine ... 3min 46s


if __name__ == '__main__':
    main()
