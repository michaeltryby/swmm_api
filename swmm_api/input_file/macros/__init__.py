from .check import check_for_nodes, check_for_duplicates
from .collection import nodes_dict, links_dict, subcatchments_per_node_dict, nodes_subcatchments_dict
from .compare import CompareSections, compare_inp_files, compare_sections
from .convert import junction_to_storage, junction_to_outfall, conduit_to_orifice
from .curve import curve_figure
from .edit import (combine_conduits, combine_conduits_keep_slope, combine_vertices, delete_link, delete_node,
                   delete_subcatchment, dissolve_conduit, flip_link_direction, move_flows, rename_link, rename_node,
                   rename_subcatchment, rename_timeseries, split_conduit, remove_quality_model, delete_pollutant)
from .filter import (filter_tags, filter_nodes, filter_links_within_nodes, filter_links, filter_subcatchments,
                     create_sub_inp, )
from .geo import (transform_coordinates, complete_vertices, reduce_vertices, complete_link_vertices,
                  simplify_link_vertices, simplify_vertices, )

try:
    import warnings

    warnings.filterwarnings('ignore', message='.*is incompatible with the GEOS version PyGEOS*')

    from .gis import (convert_inp_to_geo_package, write_geo_package, get_subcatchment_connectors,
                      links_geo_data_frame, nodes_geo_data_frame, gpkg_to_swmm, update_length, set_crs, update_area)
except ImportError as e:
    print('Needed Packages: pyproj, fiona, geopandas, shapely')
    print(e)
    pass

from .graph import (inp_to_graph, get_path, get_path_subgraph, next_links, next_links_labels, next_nodes,
                    previous_links, previous_links_labels, previous_nodes, links_connected, number_in_out,
                    downstream_nodes, upstream_nodes, get_network_forks, split_network, conduit_iter_over_inp)
from .macros import (find_node, find_link, calc_slope, conduit_slopes, conduits_are_equal, update_no_duplicates,
                     increase_max_node_depth, set_times, combined_subcatchment_frame, delete_sections)
from .plotting_longitudinal import plot_longitudinal
from .plotting_map import (plot_map, init_empty_map_plot, add_node_map, add_link_map, add_subcatchment_map,
                           add_node_labels, set_inp_dimensions)
from .reduce_unneeded import (reduce_curves, reduce_controls, simplify_curves, reduce_raingages,
                              remove_empty_sections, reduce_timeseries, reduce_pattern)
from .split_inp_file import split_inp_to_files, read_split_inp_file
from .summerize import print_summary
from .tags import get_node_tags, get_link_tags, get_subcatchment_tags, filter_tags, delete_tag_group

try:
    from .cross_section_curve import (get_cross_section_maker, profil_area, to_cross_section_maker)
except ImportError as e:
    print('Missing package: pip install SWMM-xsections-shape-generator')
