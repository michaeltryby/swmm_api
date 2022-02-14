import os
from shutil import rmtree

from tqdm.auto import tqdm

from swmm_api import read_inp_file, SwmmReport, SwmmOutput
from swmm_api.input_file.sections import Timeseries
# from swmm_api.run import swmm5_run, get_swmm_version
from swmm_api.run import get_result_filenames
from swmm_api.run_py import run_progress, run, get_swmm_version

# t = Timeseries.create_section("""KOSTRA 01-01-2021 00:00 0.0
# KOSTRA 01-01-2021 00:05 1.9999999999999982
# KOSTRA 01-01-2021 00:10 2.8000000000000007""")
# exit()


"""if no error occur pretty much everything works (or more test cases are needed)"""

temp_dir = 'temp'
if not os.path.isdir(temp_dir):
    os.mkdir(temp_dir)

parent_dir = os.path.dirname(__file__)
example_dirs = [os.path.join(parent_dir, 'epaswmm5_apps_manual'),
                os.path.join(parent_dir, 'epaswmm5_apps_manual', 'projects')]

example_files = [os.path.join(folder, fn) for folder in example_dirs for fn in os.listdir(folder) if '.inp' in fn]
example_files = tqdm(example_files, desc='TESTING_ALL_EXAMPLES')

version = get_swmm_version()
print('Version: ', version)


def _convert_all(rpt):
    keys = ['analyse_duration',
            'analyse_end',
            'analyse_start',
            'analysis_options',
            'conduit_surcharge_summary',
            'crosssection_summary',
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
        eval(f'rpt.{key}')


for fn in example_files:
    example_files.set_postfix_str(str(list(example_files.iterable)[example_files.n]))
    # print(fn)
    # fn = '/home/markus/PycharmProjects/swmm_api/examples/epaswmm5_apps_manual/Example6-Final+TimeseriesVariation _MP.inp'

    if version != '5.1.15' and fn.endswith('Example1_smm5-1-15.inp'):
        continue

    # READ
    inp = read_inp_file(fn)

    # MANIPULATE
    inp.force_convert_all()
    inp.REPORT['INPUT'] = True
    inp.REPORT['CONTINUITY'] = True
    inp.REPORT['FLOWSTATS'] = True
    inp.REPORT['CONTROLS'] = True
    inp.REPORT['SUBCATCHMENTS'] = 'ALL'
    inp.REPORT['NODES'] = 'ALL'
    inp.REPORT['LINKS'] = 'ALL'
    inp.copy()

    fn_inp = os.path.join(temp_dir, 'temp.inp')
    fn_rpt, fn_out = get_result_filenames(fn_inp)

    # WRITE
    inp.write_file(fn_inp)

    # RUN
    # swmm5_run(inp_fn, init_print=False)
    run_progress(fn_inp)
    # run(inp_fn)

    # REPORT
    rpt = SwmmReport(fn_rpt)

    _convert_all(rpt)
    # print(rpt.get_warnings())

    # OUTPUT
    out = SwmmOutput(fn_out)
    out.to_numpy()

    os.remove(fn_rpt)
    os.remove(fn_out)

rmtree(temp_dir)
