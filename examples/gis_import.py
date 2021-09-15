from swmm_api.input_file.macro_snippets.gis_standard_import import gpkg_to_swmm

if __name__ == '__main__':
    inp = gpkg_to_swmm('/mnt/Windows/Users/mp/GIS/inp_update.gpkg')
    print()