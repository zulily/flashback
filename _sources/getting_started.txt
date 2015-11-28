***************
Getting Started
***************

Installation
============

Prerequisites
-------------

*To get up and running, the following must be installed:*

* python 2.7.x
* fabric
* jinja2

*Other requirements:*

* The ability to ssh to remote machines and run specific commands (cp, diff, find, mkdir, rm) with sudo
* The ability to run arbitrary sudo commands (optional with --post-recover-command cli argument)

pip
---
From the top-level directory of the cloned repository:

.. code-block:: bash

    pip install .

.. note:: This is typically performed within an active python virtual environment.

And for *optional* document generation with sphinx, install the following python packages as well:

.. code-block:: bash

    pip install sphinx
    pip install pygments
    pip install sphinx_rtd_theme
    pip install sphinx-argparse


Basic Usage
===========

*For a full set of CLI usage examples, please see the* :doc:`flashback` *cli* documentation.
