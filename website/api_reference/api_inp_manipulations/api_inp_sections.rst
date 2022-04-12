Input File Sections
-------------------

Import from
`swmm_api.input_file.section_labels <https://gitlab.com/markuspichler/swmm_api/-/blob/master/swmm_api/input_file/section_labels.py>`_
all section headers, so you don't have to write every string for your own and save some typo error handling.

.. code-block:: python

    from swmm_api.input_file import section_labels

Each section has a specific type, which can be seen under:
`swmm_api.input_file.section_types <https://gitlab.com/markuspichler/swmm_api/-/blob/master/swmm_api/input_file/section_types.py>`_


.. currentmodule:: swmm_api.input_file.sections

Generic Sections
^^^^^^^^^^^^^^^^
.. autosummary::
    :toctree: inp_sections/

    TitleSection
    OptionSection
    ReportSection
    EvaporationSection
    TemperatureSection
    MapSection
    FilesSection
    AdjustmentsSection
    BackdropSection

Node Sections
^^^^^^^^^^^^^
.. autosummary::
    :toctree: inp_sections/

    Junction
    Storage
    Outfall

.. autosummary::
    :toctree: inp_sections/

    DryWeatherFlow
    Inflow
    Coordinate
    RainfallDependentInfiltrationInflow
    Treatment


Link Sections
^^^^^^^^^^^^^
.. autosummary::
    :toctree: inp_sections/

    Conduit
    Weir
    Outlet
    Orifice
    Pump

.. autosummary::
    :toctree: inp_sections/

    CrossSection
    Loss
    Vertices


Subcatchment Sections
^^^^^^^^^^^^^^^^^^^^^
.. autosummary::
    :toctree: inp_sections/

    SubCatchment
    SubArea
    Infiltration
    InfiltrationHorton
    InfiltrationCurveNumber
    InfiltrationGreenAmpt
    Polygon
    Loading
    Coverage
    Groundwater
    GroundwaterFlow

Other Object-based Sections
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autosummary::
    :toctree: inp_sections/

    RainGage
    Symbol
    Pattern
    Pollutant
    Transect
    Control
    Curve
    Street
    Inlet
    InletUsage
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

LID Sections
^^^^^^^^^^^^
.. autosummary::
    :toctree: inp_sections/

    LIDControl
    LIDUsage
