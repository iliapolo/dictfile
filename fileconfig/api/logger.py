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

import coloredlogger


class Logger(object):

    _logger = None

    def __init__(self, name=None):
        self._logger = coloredlogger.get_logger(name)

    def info(self, message):
        self._logger.info(message)

    def warning(self, message):
        self._logger.wtf(message)

    def warn(self, message):
        self.warning(message)

    def error(self, message):
        self._logger.error(message)

    def debug(self, message):
        self._logger.verbose(message)


def get_logger(name):
    return Logger(name)
