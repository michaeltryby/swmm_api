API for the Input File
======================


Overall Macro Class for SWMM
****************************

.. currentmodule:: swmm_api.input_file.inp_macros

.. autosummary::
    InpMacros
    section_from_frame
    split_inp_to_files
    combined_subcatchment_infos
    find_node
    find_link
    calc_slope
    delete_node
    combine_conduits
    conduit_iter_over_inp
    junction_to_storage
    junction_to_outfall
    remove_empty_sections
    reduce_curves
    reduce_raingages
    filter_nodes
    filter_links
    filter_subcatchments

.. autoclass:: swmm_api.input_file.inp_macros.InpMacros
    :members:


.. rubric:: Methods

.. currentmodule:: swmm_api.input_file.inp_macros.InpMacros

.. autosummary::
    set_name
    report_filename
    out_filename
    parquet_filename
    read_file
    from_file
    write
    from_pickle
    to_pickle
    execute_swmm
    delete_report_file
    delete_inp_file
    run
    output_data
    get_out_frame
    convert_out
    delete_out_file
    get_result_frame
    reset_section
    check_section
    set_start
    set_start_report
    set_end
    set_threads
    ignore_rainfall
    ignore_snowmelt
    ignore_groundwater
    ignore_quality
    set_intervals
    activate_report
    add_obj_to_report
    add_nodes_to_report
    add_links_to_report
    add_timeseries_file
    reduce_curves
    reduce_raingages
    combined_subcatchment_infos
    find_node
    find_link
    calc_slope
    delete_node
    combine_conduits
    conduit_iter_over_inp
    junction_to_outfall
    junction_to_storage

Input File Manipulations
************************

.. currentmodule:: swmm_api.input_file.inp_reader

.. rubric:: Input file reader

.. autosummary::
    read_inp_file

.. currentmodule:: swmm_api.input_file.inp_helpers

.. rubric:: Helpers for the Input file manipulation

.. autosummary::
    BaseSectionObject
    InpSectionGeneric
    InpSection
    InpData
    dataframe_to_inp_string
    txt_to_lines

.. automodule:: swmm_api.input_file.inp_reader
    :members:
    :no-undoc-members:

.. automodule:: swmm_api.input_file.inp_helpers
    :members:
    :no-undoc-members:



Write SWMM INP File
************************

.. currentmodule:: swmm_api.input_file.inp_writer

.. autosummary::
    section_to_string
    inp2string
    write_inp_file

.. automodule:: swmm_api.input_file.inp_writer
    :members:
    :no-undoc-members:
