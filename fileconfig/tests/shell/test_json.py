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

import json

from fileconfig.tests.shell import BaseCommandLineTest


class JsonTest(BaseCommandLineTest):

    def test_put_with_simple_value(self):

        filename = '{0}.json'.format(self._testMethodName)

        with open(filename, 'w') as f:
            f.write('{"key1": "value1"}')

        self.invoke('fileconfig json --filename {0} put --key key1 --value value2'.format(filename))

        with open(filename) as f:
            modified_content = f.read()

        self.assertEqual(modified_content, '''{
  "key1": "value2"
}''')

    def test_put_compound_value(self):

        filename = '{0}.json'.format(self._testMethodName)

        with open(filename, 'w') as f:
            f.write('{"key1": "value1"}')

        self.invoke('fileconfig json --filename {0} put --key key1 --value {{"key2":"value1"}}'.format(filename))

        with open(filename) as f:
            modified_content = f.read()

        self.assertEqual(modified_content, '''{
  "key1": {
    "key2": "value1"
  }
}''')

    def test_put_complex_key_compound_value(self):

        filename = '{0}.json'.format(self._testMethodName)

        with open(filename, 'w') as f:
            f.write(json.dumps({
                'key1': {
                    'key2': 'value1'
                }
            }))

        self.invoke('fileconfig json --filename {0} put --key key1:key2 --value {{"key3":"value2"}}'.format(filename))

        with open(filename) as f:
            modified_content = f.read()

        self.assertEqual(modified_content, '''{
  "key1": {
    "key2": {
      "key3": "value2"
    }
  }
}''')

    def test_delete_complex_key(self):

        filename = '{0}.json'.format(self._testMethodName)

        with open(filename, 'w') as f:
            f.write(json.dumps({
                'key1': {
                    'key2': 'value1',
                    'key3': 'value2'
                }
            }))

        self.invoke('fileconfig json --filename {0} delete --key key1:key3'.format(filename))

        with open(filename) as f:
            modified_content = f.read()

        self.assertEqual(modified_content, '''{
  "key1": {
    "key2": "value1"
  }
}''')

    def test_delete(self):

        filename = '{0}.json'.format(self._testMethodName)

        with open(filename, 'w') as f:
            f.write(json.dumps({
                'key1': 'value1',
                'key2': 'value2'
            }))

        self.invoke('fileconfig json --filename {0} delete --key key1'.format(filename))

        with open(filename) as f:
            modified_content = f.read()

        self.assertEqual(modified_content, '''{
  "key2": "value2"
}''')

    def test_get(self):

        filename = '{0}.json'.format(self._testMethodName)

        with open(filename, 'w') as f:
            f.write(json.dumps({
                'key1': 'value1'
            }))

        result = self.invoke('fileconfig json --filename {0} get --key key1'.format(filename))

        self.assertEqual('value1\n', result.output)

    def test_get_compound_value(self):

        filename = '{0}.json'.format(self._testMethodName)

        with open(filename, 'w') as f:
            f.write(json.dumps({
                'key1': {
                    'key2': 'value1'
                }
            }))

        result = self.invoke('fileconfig json --filename {0} get --key key1'.format(filename))

        self.assertEqual('''{
  "key2": "value1"
}
''', result.output)

    def test_get_complex_key(self):

        filename = '{0}.json'.format(self._testMethodName)

        with open(filename, 'w') as f:
            f.write(json.dumps({
                'key1': {
                    'key2': 'value1'
                }
            }))

        result = self.invoke('fileconfig json --filename {0} get --key key1:key2'.format(filename))

        self.assertEqual('value1\n', result.output)

    def test_add(self):

        filename = '{0}.json'.format(self._testMethodName)

        with open(filename, 'w') as f:
            f.write(json.dumps({
                'key1': ['value1']
            }))

        self.invoke('fileconfig json --filename {0} add --key key1 --value value2'.format(filename))

        with open(filename) as f:
            modified_content = f.read()

        self.assertEqual(modified_content, '''{
  "key1": [
    "value1", 
    "value2"
  ]
}''')

    def test_add_to_complex_key(self):

        filename = '{0}.json'.format(self._testMethodName)

        with open(filename, 'w') as f:
            f.write(json.dumps({
                'key1': {
                    'key2': ['value1']
                }
            }))

        self.invoke('fileconfig json --filename {0} add --key key1:key2 --value value2'.format(filename))

        with open(filename) as f:
            modified_content = f.read()

        self.assertEqual(modified_content, '''{
  "key1": {
    "key2": [
      "value1", 
      "value2"
    ]
  }
}''')

    def test_remove(self):

        filename = '{0}.json'.format(self._testMethodName)

        with open(filename, 'w') as f:
            f.write(json.dumps({
                'key1': ['value1', 'value2']
            }))

        self.invoke('fileconfig json --filename {0} remove --key key1 --value value1'.format(filename))

        with open(filename) as f:
            modified_content = f.read()

        self.assertEqual(modified_content, '''{
  "key1": [
    "value2"
  ]
}''')

    def test_remove_from_complex_key(self):

        filename = '{0}.json'.format(self._testMethodName)

        with open(filename, 'w') as f:
            f.write(json.dumps({
                'key1': {
                    'key2': ['value1', 'value2']
                }
            }))

        self.invoke('fileconfig json --filename {0} remove --key key1:key2 --value value1'.format(filename))

        with open(filename) as f:
            modified_content = f.read()

        self.assertEqual(modified_content, '''{
  "key1": {
    "key2": [
      "value2"
    ]
  }
}''')
