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

import unittest

from fileconfig.api import parser
from fileconfig.tests.resources import get_resource


class ParserTest(unittest.TestCase):

    def test_parse_properties(self):

        resource = 'test_parse_properties.properties'

        with open(get_resource(resource)) as stream:

            sproperties = stream.read()

        parsed = parser.parse_properties(sproperties)

        self.assertDictEqual(
            {
                'key1': 'value1',
                'key2': 'value2',
                'key3': 'value3    ',
                'key4': 'first, second, third'
            }, parsed)

    def test_parse_json(self):

        resource = 'test_parse_json.json'

        with open(get_resource(resource)) as stream:

            sjson = stream.read()

        parsed = parser.parse_json(sjson)

        self.assertDictEqual(
            {
                'key1': 'value1',
                '   key2': '  value2  '
            }, parsed)

    def test_parse_yaml(self):

        resource = 'test_parse_yaml.yaml'

        with open(get_resource(resource)) as stream:

            syaml = stream.read()

        parsed = parser.parse_yaml(syaml)

        self.assertDictEqual(
            {
                'key1': 'value1',
                'key2': {
                    'a': 'test1',
                    'b': 'test2'
                }
            }, parsed)
