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
import shutil
import pytest

from click.testing import CliRunner

from fileconfig.api import logger
from fileconfig.main import app
from fileconfig.api import writer
from fileconfig.api import constants


@pytest.fixture(params=constants.SUPPORTED_FORMATS)
def configurer(request):

    class Configurer(object):

        def __init__(self, _request):
            super(Configurer, self).__init__()
            self._request = _request
            self._runner = CliRunner()
            self.log = logger.get_logger('fileconfig.tests.cli.configurer')

        def run(self, command, catch_exceptions=False):

            command = 'fileconfig configurer --alias {0} {1}'.format(request.node.name, command)
            self.log.info('Invoking command: {0}'.format(command))

            return self._runner.invoke(app, command.split(' ')[1:],
                                       catch_exceptions=catch_exceptions)

        @property
        def request(self):
            return self._request

    # change the home directory so that the test
    # wont pollute it.
    tempdir = tempfile.mkdtemp()
    os.environ['HOME'] = tempdir

    # change the cwd to run in an isolated environment
    os.chdir(tempdir)

    # create the file we intent to alias
    fmt = request.param
    writer.dump(obj={}, file_path=request.node.name, fmt=fmt)
    CliRunner().invoke(app, 'fileconfig repository add --alias {0} --file-path {1} --fmt {2}'
                       .format(request.node.name, request.node.name, fmt).split(' ')[1:],
                       catch_exceptions=False)

    yield Configurer(request)

    # cleanup
    shutil.rmtree(tempdir)


@pytest.fixture()
def temp_file():

    file_path = tempfile.mkstemp()[1]

    yield file_path

    # cleanup
    os.remove(file_path)
