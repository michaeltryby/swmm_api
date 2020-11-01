===============================
API for the Input File Sections
===============================

Import from
`swmm_api.input_file.inp_sections.labels <https://gitlab.com/markuspichler/swmm_api/-/blob/master/swmm_api/input_file/inp_sections/labels.py>`_
all section headers, so you don't have to write every string for your own and save some typo error handling.

.. code-block:: python

    from swmm_api.input_file.inp_sections import labels

Each section has a specific type, which can be seen under:
`swmm_api.input_file.inp_sections.types <https://gitlab.com/markuspichler/swmm_api/-/blob/master/swmm_api/input_file/inp_sections/types.py>`_

Input File Sections
===================

.. currentmodule:: swmm_api.input_file.inp_sections.generic_section

.. rubric:: Converter for Generic Sections

.. autosummary::
    convert_title
    convert_options
    convert_evaporation
    convert_temperature

.. rubric:: Classes of Generic Sections

.. autosummary::
    ReportSection
    TagsSection
    MapSection

.. currentmodule:: swmm_api.input_file.inp_sections.node

.. rubric:: Node Sections

.. autosummary::
    Junction
    Storage
    Outfall

.. currentmodule:: swmm_api.input_file.inp_sections.node_component

.. autosummary::
    DryWeatherFlow
    Inflow
    Coordinate

.. currentmodule:: swmm_api.input_file.inp_sections.link

.. rubric:: Link Sections

.. autosummary::
    Conduit
    Weir
    Outlet
    Orifice
    Pump

.. currentmodule:: swmm_api.input_file.inp_sections.link_component

.. autosummary::
    CrossSection
    Loss
    Vertices

.. currentmodule:: swmm_api.input_file.inp_sections.subcatch

.. rubric:: Subcatchment Sections

.. autosummary::
    SubCatchment
    SubArea
    Infiltration
    Polygon
    Loading

.. currentmodule:: swmm_api.input_file.inp_sections.others

.. rubric:: Other Object-based Sections

.. autosummary::
    RainGage
    Symbol
    Pattern
    Pollutant
    Transect
    Control
    Curve
    Timeseries


Generic Sections
----------------

.. automodule:: swmm_api.input_file.inp_sections.generic_section
    :members:
    :no-undoc-members:

Node Sections
-------------

.. automodule:: swmm_api.input_file.inp_sections.node
    :members:
    :no-undoc-members:

.. automodule:: swmm_api.input_file.inp_sections.node_component
    :members:
    :no-undoc-members:

Link Sections
-------------

.. automodule:: swmm_api.input_file.inp_sections.link
    :members:
    :no-undoc-members:

.. automodule:: swmm_api.input_file.inp_sections.link_component
    :members:
    :no-undoc-members:

Subcatchment Sections
---------------------

.. automodule:: swmm_api.input_file.inp_sections.subcatch
    :members:
    :no-undoc-members:


Other Object-based Sections
---------------------------

.. automodule:: swmm_api.input_file.inp_sections.others
    :members:
    :no-undoc-members:
