==================
Report File Reader
==================
.. currentmodule:: swmm_api

Constructor
~~~~~~~~~~~
.. autosummary::
    :toctree: rpt/

    SwmmReport
    read_rpt_file


Errors and Warnings
~~~~~~~~~~~~~~~~~~~
.. autosummary::
    :toctree: rpt/

    SwmmReport.get_warnings
    SwmmReport.get_errors
    SwmmReport.print_errors
    SwmmReport.print_warnings

Simulation Info
~~~~~~~~~~~~~~~
.. autosummary::
    :toctree: rpt/

    SwmmReport.analysis_options
    SwmmReport.analyse_start
    SwmmReport.analyse_end
    SwmmReport.analyse_duration

Helpers
~~~~~~~
.. autosummary::
    :toctree: rpt/

    SwmmReport.get_version_title
    SwmmReport.get_simulation_info
    SwmmReport.note
    SwmmReport.available_parts

Unit
~~~~
.. autosummary::
    :toctree: rpt/

    SwmmReport.flow_unit
    SwmmReport.unit

    :toctree: rpt/

    report_file.helpers.ReportUnitConversion

Continuities
~~~~~~~~~~~~
.. autosummary::
    :toctree: rpt/

    SwmmReport.runoff_quantity_continuity
    SwmmReport.flow_routing_continuity
    SwmmReport.quality_routing_continuity
    SwmmReport.runoff_quality_continuity
    SwmmReport.groundwater_continuity


Numerics
~~~~~~~~
.. autosummary::
    :toctree: rpt/

    SwmmReport.highest_continuity_errors
    SwmmReport.highest_flow_instability_indexes
    SwmmReport.time_step_critical_elements

Summaries
~~~~~~~~~
.. autosummary::
    :toctree: rpt/

    SwmmReport.element_count
    SwmmReport.conduit_surcharge_summary
    SwmmReport.cross_section_summary
    SwmmReport.flow_classification_summary
    SwmmReport.groundwater_summary
    SwmmReport.landuse_summary
    SwmmReport.lid_control_summary
    SwmmReport.lid_performance_summary
    SwmmReport.link_flow_summary
    SwmmReport.link_pollutant_load_summary
    SwmmReport.link_summary
    SwmmReport.node_depth_summary
    SwmmReport.node_flooding_summary
    SwmmReport.node_inflow_summary
    SwmmReport.node_summary
    SwmmReport.node_surcharge_summary
    SwmmReport.outfall_loading_summary
    SwmmReport.pollutant_summary
    SwmmReport.pumping_summary
    SwmmReport.rainfall_file_summary
    SwmmReport.raingage_summary
    SwmmReport.routing_time_step_summary
    SwmmReport.storage_volume_summary
    SwmmReport.subcatchment_runoff_summary
    SwmmReport.subcatchment_summary
    SwmmReport.subcatchment_washoff_summary
    SwmmReport.transect_summary

Controls
~~~~~~~~
.. autosummary::
    :toctree: rpt/

    SwmmReport.control_actions_taken
