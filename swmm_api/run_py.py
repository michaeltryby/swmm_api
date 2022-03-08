import os
from datetime import timedelta
from math import floor

from swmm.toolkit import solver
from pyswmm import Simulation
from tqdm.auto import tqdm

from swmm_api import SwmmReport
from swmm_api.run import get_result_filenames, SWMMRunError


def run(fn_inp):
    try:
        solver.swmm_run(fn_inp, *get_result_filenames(fn_inp))
        print()
    except Exception as e:
        fn_rpt, fn_out = get_result_filenames(fn_inp)
        message = e.args[0] + '\n' + fn_inp
        if os.path.isfile(fn_rpt):
            message += SwmmReport(fn_rpt).get_errors()

            with open(fn_rpt, 'r') as f:
                rpt_content = f.read()
            if 'ERROR' in rpt_content.upper():
                message += rpt_content
        else:
            message += 'NO Report file created!!!'
        raise SWMMRunError(message)


def run_progress(fn_inp, n_total=100):
    with Simulation(fn_inp) as sim:
        total_time_seconds = (sim.end_time - sim.start_time) / timedelta(seconds=1)
        sim.step_advance(floor(total_time_seconds / n_total))
        progress = tqdm(total=n_total, desc=f'swmm5 {fn_inp}')
        for _ in sim:
            progress.update(1)
            progress.postfix = f'{sim.current_time}'
        progress.update(progress.total - progress.n)
        progress.postfix = f'{sim.current_time}'
        progress.close()


def get_swmm_version():
    return '.'.join(solver.swmm_version_info())
