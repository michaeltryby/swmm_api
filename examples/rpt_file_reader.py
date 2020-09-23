from swmm_api.report_file.report import Report
import pandas as pd

pd.set_option('display.max_columns', 35)
pd.set_option('display.width', 720)
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_colwidth', 150)

if __name__ == '__main__':
    r = Report('epaswmm5_apps_manual/Example7-Final.rpt')
    r.flow_classification_summary

    # r.flow_routing_continuity
    #
    # ols = r.outfall_loading_summary['Total_Volume_10^6 ltr'] * 1000  # m³
    # ols = ols.to_dict()
    # print()
    #
    # r.flow_classification_summary
    # r.conduit_surcharge_summary
