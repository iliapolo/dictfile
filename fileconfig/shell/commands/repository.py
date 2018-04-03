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

import datetime

import click
from prettytable import PrettyTable

from fileconfig.shell import handle_exceptions


@click.command()
@click.option('--alias', required=True)
@click.option('--file-path', required=True)
@click.option('--fmt', 'fmt', required=True)
@click.pass_context
@handle_exceptions
def add(ctx, alias, file_path, fmt):

    ctx.parent.parent.repo.add(alias=alias, file_path=file_path, fmt=fmt)


@click.command()
@click.option('--alias', required=True)
@click.option('--version', required=True)
@click.pass_context
@handle_exceptions
def show(ctx, alias, version):

    repo = ctx.parent.parent.repo

    click.echo(repo.contents(alias, version))


@click.command()
@click.option('--alias', required=True)
@click.pass_context
@handle_exceptions
def revisions(ctx, alias):

    repo = ctx.parent.parent.repo

    table = PrettyTable(field_names=['alias', 'path', 'timestamp', 'version'])

    for revision in sorted(repo.revisions(alias), key=lambda rev: rev.version):
        table.add_row([revision.alias,
                       revision.file_path,
                       datetime.datetime.fromtimestamp(revision.timestamp).isoformat(),
                       revision.version])

    click.echo(table.get_string())


@click.command()
@click.pass_context
@handle_exceptions
def files(ctx):

    repo = ctx.parent.parent.repo

    table = PrettyTable(field_names=['alias', 'path', 'format'])

    for f in repo.files():
        table.add_row([f.alias, f.file_path, f.fmt])

    click.echo(table.get_string())


@click.command()
@click.option('--alias', required=True)
@click.option('--version', required=True)
@click.pass_context
@handle_exceptions
def reset(ctx, alias, version):

    repo = ctx.parent.parent.repo

    with open(repo.path(alias), 'w') as f:
        f.write(repo.contents(alias, version))

    repo.commit(alias)
