Reproduction Scripts for `python-firestore` #18
###############################################

See: https://github.com/googleapis/python-firestore/issues/18


Installing in a Virtual Environment
-----------------------------------

- Create the virtual environment with Python 3.7:

.. code-block:: bash

    $ export VENV=/tmp/repro-gcf-18
    $ python3.7 -m venv $VENV
    $ $VENV/bin/pip install --upgrade "setuptools < 50.0.0" pip

- Install latest 1.x Firestore:

.. code-block:: bash

    $ $VENV/bin/pip install "google-cloud-firestore < 2.0dev"

Or install a specific version, e.g.:

.. code-block:: bash

    $ $VENV/bin/pip install "google-cloud-firestore == 1.6.1"

Setting up Credentials
----------------------

.. code-block:: bash

    $ export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
    $ export GOOGLE_CLOUD_PROJECT=<PROJECT ID HERE>

Running the Listener
--------------------

In a separate terminal, first setup credentials, then:

.. code-block:: bash

    $ $VENV/bin/python listen_query.py

To see the ``DEBUG`` level messages, run as:

.. code-block:: bash

    $ $VENV/bin/python listen_query.py --debug


Running the Updater
-------------------

In one or more separate terminals, first setup credentials, then:

.. code-block:: bash

    $ $VENV/bin/python update_document.py --count 10000 --interval 100

This will update a default document, ``watch_me``, within the default
collection, ``repro_gcf_18``, 10000 times, at ~ 100 second intervals.

To update a separate document within the default collection via:

.. code-block:: bash

    $ $VENV/bin/python update_document.py --document <DOC ID> ...
