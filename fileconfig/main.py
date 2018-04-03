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

import sys
import click
import os

from fileconfig.api.patcher import Patcher
from fileconfig.api import parser
from fileconfig.api.repository import Repository
from fileconfig.shell import handle_exceptions
from fileconfig.shell.commands import configurer as configurer_group
from fileconfig.shell.commands import repository as repository_group


@click.group()
@click.pass_context
@handle_exceptions
def app(ctx):

    # initialize the repository object
    repo = Repository('{0}/.fileconfig/repo'.format(os.path.expanduser('~')))
    ctx.repo = repo


@click.group()
@click.pass_context
@click.option('--alias', required=True)
def configurer(ctx, alias):

    repo = ctx.parent.repo

    file_path = repo.path(alias)

    with open(file_path) as f:
        string = f.read()

    parsed = parser.parse(string=string, fmt=repo.fmt(alias))
    patcher = Patcher(parsed)
    ctx.patcher = patcher


@click.group()
def repository():
    pass


configurer.add_command(configurer_group.put)
configurer.add_command(configurer_group.add)
configurer.add_command(configurer_group.delete)
configurer.add_command(configurer_group.remove)
configurer.add_command(configurer_group.get)

repository.add_command(repository_group.show)
repository.add_command(repository_group.revisions)
repository.add_command(repository_group.files)
repository.add_command(repository_group.reset)
repository.add_command(repository_group.add)

app.add_command(repository)
app.add_command(configurer)

# allows running the application as a single executable
# created by pyinstaller
if getattr(sys, 'frozen', False):
    app(sys.argv[1:])
