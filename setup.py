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
"""flashback setup"""

from setuptools import setup, find_packages

execfile('flashback/version.py')

setup(name='flashback',
      version=__version__,
      description='Quickly roll-back configuration changes gone awry, across a fleet of Linux '
                  'instances running sshd.',
      author='zulily, llc',
      author_email='opensource@zulily.com',
      packages=find_packages(),
      url='https://github.com/zulily/flashback',
      license='Apache License, Version 2.0',
      entry_points={
          'console_scripts': [
              'flashback = flashback.scripts.cli:main'
          ]
      },
      install_requires=[
          'fabric',
          'jinja2',
      ],
      #package_data={'flashback': ['templates/*']},
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 2.7',
          'Topic :: System :: Systems Administration',
      ],
)
