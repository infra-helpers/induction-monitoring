========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/datamonitoring/badge/?style=flat
    :target: https://readthedocs.org/projects/datamonitoring
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.org/infra-helpers/induction-monitoring.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/infra-helpers/induction-monitoring

.. |requires| image:: https://requires.io/github/infra-helpers/induction-monitoring/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/infra-helpers/induction-monitoring/requirements/?branch=master

.. |codecov| image:: https://codecov.io/gh/infra-helpers/induction-monitoring/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/infra-helpers/induction-monitoring

.. |version| image:: https://img.shields.io/pypi/v/datamonitor.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/datamonitor

.. |wheel| image:: https://img.shields.io/pypi/wheel/datamonitor.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/datamonitor

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/datamonitor.svg
    :alt: Supported versions
    :target: https://pypi.org/project/datamonitor

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/datamonitor.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/datamonitor

.. |commits-since| image:: https://img.shields.io/github/commits-since/infra-helpers/induction-monitoring/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/infra-helpers/induction-monitoring/compare/v0.0.0...master



.. end-badges

Python utility to monitor metadata KPI

* Free software: MIT license

Installation
============

::

    pip install datamonitor

You can also install the in-development version with::

    pip install https://github.com/infra-helpers/induction-monitoring/archive/master.zip


Documentation
=============


https://datamonitoring.readthedocs.io/en/latest/


Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
