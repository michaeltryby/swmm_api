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

    SwmmOutput.filename
    SwmmOutput.number_columns

Export
~~~~~~
.. autosummary::
    :toctree: out/

    SwmmOutput.get_part
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

Parquet I/O
~~~~~~~~~~~

.. currentmodule:: swmm_api.output_file.parquet

.. autosummary::
    :toctree: out/

    read
    write
