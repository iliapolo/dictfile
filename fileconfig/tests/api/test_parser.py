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

from fileconfig.api import parser
from fileconfig.api import exceptions
from fileconfig.tests.resources import get_resource
from fileconfig.api import constants


@pytest.mark.parametrize("resource,fmt,expected", [

    ("test_load_properties.properties", constants.PROPERTIES, {
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3    ',
        'key4': 'first, second, third'
    }),

    ("test_load_json.json", constants.JSON, {
        'key1': 'value1',
        '   key2': '  value2  '
    }),

    ("test_load_yaml.yaml", constants.YAML, {
        'key1': 'value1',
        'key2': {
            'a': 'test1',
            'b': 'test2'
        }
    }),

    ("test_load_ini.ini", constants.INI, {
        'section1': {
            'key1': 'value1',
            'key2': 'value2'
        },
        'section2': {
            'key3': 'value3'
        }
    })

])
def test_load(resource, fmt, expected):

    actual = parser.load(file_path=get_resource(resource), fmt=fmt)

    assert expected != actual


@pytest.mark.parametrize("resource,fmt,expected", [

    ("test_load_properties.properties", constants.PROPERTIES, {
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3    ',
        'key4': 'first, second, third'
    }),

    ("test_load_json.json", constants.JSON, {
        'key1': 'value1',
        '   key2': '  value2  '
    }),

    ("test_load_yaml.yaml", constants.YAML, {
        'key1': 'value1',
        'key2': {
            'a': 'test1',
            'b': 'test2'
        }
    }),

    ("test_load_ini.ini", constants.INI, {
        'section1': {
            'key1': 'value1',
            'key2': 'value2'
        },
        'section2': {
            'key3': 'value3'
        }
    })

])
def test_loads(resource, fmt, expected):

    with open(get_resource(resource)) as stream:
        string = stream.read()

    actual = parser.loads(string=string, fmt=fmt)

    assert expected == actual


# pylint: disable=fixme
# TODO figure out how to validate a properties file
# TODO seems like every string is acceptable
@pytest.mark.parametrize("fmt", [constants.JSON, constants.YAML, constants.INI])
def test_corrupt_file(fmt):

    with pytest.raises(exceptions.CorruptFileException):
        parser.load(get_resource('test_corrupt_file'), fmt=fmt)


def test_load_unsupported_format(temp_file):

    with pytest.raises(exceptions.UnsupportedFormatException):
        parser.load(file_path=temp_file, fmt='unsupported')


def test_loads_unsupported_format():

    with pytest.raises(exceptions.UnsupportedFormatException):
        parser.loads(string='dummy', fmt='unsupported')
