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

import shlex
import re
import platform
import os
import tempfile

import click
from click.testing import CliRunner
from boltons.cacheutils import cachedproperty
from pyci.api.runner import LocalCommandRunner
from pyci.api.runner import CommandExecutionResponse
from pyci.api.packager import Packager

from dictfile.api import log, constants
from dictfile.api.constants import PROGRAM_NAME
from dictfile.api.repository import Repository
from dictfile.shell.main import app

DEBUG = False


# pylint: disable=too-few-public-methods
class Runner(object):

    def __init__(self, package_type, repo_path):
        super(Runner, self).__init__()
        self._click_runner = CliRunner()
        self._local_runner = LocalCommandRunner()
        self._package_type = package_type
        self._packager = Packager.create(path=repo_path, target_dir=tempfile.mkdtemp())
        self.log = log.get_logger('{0}.tests.shell.commands:Runner'.format(PROGRAM_NAME))

    def run(self, command, catch_exceptions=False, escape=False):

        if DEBUG:
            command = '--debug {}'.format(command)

        if self._package_type == 'binary':
            response = self._run_binary(command=command, escape=escape)
        else:
            response = self._run_source(command=command, escape=escape)

        click.echo(response.std_out)

        if response.return_code != 0 and not catch_exceptions:
            raise click.ClickException(response.std_err)

        return response

    def _run_source(self, command, escape):

        possix = platform.system().lower() != 'windows'

        if possix and escape:
            command = command.replace('"', '\\"')

        args = shlex.split(command, posix=possix)

        self.log.info('Invoking command: {} [cwd={}]'.format(command, os.getcwd()))

        result = self._click_runner.invoke(app, args, catch_exceptions=True)

        exception = result.exception

        return CommandExecutionResponse(command=command,
                                        std_out=result.output,
                                        std_err=str(exception) if exception else None,
                                        return_code=result.exit_code)

    def _run_binary(self, command, escape):

        possix = platform.system().lower() != 'windows'

        if possix and escape:
            command = command.replace('"', '\\"')

        command = '{} {}'.format(self._binary_path, command)

        args = shlex.split(command, posix=possix)

        self.log.info('Invoking command: {}. [cwd={}]'.format(command, os.getcwd()))

        return self._local_runner.run(args, exit_on_failure=False, pipe=True)

    @cachedproperty
    def _binary_path(self):
        self.log.info('Creating binary package... [cwd={}]'.format(os.getcwd()))
        package_path = self._packager.binary()
        self.log.info('Created binary package: {} [cwd={}]'.format(package_path, os.getcwd()))
        return package_path


class CommandLineFixture(object):

    def __init__(self, _request, home_dir):
        super(CommandLineFixture, self).__init__()
        self._request = _request
        self._repo = Repository(os.path.join(home_dir, '.{0}'.format(PROGRAM_NAME)))

    @property
    def repo(self):
        return self._repo

    @property
    def alias(self):
        return self._request.node.name

    @property
    def fmt(self):
        return self._request.param

    def run(self, command, catch_exceptions=False, escape=False):
        raise NotImplementedError()


def get_parse_error(fmt):
    expected_exception_message = 'mapping values are not allowed here'
    if fmt == constants.INI:
        expected_exception_message = 'File contains no section headers'
    return expected_exception_message


# take from https://stackoverflow.com/questions/33560364/python-windows-parsing-command-
# lines-with-shlex?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
# pylint: disable=too-many-branches
def split(command):

    if platform.system().lower() != 'windows':
        re_cmd_lex = r'"((?:\\["\\]|[^"])*)"|' \
                     r"'([^']*)'|(\\.)|(&&?|\|\|?|\d?\>|[<])|([^\s'" \
                     r'"\\&|<>]+)|(\s+)|(.)'
    else:
        re_cmd_lex = r'"((?:""|\\["\\]|[^"])*)"?()|(\\\\(?=\\*")|\\")|(&&?|\|\|' \
                     r'?|\d?>|[<])|([^\s"&|<>]+)|(\s+)|(.)'

    args = []
    accu = None
    for qs, qss, esc, pipe, word, white, fail in re.findall(re_cmd_lex, command):
        if word:
            pass
        elif esc:
            word = esc[1]
        elif white or pipe:
            if accu is not None:
                args.append(accu)
            if pipe:
                args.append(pipe)
            accu = None
            continue
        elif fail:
            raise ValueError("invalid or incomplete shell string")
        elif qs:
            word = qs.replace('\\"', '"').replace('\\\\', '\\')
            if platform == 0:
                word = word.replace('""', '"')
        else:
            word = qss   # may be even empty; must be last

        accu = (accu or '') + word

    if accu is not None:
        args.append(accu)

    return args
