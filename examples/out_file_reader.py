from swmm_api import read_out_file, swmm5_run

## Example for OUT File Reader

# swmm5_run('epaswmm5_apps_manual/Example6-Final.inp')

out = read_out_file('epaswmm5_apps_manual/Example6-Final.out')

out.variables

out.labels

out.number_columns

type(out.to_numpy())

# get all data as pandas.DataFrame
out.to_frame()

# get a specific part of the out data as pandas.Series
out.get_part('node', 'J1', 'Hydraulic_head').to_frame()

# to get all data of a node, just remove the variable part
out.get_part('node', 'J1')
