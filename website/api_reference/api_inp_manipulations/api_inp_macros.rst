Input File Manipulation - Macros
--------------------------------

Check
~~~~~

.. currentmodule:: swmm_api.input_file.macros.check
.. autosummary::
    :toctree: macros/

    check_for_duplicates
    check_for_nodes
    check_for_subcatchment_outlets

Collection
~~~~~~~~~~

.. currentmodule:: swmm_api.input_file.macros.collection
.. autosummary::
    :toctree: macros/

    links_dict
    nodes_dict
    nodes_subcatchments_dict
    subcatchments_per_node_dict

Compare
~~~~~~~

.. currentmodule:: swmm_api.input_file.macros.compare
.. autosummary::
    :toctree: macros/

    compare_inp_files
    compare_sections
    inp_version_control

Convert
~~~~~~~

.. currentmodule:: swmm_api.input_file.macros.convert
.. autosummary::
    :toctree: macros/

    conduit_to_orifice
    junction_to_outfall
    junction_to_storage

Cross-Section Curve
~~~~~~~~~~~~~~~~~~~

.. currentmodule:: swmm_api.input_file.macros.cross_section_curve
.. autosummary::
    :toctree: macros/

    get_cross_section_maker
    profil_area
    velocity

Curve
~~~~~

.. currentmodule:: swmm_api.input_file.macros.curve
.. autosummary::
    :toctree: macros/

    curve_figure

Edit
~~~~

.. currentmodule:: swmm_api.input_file.macros.edit
.. autosummary::
    :toctree: macros/

    combine_conduits
    combine_conduits_keep_slope
    combine_vertices
    delete_link
    delete_node
    delete_subcatchment
    dissolve_conduit
    flip_link_direction
    move_flows
    remove_quality_model
    rename_link
    rename_node
    rename_subcatchment
    rename_timeseries
    split_conduit

Filter
~~~~~~

.. currentmodule:: swmm_api.input_file.macros.filter
.. autosummary::
    :toctree: macros/

    create_sub_inp
    filter_links
    filter_links_within_nodes
    filter_nodes
    filter_subcatchments
    filter_tags

Geo
~~~

.. currentmodule:: swmm_api.input_file.macros.geo
.. autosummary::
    :toctree: macros/

    complete_link_vertices
    complete_vertices
    reduce_vertices
    simplify_link_vertices
    simplify_vertices
    transform_coordinates

GIS
~~~

.. currentmodule:: swmm_api.input_file.macros.gis
.. autosummary::
    :toctree: macros/

    convert_inp_to_geo_package
    get_subcatchment_connectors
    gpkg_to_swmm
    links_geo_data_frame
    nodes_geo_data_frame
    problems_to_gis
    update_length
    write_geo_package

Graph
~~~~~

.. currentmodule:: swmm_api.input_file.macros.graph
.. autosummary::
    :toctree: macros/

    conduit_iter_over_inp
    downstream_nodes
    get_network_forks
    get_path
    get_path_subgraph
    inp_to_graph
    links_connected
    next_links
    next_links_labels
    next_nodes
    number_in_out
    previous_links
    previous_links_labels
    previous_nodes
    split_network
    upstream_nodes

Other Macros
~~~~~~~~~~~~

.. currentmodule:: swmm_api.input_file.macros.macros
.. autosummary::
    :toctree: macros/

    calc_slope
    combined_nodes_frame
    combined_subcatchment_frame
    conduit_slopes
    conduits_are_equal
    delete_sections
    find_link
    find_node
    increase_max_node_depth
    iter_sections
    nodes_data_frame
    set_times
    update_no_duplicates

Plotting
~~~~~~~~

.. currentmodule:: swmm_api.input_file.macros.plotting
.. autosummary::
    :toctree: macros/

    get_longitudinal_data
    get_node_station
    get_water_level
    iter_over_inp
    iter_over_inp_
    plot_longitudinal
    plot_map
    set_inp_dimensions
    set_zero_node

Reduce Unneeded
~~~~~~~~~~~~~~~

.. currentmodule:: swmm_api.input_file.macros.reduce_unneeded
.. autosummary::
    :toctree: macros/

    reduce_controls
    reduce_curves
    reduce_pattern
    reduce_raingages
    remove_empty_sections
    simplify_curves

Split the inp File
~~~~~~~~~~~~~~~~~~

.. currentmodule:: swmm_api.input_file.macros.split_inp_file
.. autosummary::
    :toctree: macros/

    read_split_inp_file
    split_inp_to_files

Tags
~~~~

.. currentmodule:: swmm_api.input_file.macros.tags
.. autosummary::
    :toctree: macros/

    delete_tag_group
    filter_tags
    get_link_tags
    get_node_tags
    get_subcatchment_tags
