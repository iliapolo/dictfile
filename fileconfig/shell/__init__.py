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

from fileconfig.api import exceptions


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

        func(*args, **kwargs)

        ctx.parent.parent.repo.commit(alias)

    return wrapper


def handle_exceptions(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        try:
            func(*args, **kwargs)
        except exceptions.VersionNotFoundException as e:
            raise click.ClickException(str(e))
        except exceptions.AliasNotFoundException as e:
            raise click.ClickException(str(e))
        except exceptions.InvalidValueTypeException as e:
            raise click.ClickException(str(e))
        except exceptions.KeyNotFoundException as e:
            raise click.ClickException(str(e))
        except exceptions.UnsupportedOperationException as e:
            raise click.ClickException(str(e))

    return wrapper
