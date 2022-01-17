class OBJECTS:
    """different types of objects in .out-file"""
    SUBCATCHMENT = "subcatchment"
    NODE = "node"
    LINK = "link"
    POLLUTANT = "pollutant"
    SYSTEM = "system"

    LIST_ = [SUBCATCHMENT, NODE, LINK, POLLUTANT, SYSTEM]


# from swmmtoolbox | swmm source | swmm gui | swmm manual
# https://support.chiwater.com/77882/swmm5-output-file
class VARIABLES:
    """different variables of the objects in the .out-file"""
    class SUBCATCHMENT:
        """variables for sub-catchments"""
        RAINFALL = "rainfall"  # rainfall intensity | Rainfall rate [mm/hr] | Precipitation
        SNOW_DEPTH = "snow_depth"  # SNOWDEPTH | snow depth [mm]
        EVAPORATION = "evaporation"  # EVAP | evap loss [mm/day] | Evaporation
        INFILTRATION = "infiltration"  # INFIL | infil loss [mm/h] | Infiltration
        RUNOFF = "runoff"  # RUNOFF | runoff flow rate
        GW_OUTFLOW = "groundwater_outflow"  # GW_FLOW | groundwater flow rate to node | Groundwater flow into the drainage network
        GW_ELEVATION = "groundwater_elevation"  # GW_ELEV | elevation of saturated gw table [m]
        SOIL_MOISTURE = "soil_moisture"  # SOIL_MOIST | Soil moisture in the unsaturated groundwater zone [fraction]
        # Concentration (mass/volume) Washoff concentration of each pollutant. | TSS

        LIST_ = [RAINFALL, SNOW_DEPTH, EVAPORATION, INFILTRATION, RUNOFF, GW_OUTFLOW, GW_ELEVATION, SOIL_MOISTURE]

    class NODE:
        """variables for nodes"""
        DEPTH = 'depth'  # DEPTH | water depth above invert | Water depth above the node invert elevation [m]
        HEAD = 'head'  # HEAD | hydraulic head | Absolute elevation per vertical datum [m]
        VOLUME = 'volume'  # VOLUME | volume stored & ponded | Stored water volume including ponded water [m³]
        LATERAL_INFLOW = 'lateral_inflow'  # LATFLOW | lateral inflow rate | Runoff + all other external (DW+GW+I&I+User) inflows
        TOTAL_INFLOW = 'total_inflow'  # INFLOW | total inflow rate | Lateral inflow + upstream inflows
        FLOODING = 'flooding'  # OVERFLOW | overflow rate | Flooding | Surface flooding; excess overflow when the node is at full depth
        # CONCENTRATION [mass/volume] Concentration of each pollutant after any treatment. | TSS

        LIST_ = [DEPTH, HEAD, VOLUME, LATERAL_INFLOW, TOTAL_INFLOW, FLOODING]

    class LINK:
        """variables for links"""
        FLOW = 'flow'  # FLOW | flow rate
        DEPTH = 'depth'  # DEPTH | flow depth | Average water depth [m]
        VELOCITY = 'velocity'  # VELOCITY | flow velocity
        VOLUME = 'volume'  # VOLUME | link volume |Volume of water in the conduit; this is based on the midpoint depth and midpoint cross sectional area [m³]
        CAPACITY = 'capacity'  # CAPACITY | ratio of area to full area |Fraction of full area filled by flow for conduits; control setting for pumps and regulators.
        # Concentration (mass/volume) Concentration of each pollutant. | TSS

        LIST_ = [FLOW, DEPTH, VELOCITY, VOLUME, CAPACITY]

    class SYSTEM:
        """system-wide variables"""
        # somewhere are Losses by Exfiltration in STORAGES ??

        AIR_TEMPERATURE = 'air_temperature'  # TEMPERATURE | air temperature [°C]
        RAINFALL = 'rainfall'  # RAINFALL | rainfall intensity | Total rainfall [mm/hr] | Precipitation
        SNOW_DEPTH = 'snow_depth'  # SNOWDEPTH | snow depth | Total snow depth [mm]
        INFILTRATION = 'infiltration'  # INFIL | infil | Average system losses [mm/hr] | Infiltration # sum in infiltration of all sub-catchments (weighted by the sc-area)
        RUNOFF = 'runoff'  # RUNOFF | runoff flow | Total runoff flow
        DW_INFLOW = 'dry_weather_inflow'  # DWFLOW | dry weather inflow | Total dry weather inflow | DW Inflow
        GW_INFLOW = 'groundwater_inflow'  # GWFLOW | ground water inflow | Total groundwater inflow | GW Inflow
        RDII_INFLOW = 'RDII_inflow'  # IIFLOW | RDII inflow | Total rainfall derived infiltration and inflow (RDII). | I&I Inflow
        DIRECT_INFLOW = 'direct_inflow'  # EXFLOW | external inflow | Total direct inflow | Direct Inflow # inflow directly defined in section [INFLOWS] and assigned to node
        LATERAL_INFLOW = 'lateral_inflow'  # INFLOW | total lateral inflow | total external inflow | Total Inflow # INFLOW = RUNOFF + DWFLOW + GWFLOW + IIFLOW + EXFLOW
        FLOODING = 'flooding'  # FLOODING | flooding outflow | Total external flooding
        OUTFLOW = 'outflow'  # OUTFLOW | outfall outflow | Total outflow from outfalls
        VOLUME = 'volume'  # STORAGE | storage volume | Total nodal storage volume in the system [m³]
        EVAPORATION = 'evaporation'  # EVAP | evaporation | Actual evaporation [mm/day]
        PET = 'PET'  # PET | potential ET | Potential evaporation [mm/day]

        LIST_ = [AIR_TEMPERATURE, RAINFALL, SNOW_DEPTH, INFILTRATION, RUNOFF, DW_INFLOW,
                 GW_INFLOW, RDII_INFLOW, DIRECT_INFLOW, LATERAL_INFLOW, FLOODING,
                 OUTFLOW, VOLUME, EVAPORATION, PET]
