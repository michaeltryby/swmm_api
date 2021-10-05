from mp.helpers.check_time import Timer

def test_swmm():
    from swmm_api.run_py import run_progress, run

    # run_progress(fn_inp_new, n_total=1000)
    run_progress('/home/markus/Documents/SWMM_source/cmake-build-debug/Example9.inp')
    exit()

    from swmm_api.run import swmm5_run
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

