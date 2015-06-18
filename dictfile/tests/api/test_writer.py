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

import pytest

from dictfile.api import writer
from dictfile.api import constants
from dictfile.api import exceptions


def test_dump_unsupported_format():

    with pytest.raises(exceptions.UnsupportedFormatException):
        writer.dump(obj={}, fmt='unsupported', file_path='dummy')


def test_dumps_unsupported_format():

    with pytest.raises(exceptions.UnsupportedFormatException):
        writer.dumps({}, fmt='unsupported')


def test_dumps_properties_not_dict():

    with pytest.raises(exceptions.InvalidValueTypeException):
        writer.dumps([], fmt=constants.PROPERTIES)


def test_dumps_properties_key_not_primitive():

    with pytest.raises(exceptions.InvalidValueTypeException):
        writer.dumps({'key1': ['value1', 'value2']}, fmt=constants.PROPERTIES)
