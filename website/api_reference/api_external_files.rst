External SWMM Files
-------------------

Climate File
^^^^^^^^^^^^

SWMM5 User Manual: Section 11.4 Climate Files

A user-prepared climate file where each line contains a recording station name, the year, month, day,
maximum temperature, minimum temperature, and optionally, evaporation rate, and wind speed.

If no data are available for any of these items on a given date, then an asterisk should be entered as its value

For a user-prepared climate file, the data must be in the same units as the project being analyzed.

For US units,
    - temperature is in degrees F,
    - evaporation is in inches/day, and
    - wind speed is in miles/hour.

For metric units,
    - temperature is in degrees C,
    - evaporation is in mm/day, and
    - wind speed is in km/hour.

.. automodule:: swmm_api.input_file.misc.climate_file
    :members:
    :no-undoc-members:


Timeseries File
^^^^^^^^^^^^^^^

SWMM5 User Manual: Section 11.6 Time Series Files

.. automodule:: swmm_api.input_file.misc.dat_timeseries
    :members:
    :no-undoc-members:
