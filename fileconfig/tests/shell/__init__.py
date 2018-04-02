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


import os
import tempfile
import shutil
import unittest

from click.testing import CliRunner

from fileconfig.api import logger
from fileconfig.main import app


class BaseCommandLineTest(unittest.TestCase):

    _working_dir = None

    # noinspection PyPep8Naming
    def __init__(self, methodName='runTest'):
        super(BaseCommandLineTest, self).__init__(methodName)
        self.log = logger.get_logger('fileconfig.tests.shell.BaseCommandLineTest')

    def setUp(self):

        self.log.info('Starting --> {0}'.format(self))

        self._working_dir = tempfile.mkdtemp()

        # change the home directory so that the command
        # line wont pollute it.
        os.environ['HOME'] = self._working_dir

        self.log.info('Changing directory to isolated filesystem: {0}'.format(self._working_dir))
        os.chdir(self._working_dir)

    def tearDown(self):

        try:
            self.log.info('Deleting directory: {0}'.format(self._working_dir))
            shutil.rmtree(self._working_dir)
        except (OSError, IOError):
            pass

        self.log.info('Finished --> {0}'.format(self))

    def invoke(self, command):

        runner = CliRunner()

        self.log.info('Invoking command: {0}'.format(command))
        return runner.invoke(app, command.split(' ')[1:])
