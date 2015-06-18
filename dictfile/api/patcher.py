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

import six
import flatdict

from dictfile.api import exceptions
from dictfile.api import parser
from dictfile.api import writer
from dictfile.api import constants
from dictfile.api import logger


class Patcher(object):

    """Class for patching dictionaries using strings values.

    This patcher is a thin wrapper around the standard dict operations.
    The main difference is that values given to this patcher must be only strings.
    Values retrieved are also strings, serialized using the json format.

    The patcher provides a 'fluent' api for easily performing multiple mutations.
    To retrieve the underlying dictionary after mutations, use the 'finish' method.
    For example:

        patcher = Patcher({'key1': 'value1', 'key2':'value2'})
        patched = patcher.set('key1', 'value3')
                         .set('key2', 'value2')
                         .finish()

    The following holds for all methods accepting a 'key' and 'value' argument.
    Keys are specified as strings (obviously), in order to access nested values you can specify
    nested keys like so:

        patcher = Patcher({'key1': {'key2': 'value1'}})
        value = patcher.get('key1:key2')

        (value will be 'value1')

    Remember that returned values are always strings. For example:

        patcher = Patcher({'key1': {'key2': 'value1'}})
        value = patcher.get('key1')

        (value will be '{"key2": "value2"}')

    Values are also restricted to strings. The patcher will take care of any type conversion
    necessary. That is:

        - '5' --> 5 (int)
        - '5.5' --> 5.5 (float)
        - 'value1' --> 'value1' (str)
        - '{"key1": "value1"}' --> {'key1': 'value1'} (dict)
        - '["value1", "value2"] --> ['value1', 'value2'] (list)

    """

    _fdict = {}
    _logger = None

    def __init__(self, dictionary):

        """Instantiate a Patcher instance.

        Args:

            dictionary (dict): The dictionary to patch.

        """

        self._fdict = flatdict.FlatDict(dictionary)
        self._logger = logger.get_logger('{0}.api.patcher.Patcher'.format(constants.PROGRAM_NAME))

    def set(self, key, value):

        """Add/Modify a key with the given value.

        Args:

            key (str): The key to operate on.
            value (str, unicode): The value of the key.

        Returns:

            The patcher instance itself, for fluent api support.

        """

        self._fdict[str(key)] = self._deserialize(value)
        return self

    def add(self, key, value):

        self._validate_list(key)
        current_value = self._fdict[key]

        current_value.append(self._deserialize(value))

        return self

    def remove(self, key, value):

        self._validate_list(key)
        current_value = self._fdict[key]

        current_value.remove(self._deserialize(value))

        return self

    def delete(self, key):

        try:
            del self._fdict[str(key)]
        except KeyError:
            raise exceptions.KeyNotFoundException(key=key)

        return self

    def get(self, key, fmt=constants.JSON):

        try:
            self._logger.debug('Fetching value for key {0}'.format(key))
            value = self._fdict[key]
            return self._serialize(value, fmt)
        except KeyError:
            raise exceptions.KeyNotFoundException(key=key)

    def finish(self):
        return self._fdict.as_dict()

    def _serialize(self, value, fmt):

        self._logger.debug('Serializing value ({0}): {1}'.format(type(value), value))

        if isinstance(value, flatdict.FlatDict):
            value = value.as_dict()

        if isinstance(value, (dict, list, set)):
            if fmt == constants.INI:
                # an ini dictionary is actually
                # a properties file, not an ini
                fmt = constants.PROPERTIES
            value = writer.dumps(value, fmt=fmt)

        return str(value)

    def _deserialize(self, value):

        if not isinstance(value, six.string_types):
            raise exceptions.InvalidValueTypeException(expected_types=six.string_types,
                                                       actual_type=type(value))

        # this is not in-lined because it easier to debug
        # this way. note that if the value is a primitive, yaml
        # will return the correct type as well.
        self._logger.debug('De-serializing value: {0}'.format(value))
        parsed = parser.loads(string=value, fmt=constants.YAML)
        return parsed

    def _validate_list(self, key):

        value = self._fdict[key]
        if not isinstance(value, list):
            raise exceptions.InvalidKeyTypeException(
                key=key,
                expected_types=[list],
                actual_type=type(value))
