*********
flashback
*********

Overview
========

**flashback**, is a simple command-line utility that offers fast system and configuration file
recovery on remote hosts.

It is a tool that is generally used for archiving smallish files just prior to the roll-out
of configuration changes, and only one version of the file or files may be archived per day.
If subsequent archive commands are run in the same day, only the latest version persists.


Example Usage
=============

Archive /etc/rsyslog.conf
-------------------------
*Let's say we are about to roll out significant changes to
/etc/rsyslog.conf through some other mechanism (e.g. chef or SaltStack), and we
are very concerned about the prospect of something going wrong and losing
several minutes of log data.  Let's perform a backup which will allow us to recover
near instantly, in the event something goes wrong, such as a syntax error
that was not caught.*

.. code-block:: bash

    $ flashback archive -H localhost -F /etc/rsyslog.conf

.. note::
    -H may be specified multiple times, but more commonly, consider using
    -f hosts.txt, where hosts.txt is a file containing a list of hosts
    to act upon, one hostname per line.

Diff Two Versions
-----------------
*Diff the current and archived version (from earlier in the same day, assuming
it exists) of /etc/rsyslog.conf*

.. code-block:: bash

    $ flashback diff -F /etc/rsyslog.conf -H localhost

.. note::

    Any two versions (there is a max of one archive per file, per day) may be compared.
    Please use the --date-first and --date-second arguments.

Recover
-------
*Continuing with the /etc/rsylog.conf example, let's say something did go wrong, and
we need to recover the latest version (archived today) immediately.  We can recover
the file and perform an rsyslog restart.*


.. code-block:: bash

    $ flashback recover -H localhost -F /etc/rsyslog.conf \
      --post-recover-command="sudo service rsyslog restart"

Report
------
*It may be necessary to get a precise idea of exactly what has been archived on a
server, or across several servers.  The report subcommand provides a hierarchical
listing, broken down by date.*

.. code-block:: bash

    $ flashback report -H localhost -f /etc/rsyslog.conf

Purge
-----
*It may be desirable to delete all archived files, which may be accomplished by
using the purge subcommand.*

.. code-block:: bash

    $ flashback report -H localhost


Important Considerations
========================

+ Only one archive of any file may exist per day, re-running the archive subcommand will
  overwrite any previous archives from earlier in the day

+ Backed up file names must be unique, or a collision may occur.  For example, archiving
  both /etc/rsylog.conf and /usr/local/etc/rsyslog.conf will result in the last file
  to be archived overwriting the first one.

+ If not using the default archive directory (/root/.flashback), precautions should be
  taken to ensure sensitive file archives are properly protected.


Command-line Reference
======================

.. argparse::
   :module: flashback.scripts.cli
   :func: parse_arguments
   :prog: flashback

