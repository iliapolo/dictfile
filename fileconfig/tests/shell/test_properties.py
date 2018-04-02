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

from fileconfig.tests.shell import BaseCommandLineTest


class PropertiesTest(BaseCommandLineTest):

    def test_put_existing_key(self):

        filename = '{0}.properties'.format(self._testMethodName)

        with open(filename, 'w') as stream:
            stream.write('key1=value1')

        self.invoke('fileconfig properties --filename {0} put --key key1 --value value2'
                    .format(filename))

        with open(filename) as stream:
            modified_content = stream.read()

        self.assertEqual(modified_content, 'key1=value2\n')

    def test_put_non_existing_key(self):

        filename = '{0}.properties'.format(self._testMethodName)

        with open(filename, 'w') as stream:
            stream.write('key1=value1')

        self.invoke('fileconfig properties --filename {0} put --key key2 --value value2'
                    .format(filename))

        with open(filename) as stream:
            modified_content = stream.read()

        self.assertEqual(modified_content, 'key2=value2\nkey1=value1\n')

    def test_delete(self):

        filename = '{0}.properties'.format(self._testMethodName)

        with open(filename, 'w') as stream:
            stream.write('key1=value1\nkey2=value2')

        self.invoke('fileconfig properties --filename {0} delete --key key1'.format(filename))

        with open(filename) as stream:
            modified_content = stream.read()

        self.assertEqual(modified_content, 'key2=value2\n')

    def test_delete_non_existing_key(self):

        filename = '{0}.properties'.format(self._testMethodName)

        with open(filename, 'w') as stream:
            stream.write('key1=value1\nkey2=value2')

        result = self.invoke('fileconfig properties --filename {0} delete --key key3'
                             .format(filename))

        assert result.output == "Error: Key 'key3' does not exist\n"

    def test_get(self):

        filename = '{0}.properties'.format(self._testMethodName)

        with open(filename, 'w') as stream:
            stream.write('key1=value1')

        result = self.invoke('fileconfig properties --filename {0} get --key key1'.format(filename))

        self.assertEqual('value1\n', result.output)
