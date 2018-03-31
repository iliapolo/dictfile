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

from fileconfig.api import writer


class WriterTest(unittest.TestCase):

    def test_get_yaml_string(self):

        dictionary = {
            'key1': {
                'key2': 'value2',
                'key3': 'value3'
            }
        }
        expected_yaml = '''key1:
  key2: value2
  key3: value3
'''

        yaml = writer.get_yaml_string(dictionary)

        self.assertEqual(expected_yaml, yaml)
