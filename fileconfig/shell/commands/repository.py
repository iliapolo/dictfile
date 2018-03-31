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

import click
import datetime

from prettytable import PrettyTable

from fileconfig.shell import handle_exceptions


@click.command()
@click.option('--filename', required=True)
@click.option('--version', required=True)
@click.pass_context
@handle_exceptions
def show(ctx, filename, version):

    repo = ctx.parent.parent.repo

    click.echo(repo.contents(filename, version))


@click.command()
@click.option('--filename', required=True)
@click.pass_context
@handle_exceptions
def revisions(ctx, filename):

    repo = ctx.parent.parent.repo

    table = PrettyTable(field_names=['filename', 'timestamp', 'version'])

    for revision in sorted(repo.revisions(filename), key=lambda rev: rev.version):
        table.add_row([revision.filename,
                       datetime.datetime.fromtimestamp(revision.timestamp).isoformat(),
                       revision.version])

    click.echo(table.get_string())


@click.command()
@click.pass_context
@handle_exceptions
def files(ctx):

    repo = ctx.parent.parent.repo

    table = PrettyTable(field_names=['filename'])

    for f in repo.files():
        table.add_row([f])

    click.echo(table.get_string())


@click.command()
@click.option('--filename', required=True)
@click.option('--version', required=True)
@click.pass_context
@handle_exceptions
def reset(ctx, filename, version):

    repo = ctx.parent.parent.repo

    with open(filename, 'w') as f:
        f.write(repo.contents(filename, version))

    repo.commit(filename)
