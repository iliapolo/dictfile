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

import yaml

import flatdict

from fileconfig.api import exceptions
from fileconfig.api import parser


class Patcher(object):

    _fdict = {}

    def __init__(self, pdict):
        self._fdict = flatdict.FlatDict(pdict)

    def set(self, key, value):

        if value.startswith('{') and value.endswith('}'):
            # this is a json. lets convert it
            value = parser.parse_json(value)

        self._fdict[str(key)] = value
        return self

    def add(self, key, value):

        self._validate_list(key)
        current_value = self._fdict[key]

        current_value.append(value)

        return self

    def remove(self, key, value):

        self._validate_list(key)
        current_value = self._fdict[key]

        current_value.remove(value)

        return self

    def delete(self, key):

        try:
            del self._fdict[str(key)]
        except KeyError:
            raise exceptions.KeyNotFoundException(key=key)

        return self

    def get(self, key):

        try:
            value = self._fdict[key]
            if isinstance(value, flatdict.FlatDict):
                return value.as_dict()
            return value
        except KeyError:
            raise exceptions.KeyNotFoundException(key=key)

    def _validate_list(self, key):

        value = self._fdict[key]
        if not isinstance(value, list):
            raise exceptions.InvalidValueTypeException(
                key=key,
                expected_type=list,
                actual_type=type(value))

    def finish(self):
        return self._fdict.as_dict()
