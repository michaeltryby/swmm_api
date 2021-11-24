Input File Sections
-------------------

Import from
`swmm_api.input_file.section_labels <https://gitlab.com/markuspichler/swmm_api/-/blob/master/swmm_api/input_file/section_labels.py>`_
all section headers, so you don't have to write every string for your own and save some typo error handling.

.. code-block:: python

    from swmm_api.input_file import section_labels

Each section has a specific type, which can be seen under:
`swmm_api.input_file.section_types <https://gitlab.com/markuspichler/swmm_api/-/blob/master/swmm_api/input_file/section_types.py>`_


.. currentmodule:: swmm_api.input_file.sections.generic_section

.. rubric:: Generic Sections

.. autosummary::
    OptionSection
    ReportSection
    EvaporationSection
    TemperatureSection
    MapSection
    FilesSection
    AdjustmentsSection
    BackdropSection

.. currentmodule:: swmm_api.input_file.sections.node

.. rubric:: Node Sections

.. autosummary::
    Junction
    Storage
    Outfall

.. currentmodule:: swmm_api.input_file.sections.node_component

.. autosummary::
    DryWeatherFlow
    Inflow
    Coordinate
    RainfallDependentInfiltrationInflow
    Treatment

.. currentmodule:: swmm_api.input_file.sections.link

.. rubric:: Link Sections

.. autosummary::
    Conduit
    Weir
    Outlet
    Orifice
    Pump

.. currentmodule:: swmm_api.input_file.sections.link_component

.. autosummary::
    CrossSection
    Loss
    Vertices

.. currentmodule:: swmm_api.input_file.sections.subcatch

.. rubric:: Subcatchment Sections

.. autosummary::
    SubCatchment
    SubArea
    Infiltration
    Polygon
    Loading
    Coverage
    GroundwaterFlow
    Groundwater

.. currentmodule:: swmm_api.input_file.sections.others

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
    Tag
    Label
    Hydrograph
    LandUse
    WashOff
    BuildUp
    SnowPack
    Aquifer

.. currentmodule:: swmm_api.input_file.sections.lid

.. rubric:: LID Sections

.. autosummary::
    LIDControl
    LIDUsage


Generic Sections
^^^^^^^^^^^^^^^^

.. currentmodule:: swmm_api.input_file.sections.generic_section

.. rubric:: Overview

.. autosummary::
    OptionSection
    ReportSection
    EvaporationSection
    TemperatureSection
    MapSection
    FilesSection
    AdjustmentsSection
    BackdropSection

.. automodule:: swmm_api.input_file.sections.generic_section
    :members:
    :no-undoc-members:


Node Sections
^^^^^^^^^^^^^

.. currentmodule:: swmm_api.input_file.sections.node

.. rubric:: Overview

.. autosummary::
    Junction
    Storage
    Outfall

.. currentmodule:: swmm_api.input_file.sections.node_component

.. autosummary::
    DryWeatherFlow
    Inflow
    Coordinate
    RainfallDependentInfiltrationInflow
    Treatment

.. automodule:: swmm_api.input_file.sections.node
    :members:
    :no-undoc-members:

.. automodule:: swmm_api.input_file.sections.node_component
    :members:
    :no-undoc-members:

Link Sections
^^^^^^^^^^^^^

.. currentmodule:: swmm_api.input_file.sections.link

.. rubric:: Overview

.. autosummary::
    Conduit
    Weir
    Outlet
    Orifice
    Pump

.. currentmodule:: swmm_api.input_file.sections.link_component

.. autosummary::
    CrossSection
    Loss
    Vertices

.. automodule:: swmm_api.input_file.sections.link
    :members:
    :no-undoc-members:

.. automodule:: swmm_api.input_file.sections.link_component
    :members:
    :no-undoc-members:

Subcatchment Sections
^^^^^^^^^^^^^^^^^^^^^

.. currentmodule:: swmm_api.input_file.sections.subcatch

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
    Coverage
    GroundwaterFlow
    Groundwater

.. automodule:: swmm_api.input_file.sections.subcatch
    :members:
    :no-undoc-members:


Other Object-based Sections
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. currentmodule:: swmm_api.input_file.sections.others

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
    TimeseriesFile
    TimeseriesData
    Tag
    Label
    Hydrograph
    LandUse
    WashOff
    BuildUp
    SnowPack
    Aquifer

.. automodule:: swmm_api.input_file.sections.others
    :members:
    :no-undoc-members:

LID Sections
^^^^^^^^^^^^

.. currentmodule:: swmm_api.input_file.sections.lid

.. rubric:: Overview

.. autosummary::
    LIDControl
    LIDUsage

.. automodule:: swmm_api.input_file.sections.lid
    :members:
    :no-undoc-members:
