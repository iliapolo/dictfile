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

from fileconfig.api.patcher import Patcher
from fileconfig.api import exceptions


class PatcherTest(unittest.TestCase):

    def test_delete(self):

        dictionary = {'key1': 'value1', 'key2': 'value2'}

        expected_dictionary = {'key2': 'value2'}

        patcher = Patcher(dictionary)
        dictionary = patcher.delete('key1').finish()

        self.assertDictEqual(expected_dictionary, dictionary)

    def test_delete_complex_key(self):

        dictionary = {
            'key1': {
                'key2': 'value1',
                'key3': 'value2'
            }
        }

        expected_dictionary = {
            'key1': {
                'key2': 'value1'
            }
        }

        patcher = Patcher(dictionary)
        dictionary = patcher.delete('key1:key3').finish()

        self.assertDictEqual(expected_dictionary, dictionary)

    def test_set(self):

        dictionary = {'key1': 'value1'}

        expected_dictionary = {'key1': 'value2'}

        patcher = Patcher(dictionary)
        dictionary = patcher.set('key1', 'value2').finish()

        self.assertDictEqual(expected_dictionary, dictionary)

    def test_set_compound_value(self):

        dictionary = {'key1': 'value1'}

        expected_dictionary = {
            'key1': {
                'key2': 'value2'
            }}

        patcher = Patcher(dictionary)
        dictionary = patcher.set('key1', '{"key2":"value2"}').finish()

        self.assertDictEqual(expected_dictionary, dictionary)

    def test_set_complex_key_compound_value(self):

        dictionary = {
            'key1': {
                'key2': 'value1'
            }
        }

        expected_dictionary = {
            'key1': {
                'key2': {
                    'key3': 'value2'
                }
            }}

        patcher = Patcher(dictionary)
        dictionary = patcher.set('key1:key2', '{"key3":"value2"}').finish()

        self.assertDictEqual(expected_dictionary, dictionary)

    def test_set_non_existing_one_level_complex_key(self):

        dictionary = {
            'key1': {
                'key2': 'value1'
            }
        }

        expected_dictionary = {
            'key1': {
                'key2': 'value1',
                'key3': 'value2'
            }
        }

        patcher = Patcher(dictionary)
        dictionary = patcher.set('key1:key3', 'value2').finish()

        self.assertDictEqual(expected_dictionary, dictionary)

    def test_set_existing_one_level_complex_key(self):

        dictionary = {
            'key1': {
                'key2': 'value1'
            }
        }

        expected_dictionary = {
            'key1': {
                'key2': 'value2'
            }
        }

        patcher = Patcher(dictionary)
        dictionary = patcher.set('key1:key2', 'value2').finish()

        self.assertDictEqual(expected_dictionary, dictionary)

    def test_set_non_existing_two_level_complex_key(self):

        dictionary = {
            'key1': {
                'key2': {
                    'key3': 'value1'
                }
            }
        }

        expected_dictionary = {
            'key1': {
                'key2': {
                    'key3': 'value1',
                    'key4': 'value2'
                }
            }
        }

        patcher = Patcher(dictionary)
        dictionary = patcher.set('key1:key2:key4', 'value2').finish()

        self.assertDictEqual(expected_dictionary, dictionary)

    def test_set_existing_two_level_complex_key(self):

        dictionary = {
            'key1': {
                'key2': {
                    'key3': 'value1'
                }
            }
        }

        expected_dictionary = {
            'key1': {
                'key2': {
                    'key3': 'value2'
                }
            }
        }

        patcher = Patcher(dictionary)
        dictionary = patcher.set('key1:key2:key3', 'value2').finish()

        self.assertDictEqual(expected_dictionary, dictionary)

    def test_get_existing_two_level_complex_key(self):

        dictionary = {
            'key1': {
                'key2': {
                    'key3': 'value1'
                }
            }
        }

        expected_value = 'value1'

        patcher = Patcher(dictionary)
        value = patcher.get('key1:key2:key3')

        self.assertEqual(expected_value, value)

    def test_get_existing_one_level_complex_key(self):

        dictionary = {
            'key1': {
                'key2': 'value1'
            }
        }

        expected_value = 'value1'

        patcher = Patcher(dictionary)
        value = patcher.get('key1:key2')

        self.assertEqual(expected_value, value)

    def test_get_non_existing_two_level_complex_key(self):

        dictionary = {
            'key1': {
                'key2': {
                    'key3': 'value1'
                }
            }
        }

        patcher = Patcher(dictionary)
        try:
            patcher.get('key1:key2:key4')
            self.fail('Expected a failure due to missing key')
        except exceptions.KeyNotFoundException:
            pass

    def test_delete_non_existing_key(self):

        dictionary = {'key': 'value'}

        patcher = Patcher(dictionary)
        try:
            patcher.delete('non-existing')
            self.fail('Expected a failure when deleting a non-existing key')
        except exceptions.KeyNotFoundException:
            pass

    def test_add(self):

        dictionary = {'key': ['value1']}

        expected_dictionary = {'key': ['value1', 'value2']}

        patcher = Patcher(dictionary)
        patcher.add(key='key', value='value2')

        self.assertDictEqual(expected_dictionary, dictionary)

    def test_add_to_complex_key(self):

        dictionary = {
            'key1': {
                'key2': ['value1']
            }
        }

        expected_dictionary = {
            'key1': {
                'key2': ['value1', 'value2']
            }
        }

        patcher = Patcher(dictionary)
        patcher.add(key='key1:key2', value='value2')

        self.assertDictEqual(expected_dictionary, dictionary)

    def test_add_to_non_list(self):

        dictionary = {'key': 'value1'}

        patcher = Patcher(dictionary)

        try:
            patcher.add(key='key', value='value2')
            self.fail('Expected a failure when adding to a non list value')
        except exceptions.InvalidValueTypeException:
            pass

    def test_remove_from_complex_key(self):

        dictionary = {
            'key1': {
                'key2': ['value1', 'value2']
            }
        }

        expected_dictionary = {
            'key1': {
                'key2': ['value1']
            }
        }

        patcher = Patcher(dictionary)
        patcher.remove(key='key1:key2', value='value2')

        self.assertDictEqual(expected_dictionary, dictionary)

    def test_remove(self):

        dictionary = {
            'key1': ['value1', 'value2']
        }

        expected_dictionary = {
            'key1': ['value1']
        }

        patcher = Patcher(dictionary)
        patcher.remove(key='key1', value='value2')

        self.assertDictEqual(expected_dictionary, dictionary)
