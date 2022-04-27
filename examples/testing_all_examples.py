import os
import time
from shutil import rmtree

from tqdm.auto import tqdm

import warnings

from swmm_api import read_inp_file, SwmmReport, SwmmOutput
from swmm_api.input_file import SEC
from swmm_api.input_file.helpers import SwmmInputWarning
from swmm_api.input_file.macros import write_geo_package
from swmm_api.input_file.sections import Timeseries
# from swmm_api.run_py import get_swmm_version, run
from swmm_api.run import get_swmm_version, swmm5_run as run
from swmm_api.run import get_result_filenames, SWMMRunError

# t = Timeseries.create_section("""KOSTRA 01-01-2021 00:00 0.0
# KOSTRA 01-01-2021 00:05 1.9999999999999982
# KOSTRA 01-01-2021 00:10 2.8000000000000007""")
# exit()

warnings.filterwarnings('ignore', category=SwmmInputWarning)

"""if no error occur pretty much everything works (or more test cases are needed)"""

temp_dir = 'temp'
if not os.path.isdir(temp_dir):
    os.mkdir(temp_dir)

parent_dir = os.path.dirname(__file__)
example_dirs = [os.path.join(parent_dir, 'epaswmm5_apps_manual'),
                os.path.join(parent_dir, 'epaswmm5_apps_manual', 'projects'),
                os.path.join(parent_dir, 'epaswmm5_apps_manual', 'Samples'),
                os.path.join(parent_dir, 'epaswmm5_apps_manual', 'Example6-Final_AllSections_GUI')]

version = get_swmm_version()
print(f'Version: {version}')
print()

example_files = [os.path.join(folder, fn) for folder in example_dirs for fn in os.listdir(folder) if '.inp' in fn]


def _convert_all(rpt):
    keys = ['analyse_duration',
            'analyse_end',
            'analyse_start',
            'analysis_options',
            'conduit_surcharge_summary',
            'cross_section_summary',
            'flow_classification_summary',
            'flow_routing_continuity',
            'flow_unit',
            'get_errors',
            'get_simulation_info',
            'get_warnings',
            'highest_continuity_errors',
            'highest_flow_instability_indexes',
            'link_flow_summary',
            'link_summary',
            'node_depth_summary',
            'node_flooding_summary',
            'node_inflow_summary',
            'node_summary',
            'node_surcharge_summary',
            'outfall_loading_summary',
            'rainfall_file_summary',
            'raingage_summary',
            'runoff_quantity_continuity',
            'storage_volume_summary',
            'subcatchment_runoff_summary',
            'subcatchment_summary',
            'time_step_critical_elements',
            'control_actions_taken',
            'element_count',
            'groundwater_continuity',
            'groundwater_summary',
            'landuse_summary',
            'lid_control_summary',
            'lid_performance_summary',
            'link_pollutant_load_summary',
            'note',
            'pollutant_summary',
            'pumping_summary',
            'quality_routing_continuity',
            'routing_time_step_summary',
            'runoff_quality_continuity',
            'subcatchment_washoff_summary',
            'transect_summary'
            ]

    for key in keys:
        rpt.__getattribute__(key)
        # eval(f'rpt.{key}')


failed = []

with tqdm(example_files, desc='TESTING_ALL_EXAMPLES') as example_files:
    for fn in example_files:
        example_files.set_postfix_str(str(list(example_files.iterable)[example_files.n]))
        # print(fn)
        # fn = '/home/markus/PycharmProjects/swmm_api/examples/epaswmm5_apps_manual/Example6-Final+TimeseriesVariation _MP.inp'

        if version != '5.1.15' and fn.endswith('Example1_smm5-1-15.inp'):
            continue

        if '5.2' not in version and 'Samples' in fn:
            continue

        # READ
        inp = read_inp_file(fn)

        # MANIPULATE

        # convert all
        inp.force_convert_all()

        # test copy
        inp.copy()

        if SEC.RAINGAGES in inp:
            if 'RainGage' in inp.RAINGAGES:
                # if isinstance(inp.RAINGAGES['RainGage'].Filename, str):
                #     print()
                if inp.RAINGAGES['RainGage'].Filename == 'Record.dat':
                    inp.RAINGAGES['RainGage'].Filename = os.path.join(os.path.dirname(__file__), 'epaswmm5_apps_manual', inp.RAINGAGES['RainGage'].Filename)
                    pass # C:\Users\mp\PycharmProjects\swmm_api\examples\epaswmm5_apps_manual\


        fn_inp = os.path.join(temp_dir, 'temp.inp')
        fn_rpt, fn_out = get_result_filenames(fn_inp)

        # WRITE
        inp.REPORT['INPUT'] = True
        inp.REPORT['CONTINUITY'] = True
        inp.REPORT['FLOWSTATS'] = True
        inp.REPORT['CONTROLS'] = True
        inp.REPORT['SUBCATCHMENTS'] = 'ALL'
        inp.REPORT['NODES'] = 'ALL'
        inp.REPORT['LINKS'] = 'ALL'
        inp.write_file(fn_inp)

        # RUN
        # swmm5_run(inp_fn, init_print=False)
        # run_progress(fn_inp)
        try:
            run(fn_inp)
        except SWMMRunError as e:
            failed.append(f'{fn}{e}')
            continue
        except UnicodeDecodeError as e:
            failed.append(f'{fn} ({e})')
            continue

        # REPORT
        rpt = SwmmReport(fn_rpt)
        _convert_all(rpt)
        # print(rpt.get_warnings())
        del rpt

        # OUTPUT
        out = SwmmOutput(fn_out)
        out.to_numpy()
        del out

        if os.path.isfile(fn_rpt):
            os.remove(fn_rpt)
        if os.path.isfile(fn_rpt):
            os.remove(fn_out)

rmtree(temp_dir)

print('FAILED:', *failed, sep='\n  - ')
