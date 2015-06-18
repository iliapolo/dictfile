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
import traceback
from functools import wraps

import click
import six

from dictfile.api import logger
from dictfile.api import constants


log = logger.get_logger(constants.PROGRAM_NAME)


def handle_exceptions(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        try:
            func(*args, **kwargs)
        except BaseException as e:
            tbio = six.StringIO()
            traceback.print_exc(file=tbio)
            log.debug(tbio.getvalue())
            click.echo('Error: {}'.format(str(e)))
            info = build_info(e)
            if info:
                click.echo(info)
            sys.exit(1)

    return wrapper


def build_info(exception):

    info = ''

    if hasattr(exception, 'cause'):
        info = info + '\n\n' + exception.cause + '.'

    if hasattr(exception, 'possible_solutions'):
        info = info + '\n\nPossible solutions: \n\n' + \
               '\n'.join(['    - ' + solution + '.' for solution in exception.possible_solutions])

    return info
