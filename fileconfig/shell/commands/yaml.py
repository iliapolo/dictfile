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

from fileconfig.api import writer
from fileconfig.shell import commit
from fileconfig.shell import handle_exceptions


@click.command()
@click.option('--key', required=True)
@click.option('--value', required=True)
@click.pass_context
@handle_exceptions
@commit
def put(ctx, key, value):

    patched = ctx.parent.patcher.set(key=key, value=value).finish()

    writer.write_yaml(patched, ctx.parent.params['filename'])


@click.command()
@click.option('--key', required=True)
@click.option('--value', required=True)
@click.pass_context
@handle_exceptions
@commit
def add(ctx, key, value):

    patched = ctx.parent.patcher.add(key=key, value=value).finish()

    writer.write_yaml(patched, ctx.parent.params['filename'])


@click.command()
@click.option('--key', required=True)
@click.pass_context
@handle_exceptions
@commit
def delete(ctx, key):

    patched = ctx.parent.patcher.delete(key=key).finish()

    writer.write_yaml(patched, ctx.parent.params['filename'])


@click.command()
@click.option('--key', required=True)
@click.pass_context
@handle_exceptions
def get(ctx, key):

    value = ctx.parent.patcher.get(key)

    if isinstance(value, dict) or isinstance(value, list) or isinstance(value, set):
        click.echo(writer.get_yaml_string(value))
    else:
        click.echo(value)
