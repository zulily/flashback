.. flashback documentation master file, created by
   bhodges.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to flashback's documentation!
================================

**flashback version:** |version|

``flashback`` is a `command-line tool <./flashback.html>`_ that provides simplified archival and recovery
of smallish system and configuration files, such as /etc/passwd or /etc/mysql/my.cnf.  It can
provide assurance with its quick recovery functionality, when rolling out significant changes related to
account management, or configuration changes for just about any service.
It leverages fabric and may be run across a large fleet of Linux instances in parallel.


Contents:

.. toctree::
   :maxdepth: 2

   getting_started
   flashback
   license


