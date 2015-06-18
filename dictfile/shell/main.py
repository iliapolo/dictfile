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

import logging
import sys
import os

import click

from dictfile.api import logger
from dictfile.api.patcher import Patcher
from dictfile.api import parser
from dictfile.api import exceptions
from dictfile.api.repository import Repository
from dictfile.shell.commands import configure as configurer_group
from dictfile.shell.commands import repository as repository_group
from dictfile.shell import solutions, handle_exceptions, causes
from dictfile.api.constants import PROGRAM_NAME


# pylint: disable=no-value-for-parameter
@click.group()
@click.option('--debug', is_flag=True)
@click.pass_context
@handle_exceptions
def app(ctx, debug):

    if debug:
        logger.setup_loggers(level=logging.DEBUG)

    # initialize the repository object
    repo = Repository(os.path.join(os.path.expanduser('~'), '.{0}'.format(PROGRAM_NAME)))
    ctx.repo = repo


@click.group()
@click.pass_context
@click.argument('alias', required=True)
@handle_exceptions
def configure(ctx, alias):

    repo = ctx.parent.repo

    file_path = repo.path(alias)

    try:
        parsed = parser.load(file_path=file_path, fmt=repo.fmt(alias))
    except exceptions.CorruptFileException as e:
        e.cause = causes.EDITED_MANUALLY
        e.possible_solutions = [solutions.edit_manually(), solutions.reset_to_latest(alias)]
        raise

    # detect if the file was manually edited since the last command.
    # if so, warn because it means the current version of the file is not
    # under version control and will be lost after the change
    latest = parser.loads(repo.contents(alias=alias, version='latest'), fmt=repo.fmt(alias))
    if latest != parsed:

        exception = click.ClickException(message='Cannot perform operation')
        exception.cause = causes.DIFFER_FROM_LATEST
        exception.possible_solutions = [solutions.reset_to_latest(alias), solutions.commit(alias)]
        raise exception

    patcher = Patcher(parsed)
    ctx.patcher = patcher


@click.group()
def repository():
    pass


configure.add_command(configurer_group.put)
configure.add_command(configurer_group.add)
configure.add_command(configurer_group.delete)
configure.add_command(configurer_group.remove)
configure.add_command(configurer_group.get)

repository.add_command(repository_group.show)
repository.add_command(repository_group.revisions)
repository.add_command(repository_group.files)
repository.add_command(repository_group.reset)
repository.add_command(repository_group.add)
repository.add_command(repository_group.remove)
repository.add_command(repository_group.commit)

app.add_command(repository)
app.add_command(configure)

# allows running the application as a single executable
# created by pyinstaller
if getattr(sys, 'frozen', False):
    app(sys.argv[1:])
