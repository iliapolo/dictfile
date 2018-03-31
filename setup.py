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


setup(
    name='fileconfig',
    version='0.1',
    author='Eli Polonsky',
    author_email='eli.polonsky@gmail.com',
    packages=[
        'fileconfig',
        'fileconfig.api',
        'fileconfig.shell',
        'fileconfig.shell.commands',
    ],
    license='LICENSE',
    description="Command Line Interface for manipulating configuration files",
    entry_points={
        'console_scripts': [
            'fileconfig = fileconfig.main:main'
        ]
    },
    install_requires=[
        'click==6.7',
        'javaproperties==0.4.0',
        'prettytable==0.7.2',
        'pyyaml==3.12',
        'flatdict==3.0.0',
        'coloredlogger==1.3.12'
    ]
)