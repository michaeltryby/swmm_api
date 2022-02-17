from swmm_api import read_rpt_file


def main():
    r = read_rpt_file('epaswmm5_apps_manual/Example7-Final.rpt')
    r.raingage_summary
    r.subcatchment_summary
    r.node_summary
    r.link_summary
    r.crosssection_summary
    r.flow_classification_summary
    r.flow_classification_summary
    r.conduit_surcharge_summary
    ols = r.outfall_loading_summary['Total_Volume_10^6 ' + r.UNIT.VOL2] * 1000  # m³
    ols = ols.to_dict()


if __name__ == '__main__':
    main()
