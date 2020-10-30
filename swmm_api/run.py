__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

import subprocess
from os import path
from sys import platform as _platform
from warnings import warn


class NoReportFileError(UserWarning):
    pass


class SWMMRunError(UserWarning):
    pass


def swmm5_run(inp, rpt_dir=None, out_dir=None, init_print=False, create_out=True):
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

    if create_out:
        out = path.join(out_dir, base_filename + '.out')
    else:
        out = ''

    # -----------------------
    # UNIX
    cl_script = 'swmm5'

    # WINDOWS
    if _platform.startswith("win"):
        cl_script = None
        # script_path = '???/swmm5.exe'
        for program_files in ['Program Files (x86)', 'Program Files']:
            for version in ['5.1.015', '5.1.014', '5.1.013']:
                script_path = path.join('C:\\', program_files, 'EPA SWMM {}'.format(version), 'swmm5.exe')
                if path.isfile(script_path):
                    cl_script = '"{}"'.format(script_path)
                    break
            if cl_script is not None:
                break

    cmd = '{} "{}" "{}" "{}"'.format(cl_script, inp, rpt, out)

    # -----------------------
    if init_print:
        sep = '_' * 100
        print(sep)
        print(cmd)
        subprocess.run(cmd, shell=True)
        print(sep)
    else:
        shell_output = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        error_log = shell_output.stdout.decode("utf-8")
        if 'error' in error_log:
            msgs = {
                'CALL': shell_output.args,
                'RETURN': shell_output.returncode,
                'OUT': error_log
            }
            if path.isfile(rpt):
                with open(rpt, 'r') as f:
                    rpt_content = f.read()
                msgs['REPORT'] = rpt_content
            else:
                msgs['REPORT'] = 'NO Report file created!!!'

            sep = '\n' + '_' * 100 + '\n'
            error_msg = sep + sep.join('{}:\n  {}'.format(k, v) for k, v in msgs.items())
            raise SWMMRunError(error_msg)

    # -------------------------
    # check if report file is created
    if not path.isfile(rpt):
        raise NoReportFileError('"{}"" was not created'.format(rpt))

    return inp, rpt, out
