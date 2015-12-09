edeposit.amqp.rest
==================

REST API for the E-deposit_ project.

.. _E-deposit: http://edeposit.nkp.cz/

Package structure
-----------------

API
+++

:doc:`/api/rest`:

.. toctree::
    :maxdepth: 1

    /api/settings.rst

:doc:`/api/database/database`

.. toctree::
    :maxdepth: 1

    /api/database/user_handler.rst
    /api/database/cache_handler.rst
    /api/database/status_handler.rst

:doc:`/api/structures/structures`

.. toctree::
    :maxdepth: 1

    /api/structures/incomming.rst
    /api/structures/outgoing.rst


Source code
+++++++++++
Project is released under the MIT license. Source code can be found at GitHub:

- https://github.com/edeposit/edeposit.amqp.storage


Installation
------------

Installation of this project is little bit more complicated. Please read installation notes:

.. toctree::
    :maxdepth: 1

    /installation/instalace_cz.rst

Unittests
+++++++++

Almost every feature of the project is tested by unittests. You can run those
tests using provided ``run_tests.sh`` script, which can be found in the root
of the project.

If you have any trouble, just add ``--pdb`` switch at the end of your ``run_tests.sh`` command like this: ``./run_tests.sh --pdb``. This will drop you to `PDB`_ shell.

.. _PDB: https://docs.python.org/2/library/pdb.html

Requirements
^^^^^^^^^^^^
This script expects that packages pytest_ is installed. In case you don't have it yet, it can be easily installed using following command::

    pip install --user pytest

or for all users::

    sudo pip install pytest

.. _pytest: http://pytest.org/

Example
^^^^^^^
::

    ./run_tests.sh
    ============================= test session starts ==============================
    platform linux2 -- Python 2.7.6, pytest-2.8.2, py-1.4.30, pluggy-0.3.1
    rootdir: /home/bystrousak/Plocha/Dropbox/c0d3z/prace/edeposit.amqp.rest, inifile: 
    plugins: cov-1.8.1
    collected 29 items 

    tests/test_context_manager.py .
    tests/database/test_cache_handler.py ...
    tests/database/test_status_handler.py ..........
    tests/database/test_user_handler.py ....
    tests/rest/test_rest.py ...........
    No handlers could be found for logger "ZEO.zrpc"


    ========================== 29 passed in 36.13 seconds ==========================

Indices and tables
++++++++++++++++++

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
