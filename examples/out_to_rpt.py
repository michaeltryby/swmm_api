from swmm_api.output_file.out import SwmmOutput
from swmm_api.report_file.rpt import SwmmReport
from swmm_api.input_file import SwmmInput


def out_to_rpt(inp: SwmmInput, out: SwmmOutput, rpt: SwmmReport):
    flow_routing_unit = 'Volume_10^6 ltr'
    runoff_quantity_unit = 'Volume_hectare-m'

    # --------------
    rpt.outfall_loading_summary['Max_Flow_LPS']
    out.get_part('node', ['ARA', 'Mischwasserueberlauf', 'O09', 'O10'], 'Total_inflow').max()
    # --------------

    # --------------
    # report ist unabhängig von report time - beeinflusst nur out file länge
    rpt.outfall_loading_summary['Total_Volume_10^6 ltr']
    # ungleich
    out.get_part('node', ['ARA', 'Mischwasserueberlauf', 'O09', 'O10'], 'Total_inflow').sum() * 5 / 1000000
    # --------------

    # --------------
    rpt.runoff_quantity_continuity['Infiltration Loss'][runoff_quantity_unit]
    (inp.SUBCATCHMENTS.frame['Area'] * rpt.subcatchment_runoff_summary['Total_Infil_mm']).sum() / \
    inp.SUBCATCHMENTS.frame['Area'].sum()

    # --------------
    rpt.subcatchment_runoff_summary['Total_Runoff_10^6 ltr']
    out.get_part('node', ['ARA', 'Mischwasserueberlauf', 'O09', 'O10'], 'Total_inflow').sum() * 5 / 1000000
    # --------------

    # --------------
    # spitzenabflussbeiwert
    (rpt.subcatchment_runoff_summary['Total_Runoff_mm'] / rpt.subcatchment_runoff_summary['Total_Precip_mm']).round(3)
    rpt.subcatchment_runoff_summary['Runoff_Coeff']
