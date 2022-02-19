Output File Reader
==================
.. currentmodule:: swmm_api

Constructor
~~~~~~~~~~~
.. autosummary::
    :toctree: out/

    SwmmOutput
    read_out_file

Macro
~~~~~
.. autosummary::
    :toctree: out/

    out2frame

Content
~~~~~~~
.. autosummary::
    :toctree: out/

    SwmmOutput.get_part
    SwmmOutput.number_columns
    SwmmOutput.filename

Export
~~~~~~
.. autosummary::
    :toctree: out/

    SwmmOutput.to_frame
    SwmmOutput.to_numpy
    SwmmOutput.to_parquet

Definitions
~~~~~~~~~~~
.. currentmodule:: swmm_api.output_file

.. autosummary::
    :toctree: out/

    OBJECTS
    VARIABLES

.. currentmodule:: swmm_api.output_file.definitions

.. autosummary::
    :toctree: out/

    SUBCATCHMENT_VARIABLES
    NODE_VARIABLES
    LINK_VARIABLES
    SYSTEM_VARIABLES
