__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

from os import path
import os
from sys import platform as _platform
import subprocess
from warnings import warn


class NoReportFileError(UserWarning):
    pass


class SWMMRunError(UserWarning):
    pass


def swmm5_run(inp, rpt_dir=None, out_dir=None, init_print=False):
    """
    run a EPA-SWMM input file
    default working directory is input-file directory

    Args:
        inp (str): path to input file
        rpt_dir (str): directory in which the report-file is written.
        out_dir (str): directory in which the output-file is written.
        init_print (bool): if the default commandline output should be printed
    """
    # -----------------------
    base_filename = path.basename(inp).replace('.inp', '')
    inp_dir = path.dirname(inp)

    # -----------------------
    if rpt_dir is None:
        rpt_dir = inp_dir

    rpt = path.join(rpt_dir, base_filename + '.rpt')

    # -----------------------
    if out_dir is None:
        out_dir = inp_dir

    out = path.join(out_dir, base_filename + '.out')

    # -----------------------
    # UNIX
    cl_script = 'swmm5'

    # WINDOWS
    if _platform == "win32":
        script_path = path.join('C:\\', 'Program Files (x86)', 'EPA SWMM 5.1.013', 'swmm5.exe')
        cl_script = f'"{script_path}"'

    cmd = '{} "{}" "{}" "{}"'.format(cl_script, inp, rpt, out)

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
            raise SWMMRunError(rpt_content)

    # -------------------------
    # check if report file is created
    if not path.isfile(rpt):
        raise NoReportFileError('"{}"" was not created'.format(rpt))
