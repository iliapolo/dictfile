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

from functools import wraps

import click

from dictfile.api import writer
from dictfile.api import constants
from dictfile.api import exceptions
from dictfile.shell import handle_exceptions


def commit(func):

    def _lookup_context(*args):

        for arg in args:
            if isinstance(arg, click.core.Context):
                return arg

        return None

    @wraps(func)
    def wrapper(*args, **kwargs):

        ctx = _lookup_context(*args)

        alias = ctx.parent.params['alias']
        message = kwargs['message']
        del kwargs['message']

        func(*args, **kwargs)

        ctx.parent.parent.repo.commit(alias, message)

    return wrapper


@click.command()
@click.option('--key', required=True)
@click.option('--value', required=True)
@click.option('--message', required=False)
@click.pass_context
@handle_exceptions
@commit
def put(ctx, key, value):

    """
    Modify/add a key with the given value.

    """

    alias = ctx.parent.params['alias']

    fmt = ctx.parent.parent.repo.fmt(alias)

    if fmt not in constants.COMPOUND_FORMATS:
        if ':' in key and fmt == constants.PROPERTIES:
            raise exceptions.UnsupportedOperationException(fmt=fmt,
                                                           operation='put with complex keys')
        if value.startswith('{') and value.endswith('}'):
            raise exceptions.UnsupportedOperationException(fmt=fmt,
                                                           operation='put with complex values')

        if value.startswith('[') and value.endswith(']'):
            raise exceptions.UnsupportedOperationException(fmt=fmt,
                                                           operation='put with complex values')

    patched = ctx.parent.patcher.set(key=key, value=value).finish()

    write_result(patched, ctx)


@click.command()
@click.option('--key', required=True)
@click.option('--value', required=True)
@click.option('--message', required=False)
@click.pass_context
@handle_exceptions
@commit
def add(ctx, key, value):

    """
    Add a value to an existing key.

    """

    alias = ctx.parent.params['alias']

    fmt = ctx.parent.parent.repo.fmt(alias)

    if fmt not in constants.COMPOUND_FORMATS:
        raise exceptions.UnsupportedOperationException(fmt=fmt, operation='add')

    patched = ctx.parent.patcher.add(key=key, value=value).finish()

    write_result(patched, ctx)

    click.echo(ctx.parent.patcher.get(key, fmt=fmt))


@click.command()
@click.option('--key', required=True)
@click.option('--message', required=False)
@click.pass_context
@handle_exceptions
@commit
def delete(ctx, key):

    """
    Delete a key.

    """

    alias = ctx.parent.params['alias']

    fmt = ctx.parent.parent.repo.fmt(alias)

    if fmt in [constants.PROPERTIES] and ':' in key:
        raise exceptions.UnsupportedOperationException(fmt=fmt,
                                                       operation='delete with complex keys')

    value = ctx.parent.patcher.get(key=key, fmt=fmt)

    patched = ctx.parent.patcher.delete(key=key).finish()

    write_result(patched, ctx)

    click.echo(value)


@click.command()
@click.option('--key', required=True)
@click.pass_context
@handle_exceptions
def get(ctx, key):

    """
    Retrieve a key.

    """

    alias = ctx.parent.params['alias']

    fmt = ctx.parent.parent.repo.fmt(alias)

    if fmt in [constants.PROPERTIES] and ':' in key:
        raise exceptions.UnsupportedOperationException(fmt=fmt,
                                                       operation='get with complex keys')

    value = ctx.parent.patcher.get(key, fmt=fmt)

    click.echo(value)


@click.command()
@click.option('--key', required=True)
@click.option('--value', required=True)
@click.option('--message', required=False)
@click.pass_context
@handle_exceptions
@commit
def remove(ctx, key, value):

    """
    Remove a value from a specific key.

    """

    alias = ctx.parent.params['alias']

    fmt = ctx.parent.parent.repo.fmt(alias)

    if fmt not in constants.COMPOUND_FORMATS:
        raise exceptions.UnsupportedOperationException(fmt=fmt, operation='remove')

    patched = ctx.parent.patcher.remove(key=key, value=value).finish()

    write_result(patched, ctx)

    click.echo(ctx.parent.patcher.get(key, fmt=fmt))


def write_result(result, ctx):

    alias = ctx.parent.params['alias']

    file_path = ctx.parent.parent.repo.path(alias)
    fmt = ctx.parent.parent.repo.fmt(alias)

    writer.dump(obj=result, file_path=file_path, fmt=fmt)
