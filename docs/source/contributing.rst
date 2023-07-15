============
Contributing
============


Environment Setup
~~~~~~~~~~~~~~~~~

Clone the source codes from Github.

.. code-block:: shell

    git clone https://github.com/linw1995/jsonpath.git
    cd jsonpath

Setup the development environment.
Please make sure you install the pdm_,
pre-commit_ and nox_ CLIs in your environment.

.. code-block:: shell

    make init
    make PYTHON=3.8 init  # for specific python version

Linting
~~~~~~~

Use pre-commit_ for installing linters to ensure a good code style.

.. code-block:: shell

    make pre-commit

Run linters. Some linters run via CLI nox_, so make sure you install it.

.. code-block:: shell

    make check-all

Testing
~~~~~~~

Run quick tests.

.. code-block:: shell

    make

Run quick tests with verbose.

.. code-block:: shell

    make vtest

Run tests with coverage.
Testing in multiple Python environments is powered by CLI nox_.

.. code-block:: shell

    make cov

Documentation
~~~~~~~~~~~~~

Run serving documents with live-reloading.

.. code-block:: shell

    make serve-docs

.. _pdm: https://github.com/pdm-project/pdm
.. _pre-commit: https://pre-commit.com/
.. _nox: https://nox.thea.codes/en/stable/
