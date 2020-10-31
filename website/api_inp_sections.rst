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

.. rubric:: Convert for Generic Sections

.. autosummary::
    convert_title
    convert_options
    convert_evaporation
    convert_temperature

.. rubric:: Generic Sections

.. autosummary::
    ReportSection
    TagsSection
    MapSection

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
    TimeseriesFile
    TimeseriesData

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

generic_section
---------------

.. automodule:: swmm_api.input_file.inp_sections.generic_section
    :members:
    :no-undoc-members:
    :special-members:

others
------

.. automodule:: swmm_api.input_file.inp_sections.others
    :members:
    :no-undoc-members:
    :special-members:

node
----

.. automodule:: swmm_api.input_file.inp_sections.node
    :members:
    :no-undoc-members:
    :special-members:

.. automodule:: swmm_api.input_file.inp_sections.node_component
    :members:
    :no-undoc-members:
    :special-members:

Link
----

.. automodule:: swmm_api.input_file.inp_sections.link
    :members:
    :no-undoc-members:
    :special-members:

.. automodule:: swmm_api.input_file.inp_sections.link_component
    :members:
    :no-undoc-members:

Subcatchment
------------

.. automodule:: swmm_api.input_file.inp_sections.subcatch
    :members:
    :no-undoc-members:
