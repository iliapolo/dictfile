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

import click

from dictfile.api import log


class Logger(object):

    def __init__(self, verbose=False):

        self._indent = 0
        self._last_break_line = True

        self._logger = log.get_logger(name='dictfile')
        self._verbose = verbose

    def set_verbose(self, verbose):
        self._verbose = verbose

    def info(self, message, **kwargs):

        if self._is_debug():
            self._logger.info(message, **kwargs)
        else:
            click.echo('{}{}'.format(message, self._format_key_values(**kwargs)))

    def debug(self, message, **kwargs):

        if self._verbose:
            # in verbose mode debug statements should be printed as well.
            click.echo('{}{}'.format(message, self._format_key_values(**kwargs)))

        self._logger.debug(message, **kwargs)

    def warn(self, message, **kwargs):

        if self._is_debug():
            self._logger.warn(message, **kwargs)
        else:
            click.secho('Warning: {}{}'.format(message, self._format_key_values(**kwargs)),
                        fg='yellow')

    def error(self, message, **kwargs):

        if self._is_debug():
            self._logger.error(message, **kwargs)
        else:
            click.secho('Error: {}{}'.format(message, self._format_key_values(**kwargs)), fg='red')

    @staticmethod
    def _format_key_values(**kwargs):

        if not kwargs:
            return ''

        kvs = []
        for key, value in kwargs.items():
            kvs.append('{}={}'.format(key, value))
        return ' [{}]'.format(', '.join(kvs))

    def _is_debug(self):
        return self._logger.logger.isEnabledFor(logging.DEBUG)


instance = Logger()


def get():
    return instance
