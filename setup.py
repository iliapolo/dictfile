#############################################################################
# Copyright (c) 2018 Eli Polonsky. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   * See the License for the specific language governing permissions and
#   * limitations under the License.
#
#############################################################################


from setuptools import setup


PROGRAM_NAME = 'dictfile'

setup(
    name=PROGRAM_NAME,
    version='0.7.1',
    author='Eli Polonsky',
    author_email='Eli.polonsky@gmail.com',
    packages=[
        PROGRAM_NAME,
        '{0}.api'.format(PROGRAM_NAME),
        '{0}.shell'.format(PROGRAM_NAME),
        '{0}.shell.commands'.format(PROGRAM_NAME),
    ],
    license='LICENSE',
    description="Command Line Interface for manipulating configuration files",
    entry_points={
        'console_scripts': [
            '{0} = {0}.shell.main:app'.format(PROGRAM_NAME)
        ]
    },
    install_requires=[
        'click==6.7',
        'colorama==0.3.9',
        'coloredlogger==1.3.12',
        'flatdict==3.0.0',
        'javaproperties==0.4.0',
        'prettytable==0.7.2',
        'PyYAML==5.4',
        'six==1.11.0',
        'configparser==3.5.0'
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
