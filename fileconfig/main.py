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
from fileconfig.shell.commands import properties as properties_group
from fileconfig.shell.commands import json as json_group
from fileconfig.shell.commands import yaml as yaml_group
from fileconfig.shell.commands import repository as repository_group


@click.group()
@click.pass_context
@handle_exceptions
def app(ctx):

    # initialize the repository object
    repo = Repository('{0}/.fileconfig/repo'.format(os.path.expanduser('~')))
    repo.init()
    ctx.repo = repo


@click.group()
@click.pass_context
@click.option('--filename', required=True)
def properties(ctx, filename):

    with open(filename) as f:
        sproperties = f.read()

    parsed = parser.parse_properties(sproperties)
    patcher = Patcher(parsed)
    ctx.patcher = patcher


@click.group()
@click.pass_context
@click.option('--filename', required=True)
def yaml(ctx, filename):

    with open(filename) as f:
        syaml = f.read()

    parsed = parser.parse_yaml(syaml)
    patcher = Patcher(parsed)
    ctx.patcher = patcher


@click.group()
@click.pass_context
@click.option('--filename', required=True)
def json(ctx, filename):

    with open(filename) as f:
        sjson = f.read()

    parsed = parser.parse_json(sjson)
    patcher = Patcher(parsed)
    ctx.patcher = patcher


@click.group()
def repository():
    pass


properties.add_command(properties_group.put)
properties.add_command(properties_group.delete)
properties.add_command(properties_group.get)

json.add_command(json_group.put)
json.add_command(json_group.add)
json.add_command(json_group.delete)
json.add_command(json_group.remove)
json.add_command(json_group.get)

yaml.add_command(yaml_group.put)
yaml.add_command(yaml_group.add)
yaml.add_command(yaml_group.delete)
yaml.add_command(yaml_group.get)

repository.add_command(repository_group.show)
repository.add_command(repository_group.revisions)
repository.add_command(repository_group.files)
repository.add_command(repository_group.reset)

app.add_command(properties)
app.add_command(repository)
app.add_command(json)
app.add_command(yaml)

if getattr(sys, 'frozen', False):
    app(sys.argv[1:])