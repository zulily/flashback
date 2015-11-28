# Copyright (C) 2015 zulily, llc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""flashback tasks"""
from __future__ import print_function

import os
import re

from datetime import datetime
from fabric.api import env, sudo
from fabric.colors import green, red, yellow
from jinja2 import Environment, PackageLoader

def recover_files(system_files_map, recover_date, archive_directory, dry_run):
    """For all hosts and specified system files, rollback
    to the recover date that was specified.
    """
    if dry_run:
        print(yellow('File Recovery -- dry-run\n'))
    if recover_date == 0:
        recover_date = datetime.now().strftime('%Y%m%d')
    for system_file in system_files_map:
        try:
            source_file = os.path.join(archive_directory,
                                       str(recover_date), system_file)
            if dry_run:
                print(yellow('[{0}] Restoring {1}/{2} -> {3}'.\
                format(env.host_string, recover_date, system_file,
                       system_files_map[system_file])))
            else:
                sudo("cp -af {0} {1}".\
                     format(source_file, system_files_map[system_file]))
                print(green('[{0}] Restored {1}/{2} -> {3}'.\
                format(env.host_string, recover_date, system_file,
                       system_files_map[system_file])))
        except Exception:
            print(red('[{0}] Error rolling back file {1}/{2} -> {3}'.\
            format(env.host_string, recover_date, system_file,
                   system_files_map[system_file])))


def post_recover_command(command, dry_run):
    """After completing a recover command, execute a command, such
    as restarting a service
    """
    if dry_run:
        print(yellow('Post-recover Command -- dry-run\n'))
        print(yellow('[{0}] Executing command: {1}'.\
        format(env.host_string, command)))
    else:
        try:
            sudo(command)
            print(green('[{0}] Executed command: {1}'.\
                  format(env.host_string, command)))
        except:
            print(red('[{0}] Error executing command: {1}'.\
                      format(env.host_string, command)))


def diff_files(system_files_map, date_first, date_second, archive_directory):
    """Going through the list of system_files specified, perform
    diffs against two dates.  If a version of the file is missing,
    warn and continue.
    """
    today = datetime.now().strftime('%Y%m%d')
    try:
        for system_file in system_files_map:
            # If today's date is specfied for date_first, we will use
            # the archived version, if it exists
            if date_first == 0:
                file_first = os.path.join(archive_directory,
                                          datetime.now().strftime('%Y%m%d'),
                                          system_file)
                date_first = str(datetime.now().strftime('%Y%m%d'))
            else:
                file_first = os.path.join(archive_directory,
                                          str(date_first), system_file)
            # If today's date is specfied for date_second, we will use the
            # live, non-archived copy.
            if today == date_second or date_second == 1 or \
            date_second == 'current':
                date_second = 'current'
                file_second = system_files_map[system_file]
            else:
                file_second = os.path.join(archive_directory,
                                           str(date_second), system_file)
            output = sudo("diff -u {0} {1} || exit 0".\
                          format(file_first, file_second))
            if len(output) == 0:
                print(green('[{0}] No differences for {1}: {2} {3}'.\
                      format(env.host_string, system_file, str(date_first),
                             str(date_second))))
            else:
                print(yellow("[{0}]").format(env.host_string))
                print(yellow(output.replace('[H', '')))
    except Exception:
        print(red('[{0}] Error running diff command'.\
                  format(env.host_string)))
        raise


def get_archive_data(output):
    """Build up a dict with host names for keys,
    date dicts as values with the date dicts having archive
    files stored in the value as a list. The ouput, input
    parameter is captured output from a remotely executed
    find commmand.
    """
    archive_data = dict()
    for host in output:
        if host not in archive_data:
            archive_data[host] = dict()
        if output[host]:
            for full_path in output[host].split():
                if re.search(r'\/\d{8}\/', full_path):
                    date = full_path.split('/')[-2:-1][0]
                    system_file = os.path.basename(full_path)
                else:
                    continue
                if date not in archive_data[host]:
                    archive_data[host][date] = list()
                if system_file not in archive_data[host][date]:
                    archive_data[host][date].append(system_file)

    return archive_data


def generate_report(archive_data):
    """Using a template, generate a simple report that lists
    archived files by host name, by date
    """
    jenv = Environment(loader=PackageLoader('flashback', 'templates'))
    template = jenv.get_template('archived_report.jinja')

    return template.render(data=archive_data)


def find_archived_files(archive_directory):
    """For all hosts, get a list of system files that are archived"""
    try:
        return sudo("test -d {0} && find {0} -type f || exit 0".\
                    format(archive_directory))
    except Exception:
        print(red('[{0}] Error running find command under directory {1}'.\
                  format(env.host_string, archive_directory)))


def archive_files(system_files, archive_directory):
    """Archive specified system files into archive_directory/YYYYMMDD/.  Only
    copies if destination does not exist or is older than source
    """
    destination_directory = os.path.join(archive_directory,
                                         datetime.now().strftime('%Y%m%d'))
    sudo("mkdir -p {0}".format(destination_directory))
    for system_file in system_files:
        full_path = os.path.join(destination_directory, system_file)
        try:
            sudo("cp -up {0} {1}".format(full_path, destination_directory))
        except Exception:
            print(red('[{0}] Error archiving file {1}'.\
                      format(env.host_string, system_file)))
        print(green('[{0}] Archived file {1}'.format(env.host_string, system_file)))


def purge(archive_directory):
    """Purge archive_directory, use with caution!"""
    try:
        sudo("rm -rf {0}".format(archive_directory))
        print(green('[{0}] Purged directory {1}'.\
                    format(env.host_string, archive_directory)))
    except:
        print(red('[{0}] Error purging directory {1}'.\
                  format(env.host_string, archive_directory)))



