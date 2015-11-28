#! /usr/bin/env python
#
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
"""flashback
flashback - given a list of hosts, create backup copies of key
    system files (for example, *smallish* text files that an account
    management system may maintain):
"""
from __future__ import print_function


import argparse
import getpass
import sys
from os.path import basename
from fabric.api import env, hide
from fabric.colors import yellow
from fabric.tasks import execute
from fabric.network import disconnect_all
from flashback.tasks import archive_files, diff_files, find_archived_files, generate_report, \
                            get_archive_data, post_recover_command, purge, recover_files


# Sensitive files such as /etc/shadow must be properly protected
# under the archive directory
ARCHIVE_DIRECTORY = '/root/.flashback'
DEFAULT_WORKERS = 10
# SYSTEM_FILES should only contain *smallish* files such as
# these defaults
SYSTEM_FILES = ['/etc/passwd', '/etc/shadow', '/etc/group', '/etc/gshadow']


def main():
    """Do some stuff..."""
    args = parse_arguments().parse_args()

    # Set a sudo password if requested
    password = None
    if args.sudo_password_prompt:
        password = getpass.getpass(prompt='sudo Password: ')
        env.password = password

    system_files = args.system_files if args.system_files else SYSTEM_FILES
    system_files_map = dict()
    for full_path in system_files:
        if len(full_path.split('/')) > 1:
            system_files_map[basename(full_path)] = full_path
    hosts = args.hosts if args.hosts \
        else read_hosts(args.hosts_file)
    # Configure parallelism, or if the environment
    # goes unchanged, tasks will run serialized
    if args.parallel_workers > 1:
        env.parallel = True
        env.pool_size = args.parallel_workers
    env.hosts = hosts
    if args.subcommand == 'purge':
        proceed = raw_input('Are you absolutely sure you wish to purge ' + \
            'this directory: {0}? (yes/no): '.format(args.archive_directory))
        if proceed != 'yes':
            print(yellow('{0}: Directory {1} was not removed.'.\
                         format(env.host_string, args.archive_directory)))
            return 1
    hide_output = 'everything' if not args.verbose else 'user'
    # fab tasks need to be called with execute, or env settings
    # will not be used.
    with hide(hide_output):
        if args.subcommand == 'archive':
            execute(archive_files, system_files, args.archive_directory)
        elif args.subcommand == 'purge':
            execute(purge, args.archive_directory)
        elif args.subcommand == 'report':
            output = execute(find_archived_files, args.archive_directory)
            archive_data = get_archive_data(output)
            print(generate_report(archive_data))
        elif args.subcommand == 'diff':
            execute(diff_files, system_files_map, args.date_first,
                    args.date_second, args.archive_directory)
        elif args.subcommand == 'recover':
            execute(recover_files, system_files_map, args.recover_date,
                    args.archive_directory, args.dry_run)
            if args.post_recover_command:
                execute(post_recover_command, args.post_recover_command,
                        args.dry_run)
    # Clean up any fabric connections still open.
    disconnect_all()



def read_hosts(hosts_file):
    """
    Read in list of hosts.
    """
    with open(hosts_file, 'r') as hosts_file:
        return [hv.rstrip('\n') for hv in hosts_file if len(hv.rstrip('\n')) > 0]


