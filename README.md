flashback
=========
**flashback** is a python script that leverages fabric to quickly roll-back configuration changes
gone awry.  Thanks to fabric, it parallelizes well, and provides quick recovery for replacing smallish text files
with previous versions, assuming sshd continues to work and the authenticated user on the
remote server has appropriate sudo permissions.

Documentation
--------------
For the full CLI reference including usage examples, please see [full project documentation](http://zulily.github.io/flashback/).

Prerequisites
--------------

*To get up and running, the following must be installed:*

+ python 2.7.x
+ fabric and its dependencies
+ jinja2

Installation
------------
+ Create a virtual environment and activate
+ Clone this git repository
+ pip install .

*Optionally for sphinx document generation, pip install the following*

+ sphinx
+ pygments
+ sphinx_rtd_theme
+ sphinx-argparse


Example CLI Usage
-----------------
**Create a backup of /etc/rsyslog.conf for all hosts listed in hosts.txt**

```bash
flashback archive -f hosts.txt -F /etc/rsyslog.conf --parallel-workers=5
```

**Recover the archived version of /etc/rsyslog.conf from earlier in the day and perform a service restart**

```bash
flashback -f hosts.txt -F /etc/rsyslog.conf --parallel-workers=5 \
--post-recover-command="sudo service rsyslog restart"
```

License
-------
Apache License, version 2.0.  Please see LICENSE
