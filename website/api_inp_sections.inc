Input File Sections
-------------------

Import from
`swmm_api.input_file.inp_sections.labels <https://gitlab.com/markuspichler/swmm_api/-/blob/master/swmm_api/input_file/inp_sections/labels.py>`_
all section headers, so you don't have to write every string for your own and save some typo error handling.

.. code-block:: python

    from swmm_api.input_file.inp_sections import labels

Each section has a specific type, which can be seen under:
`swmm_api.input_file.inp_sections.types <https://gitlab.com/markuspichler/swmm_api/-/blob/master/swmm_api/input_file/inp_sections/types.py>`_


.. currentmodule:: swmm_api.input_file.inp_sections.generic_section

.. rubric:: Generic Sections

.. autosummary::
    OptionSection
    ReportSection
    EvaporationSection
    TemperatureSection
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
    Tag


Generic Sections
^^^^^^^^^^^^^^^^

.. currentmodule:: swmm_api.input_file.inp_sections.generic_section

.. rubric:: Overview

.. autosummary::
    OptionSection
    ReportSection
    EvaporationSection
    TemperatureSection
    MapSection

.. automodule:: swmm_api.input_file.inp_sections.generic_section
    :members:
    :no-undoc-members:


Node Sections
^^^^^^^^^^^^^

.. currentmodule:: swmm_api.input_file.inp_sections.node

.. rubric:: Overview

.. autosummary::
    Junction
    Storage
    Outfall

.. currentmodule:: swmm_api.input_file.inp_sections.node_component

.. autosummary::
    DryWeatherFlow
    Inflow
    Coordinate

.. automodule:: swmm_api.input_file.inp_sections.node
    :members:
    :no-undoc-members:

.. automodule:: swmm_api.input_file.inp_sections.node_component
    :members:
    :no-undoc-members:

Link Sections
^^^^^^^^^^^^^

.. currentmodule:: swmm_api.input_file.inp_sections.link

.. rubric:: Overview

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

.. automodule:: swmm_api.input_file.inp_sections.link
    :members:
    :no-undoc-members:

.. automodule:: swmm_api.input_file.inp_sections.link_component
    :members:
    :no-undoc-members:

Subcatchment Sections
^^^^^^^^^^^^^^^^^^^^^

.. currentmodule:: swmm_api.input_file.inp_sections.subcatch

.. rubric:: Overview

.. autosummary::
    SubCatchment
    SubArea
    Infiltration
    InfiltrationHorton
    InfiltrationGreenAmpt
    InfiltrationCurveNumber
    Polygon
    Loading

.. automodule:: swmm_api.input_file.inp_sections.subcatch
    :members:
    :no-undoc-members:


Other Object-based Sections
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. currentmodule:: swmm_api.input_file.inp_sections.others

.. rubric:: Overview

.. autosummary::
    RainGage
    Symbol
    Pattern
    Pollutant
    Transect
    Control
    Curve
    Timeseries
    Tag

.. automodule:: swmm_api.input_file.inp_sections.others
    :members:
    :no-undoc-members:
