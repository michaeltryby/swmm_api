from os import path
import os
from sys import platform as _platform
import subprocess
from warnings import warn


def swmm5_run(inp, rpt_dir=None, out_dir=None, init_print=False):
    # --- not necessary
    # if _platform == "win32":
    #     pass
    # else:
    #     inp = inp  # .replace('#', '\#').replace(' ', '\ ')

    # -----------------------
    sim_name = path.basename(inp).replace('.inp', '')
    inp_dir = path.dirname(inp)

    # -----------------------
    if rpt_dir is None:
        rpt_dir = inp_dir

    rpt = path.join(rpt_dir, f'{sim_name}.rpt')

    # -----------------------
    if out_dir is None:
        out_dir = inp_dir

    out = path.join(out_dir, f'{sim_name}.out')

    # -----------------------
    cl_script = 'swmm5'

    if _platform == "win32":
        script_path = path.join('C:\\', 'Program Files (x86)', 'EPA SWMM 5.1.013', 'swmm5.exe')
        cl_script = f'"{script_path}"'

    cmd = f'{cl_script} "{inp}" "{rpt}" "{out}"'

    # -----------------------
    if init_print:
        subprocess.run(cmd, shell=True)
    else:
        shell_output = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        error_log = shell_output.stdout.decode("utf-8")
        if 'error' in error_log:
            warn('\n'.join(['#' * 100,
                            'CALL:\n{}\n'.format(shell_output.args),
                            'RETURN = {}\n'.format(shell_output.returncode),
                            'OUT:\n',
                            '-' * 50,
                            '\n{}'.format(error_log),
                            '-' * 50,
                            '#' * 100]))

            # -------------------------
            # print report file content
            with open(rpt, 'r') as f:
                rpt_content = f.read()
            warn(rpt_content)
            exit(-99)

    if not path.isfile(rpt):
        UserWarning(f'"{rpt}"" was not created')