def parse_arguments():
    """
    Collect command-line arguments.
    """
    parser = argparse.ArgumentParser(prog='flashback',
                                     description='Roll-back changes ' + \
                                     'in a flash. ' + \
                                     'Perform archiving, recovery and ' + \
                                     'reporting for *small* system and ' + \
                                     'configuration files.  Can be a bit ' + \
                                     'slow to execute if used in ' + \
                                     'a way that opens up large numbers ' + \
                                     'of concurrent ssh connections')
    subparsers = parser.add_subparsers(dest='subcommand',
                                       help='Sub-command help')

    parser_common = subparsers.add_parser('common', add_help=False)
    parser_common.add_argument('--verbose', '-v', action='store_true',
                               dest='verbose', default=False,
                               help='Turn on verbose fabric output.')
    host_group = parser_common.add_mutually_exclusive_group(required=True)
    host_group.add_argument('--host', '-H', action='append',
                            dest='hosts', metavar='hostname',
                            help='Hostname for host where we wish to ' + \
                            'archive files or perform reporting')
    host_group.add_argument('--hosts-file', '-f', action='store',
                            dest='hosts_file', metavar='FILE',
                            help='Text file containing a list of hosts, ' + \
                            'one per line. Ignored if --host is specified')
    parser_common.add_argument('--system-file', '-F', action='append',
                               dest='system_files', metavar='FULLPATH',
                               help='Full path for ' + \
                               'system files to perform operations on. ' + \
                               'Does not apply when used with the purge ' + \
                               'subcommand (purge removes the entire ' + \
                               'directory).  Defaults to {0}'.\
                               format(', '.join(SYSTEM_FILES)))
    parser_common.add_argument('--archive-directory', '-D', action='store',
                               dest='archive_directory', metavar='N',
                               default=ARCHIVE_DIRECTORY,
                               help='The directory where archived system ' + \
                               'and configuration files reside. ' + \
                               'Defaults to {0}'.format(ARCHIVE_DIRECTORY))
    parser_common.add_argument('--parallel-workers', '-w', action='store',
                               dest='parallel_workers', metavar='N',
                               default=DEFAULT_WORKERS, type=int,
                               help='Number of concurrent connections, ' + \
                               'set to 1 to serialize.  Defaults to ' + \
                               '{0}'.format(DEFAULT_WORKERS))
    parser_common.add_argument('--sudo-password-prompt', '-p',
                               action='store_true', default=False,
                               dest='sudo_password_prompt',
                               help='Prompt for a password if required ' + \
                               'for sudo command execution. ')
    subparsers.add_parser('archive', parents=[parser_common],
                          conflict_handler='resolve',
                          help='Archive system files')
    parser_diff = subparsers.add_parser('diff', parents=[parser_common],
                                        conflict_handler='resolve',
                                        help='Diff files for two dates, ' + \
                                        'the current and most recent ' + \
                                        'archives are used by default')
    parser_diff.add_argument('--date-first', '-a', action='store',
                             metavar='YYYYMMDD', dest='date_first', default=0,
                             help="Date to perform comparison, defaults ' + \
                             'to today's date, such as earlier today",
                             type=int)
    parser_diff.add_argument('--date-second', '-b', action='store',
                             metavar='YYYYMMDD', dest='date_second',
                             default=1, help='Date to perform ' + \
                             'comparison, defaults to the live copy if ' + \
                             'unspecified', type=int)
    subparsers.add_parser('purge', parents=[parser_common],
                          conflict_handler='resolve',
                          help='Purge all archived files')
    parser_recover = subparsers.add_parser('recover', parents=[parser_common],
                                           conflict_handler='resolve',
                                           help='Recover an archived copy ' + \
                                           'for the specified file(s). ' + \
                                           'Defaults to today if a ' + \
                                           'YYYYMMDD date is not specified.')
    parser_recover.add_argument('--recover-date', '-r', action='store',
                                metavar='YYYYMMDD', dest='recover_date',
                                default=0, type=int, help='Date to ' + \
                                'recover from if the file exists, ' + \
                                "defaults to today's date, such as " + \
                                'earlier today')
    parser_recover.add_argument('--post-recover-command', '-c',
                                action='store', metavar='COMMAND',
                                dest='post_recover_command',
                                help='A quoted command to execute with ' + \
                                'sudo after file recovery, such as ' + \
                                '"service nginx restart"')
    parser_recover.add_argument('--dry-run', '-n', action='store_true',
                                dest='dry_run', default=False,
                                help="Don't actually recover files")
    subparsers.add_parser('report', parents=[parser_common],
                          conflict_handler='resolve',
                          help='Summarized reporting of ' + \
                          'archived system files')

    # sphinx is not add_help=False aware...
    del subparsers.choices['common']

    return parser


if __name__ == '__main__':
    sys.exit(main())
