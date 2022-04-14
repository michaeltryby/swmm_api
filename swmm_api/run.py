__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

import subprocess
import os
from sys import platform as _platform

from swmm_api import SwmmReport


class SWMMRunError(UserWarning):
    pass


def get_swmm_command_line(swmm_path, inp, rpt, out):
    cmd = (swmm_path, inp, rpt, out)
    return cmd, inp, rpt, out


def infer_swmm_path():
    # UNIX
    swmm_path = 'swmm5'

    # WINDOWS
    if _platform.startswith("win"):
        swmm_path = None
        # script_path = '???/swmm5.exe'
        for program_files in ('Program Files (x86)', 'Program Files'):
            for version in ('5.1.015', '5.1.014', '5.1.013', '5.2.0', '5.2.0 (64-bit)'):
                for fn_exe in ('runswmm.exe', 'swmm5.exe'):
                    script_path = os.path.join('C:\\', program_files, 'EPA SWMM {}'.format(version), fn_exe)
                    if os.path.isfile(script_path):
                        swmm_path = script_path
                        break
            if swmm_path is not None:
                break

    return swmm_path


def get_result_filenames(inp_fn):
    """
    get filenames for the Report and Output files

    Args:
        inp_fn (str): filename of the Input-Files

    Returns:
        tuple(str, str): filenames for the Report- and Output-file
    """
    return inp_fn.replace('.inp', '.rpt'), inp_fn.replace('.inp', '.out')


def delete_swmm_files(fn_inp, including_inp=False):
    """
    Delete the swmm project files.

    Helpful if you run just a temporary test.

    Args:
        fn_inp (str): filename of the inp-file
        including_inp (bool): if the inp-file should also be deleted.
    """
    fn_rpt, fn_out = get_result_filenames(fn_inp)
    for fn in (fn_out, fn_rpt, (fn_inp if including_inp else None)):
        if fn is not None and os.path.isfile(fn):
            os.remove(fn)


def get_swmm_command_line_auto(inp, rpt_dir=None, out_dir=None, create_out=True, swmm_path=None):
    base_filename = os.path.basename(inp).replace('.inp', '')
    inp_dir = os.path.dirname(inp)

    # -----------------------
    if rpt_dir is None:
        rpt_dir = inp_dir

    rpt = os.path.join(rpt_dir, base_filename + '.rpt')

    # -----------------------
    if out_dir is None:
        out_dir = inp_dir

    if create_out:
        out = os.path.join(out_dir, base_filename + '.out')
    else:
        out = ''

    # -----------------------
    if swmm_path is None:
        swmm_path = infer_swmm_path()

    return get_swmm_command_line(swmm_path, inp, rpt, out)


def run_swmm_stdout(command_line, sep='_' * 100):
    print(sep)
    print(command_line)
    subprocess.run(command_line)
    print(sep)


def run_swmm_custom(command_line):
    # shell_output = subprocess.run(command_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    shell_output = subprocess.run(command_line, capture_output=True)
    return shell_output


def check_swmm_errors(fn_rpt, shell_output):
    msgs = {}

    if isinstance(shell_output, str):
        msgs['CALL'] = shell_output

    else:
        stdout = shell_output.stdout.decode()
        # if 'error' in stdout:
        msgs.update({
            'CALL': shell_output.args,
            'RETURN': shell_output.returncode,
            'ERROR': shell_output.stderr.decode(),
            'OUT': stdout,
        })

    if os.path.isfile(fn_rpt):
        rpt = SwmmReport(fn_rpt)
        errors = rpt.get_errors()
        if errors:
            msgs['REPORT'] = rpt._pretty_dict(errors)
    else:
        msgs['REPORT'] = 'NO Report file created!!!'

    if 'REPORT' in msgs:
        sep = '\n' + '_' * 100 + '\n'
        error_msg = sep + sep.join('{}:\n  {}'.format(k, v) for k, v in msgs.items())
        raise SWMMRunError(error_msg)


def swmm5_run(inp, rpt_dir=None, out_dir=None, init_print=False, create_out=True, swmm_path=None):
    """
    run a simulation with an EPA-SWMM input-file
    default working directory is input-file directory

    Args:
        inp (str): path to input file
        rpt_dir (str): directory in which the report-file is written.
        out_dir (str): directory in which the output-file is written.
        init_print (bool): if the default commandline output should be printed
        create_out (bool): if the out-file should be created

    Returns:
        tuple[str, str, str]: INP-, RPT- and OUT-filename
    """
    command_line, inp, rpt, out = get_swmm_command_line_auto(inp, rpt_dir=rpt_dir, out_dir=out_dir,
                                                             create_out=create_out, swmm_path=swmm_path)
    # -------------------------
    if init_print:
        run_swmm_stdout(command_line)
        stdout = ' '.join(command_line)
    else:
        stdout = run_swmm_custom(command_line)

    # -------------------------
    check_swmm_errors(rpt, stdout)

    return rpt, out


def swmm5_run_parallel(inp_fns, processes=4):
    """
    run multiple swmm models in parallel

    Args:
        inp_fns (list): list of SWMM modell filenames (.inp-files)
        processes (int): number of parallel processes
    """
    _run_parallel(inp_fns, swmm5_run, processes=processes)


def _run_parallel(variable, func=swmm5_run, processes=4):
    from tqdm.auto import tqdm
    from functools import partial

    if processes == 1:
        for fn_inp in tqdm(variable):
            func(fn_inp)

    else:
        from multiprocessing.dummy import Pool

        pool = Pool(processes)
        for _ in tqdm(pool.imap(partial(func), variable), total=len(variable)):
            pass


def get_swmm_version():
    swmm_path = infer_swmm_path()
    shell_output = subprocess.run([swmm_path, '--version'], capture_output=True)
    return shell_output.stdout.decode().strip()
