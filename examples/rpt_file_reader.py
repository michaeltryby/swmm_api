from swmm_api import read_rpt_file
import pandas as pd

pd.set_option('display.max_columns', 35)
pd.set_option('display.width', 720)
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_colwidth', 150)

if __name__ == '__main__':
    r = read_rpt_file('epaswmm5_apps_manual/Example7-Final.rpt')

    r.raingage_summary
    r.subcatchment_summary
    r.node_summary
    r.link_summary
    r.crosssection_summary
    exit()
    r.flow_classification_summary

    ols = r.outfall_loading_summary['Total_Volume_10^6 ' + r.UNIT.VOL2] * 1000  # m³
    ols = ols.to_dict()
    print()

    r.flow_classification_summary
    r.conduit_surcharge_summary
