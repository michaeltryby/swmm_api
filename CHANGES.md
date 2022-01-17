# Changelog  
## 0.2.0.16 (Jan 7, 2022)
- moved predefined output file variables (VARIABLES, OBJECTS) to swmm_api.output_file.definitions
- new functions:
- swmm_api.input_file.macros.iter_sections
- swmm_api.input_file.macros.delete_sections
- added functions `add_obj` and `add_multiple` to SwmmInput object
- added function `delete_tag_group` to delete tags for specific objects i.e. all node tags
- `SEC` as reference for inp-sections
- remove ignore_sections, convert_sections and ignore_gui_sections parameters of swmm_api.SwmmInput.read_file
  - sections with be converted wenn needed.
- added function
  - SwmmInput.force_convert_all()
- added `SUBCATCHMENT_SECTIONS` to `swmm_api.input_file.section_lists`
- 

## 0.2.0.15 (Nov 19, 2021)
- added functions in swmm_api.input_file.macros.*
- added documentation for marcos
- minor changes

## 0.2.0.14 (Nov 11, 2021)
- New `TITLE` Section `TitleSection` based on `UserString`
- Default Infiltration based on `OPTIONS` - `INFILTRATION` parameter (function: `SwmmInput.set_default_infiltration`)
- added `InpSection.set_parent_inp` and `InpSection.get_parent_inp` to InpSections

## 0.2.0.13 (Oct 21, 2021)
- SwmmOutExtract.get_selective_results small performance boost
- new function: update_length
- updated and add example files
- resorted macros
- added macros with package `SWMM_xsections_shape_generator`
- added Summary tables to SwmmReport reader
- fixed some issued with SwmmReport
- new function: `check_for_duplicates`

## 0.2.0.12 (Sep 28, 2021)
- fixed out reader for custom pollutant unit
- gis import example
- LINK_SECTIONS, NODE_SECTIONS as section list
- SnowPack as new Class for reader
- datetime format fixed for import and export
- new "check_for_duplicates" macro
- fixed run for linux
- new get_swmm_version function
- pyswmm runner (not stable)
- fixed docker for documentation site

## 0.2.0.6 (Sep 15, 2021)
- better gis export
- compare inp files
- macro documentations

## 0.2.0.5 (Sep 10, 2021)
- gis export of all nodes, links as separate function
- added subcatchment connector to gis export
- added inp write and inp to string to SwmmInput class
- abstract class for nodes and links

## 0.2.0.4 (May 27, 2021)

- fixed errors when object labels start with a number
- rewritten out-file-reader

## 0.2.0.3 (May 18, 2021)

- fixed errors when `-nan(ind)` in report file

## 0.2.0.2 (May 5, 2021)

- added polygons to transform coordinated function
- added geopandas_to_polygons
- fixed some documentation errors
- fixed tag error (spaces in tag)
- fixed undefined types in some objects
- added function "add_inp_lines" to add a collection of lines to an existing section
- set default of "ignore_gui_sections" in "SwmmInput.read_file" to False
- added "delete_subcatchment" to macros
- fixed faulty tag filter in filter_nodes/_links/_subcatchments

## 0.2 (Apr 6, 2021)

## 0.1a25  (Apr 1, 2021)

## 0.1a24  (Mar 30, 2021)

## 0.1a23  (Feb 19, 2021)

## 0.1a22  (Dec 15, 2020)

## 0.1a21  (Nov 18, 2020)

Changes Including:
- 0.1a20  (Nov 9, 2020)
- 0.1a19  (Nov 6, 2020)
- 0.1a18  (Nov 6, 2020)

## 0.1a17  (Oct 16, 2020)

Changes Including:
- 0.1a16  (Sep 30, 2020)
- 0.1a15  (Sep 24, 2020)
- 0.1a14  (Sep 23, 2020)
- 0.1a13  (Sep 23, 2020)
- 0.1a12  (Sep 23, 2020)
- 0.1a11  (Sep 14, 2020)

## 0.1a10  (Aug 27, 2020)

Changes Including:
- 0.1a9  (Aug 27, 2020)

## 0.1a8  (Apr 19, 2020)

Changes Including:
- 0.1a7  (Apr 19, 2020)

## 0.1a6  (Nov 13, 2019)

Changes Including:
- 0.1a5  (Nov 8, 2019)
- 0.1a4  (Nov 4, 2019)
- 0.1a3  (Oct 28, 2019)
- 0.1a2  (Oct 3, 2019)
- 0.1a0  (Oct 2, 2019)