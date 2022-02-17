from swmm_api.hotstart import SwmmHotstart
from swmm_api import SwmmInput, SwmmOutput, SwmmReport


def main():
    inp = SwmmInput.read_file('epaswmm5_apps_manual/Example6-Final_AllSections_GUI/Example6-Final_AllSections_GUI.inp')
    out = SwmmOutput('epaswmm5_apps_manual/Example6-Final_AllSections_GUI/Example6-Final_AllSections_GUI.out')
    out.to_frame().to_csv(out.filename + '.csv')
    rpt = SwmmReport('epaswmm5_apps_manual/Example6-Final_AllSections_GUI/Example6-Final_AllSections_GUI.rpt')
    hsf = SwmmHotstart('epaswmm5_apps_manual/Example6-Final_AllSections_GUI/Example6-Final_AllSections_GUI.hsf', inp)
    last_timestamp = out.to_frame().iloc[-1]


if __name__ == '__main__':
    main()
