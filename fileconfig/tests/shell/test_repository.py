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


class RepositoryTest(BaseCommandLineTest):

    def test_show(self):

        filename = '{0}.properties'.format(self._testMethodName)

        with open(filename, 'w') as f:
            f.write('key=value')

        self.invoke('fileconfig properties --filename {0} update --key key --value changed_value'.format(filename))

        self.invoke('fileconfig repository show --filename {0} --version 1'.format(filename))