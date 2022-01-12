from swmm_api.input_file.sections import Junction, Storage, Outfall, Coordinate, DryWeatherFlow, Inflow, RainfallDependentInfiltrationInflow, Treatment

# todo: JUST A THOUGHT


class Node(Junction, Storage, Outfall, Coordinate, DryWeatherFlow, Inflow, RainfallDependentInfiltrationInflow, Treatment):
    def __init__(self):
        Junction.__init__(self)
