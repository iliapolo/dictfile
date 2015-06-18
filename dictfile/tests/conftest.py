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

import os
import tempfile

import pytest

from dictfile.api import utils
from dictfile.tests.shell.commands import Runner


BINARY = 'binary'
SOURCE = 'source'


@pytest.fixture(name='temp_file')
def _temp_file(request, temp_dir):

    name = request.node.name

    file_path = os.path.join(temp_dir, name)

    with open(file_path, 'w') as stream:
        stream.write('')

    yield file_path


@pytest.fixture(name='temp_dir')
def _temp_dir():

    dir_path = tempfile.mkdtemp()

    try:
        yield dir_path
    finally:
        utils.rmf(dir_path)


@pytest.fixture(name='home_dir')
def _home_dir():

    homedir = tempfile.mkdtemp()
    os.environ['HOME'] = homedir

    try:
        yield homedir
    finally:
        utils.rmf(homedir)


@pytest.fixture(name='repo_path', scope='session')
def _repo_path():
    import dictfile
    return os.path.abspath(os.path.join(dictfile.__file__, os.pardir, os.pardir))


@pytest.fixture(name='runner', scope='session', params=[SOURCE, BINARY])
def _runner(request, repo_path):

    return Runner(request.param, repo_path)
