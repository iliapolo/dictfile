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

from fileconfig.api.exceptions import ApiException
from fileconfig.shell import build_info


def test_build_info():

    ex = ApiException()
    ex.possible_solutions = ['do this', 'do that']
    ex.cause = 'the cause'

    actual = build_info(ex)

    expected = '''

the cause.

Possible solutions: 

    - do this.
    - do that.'''

    assert expected == actual


def test_build_info_no_cause():

    ex = ApiException()
    ex.possible_solutions = ['do this', 'do that']

    actual = build_info(ex)

    expected = '''

Possible solutions: 

    - do this.
    - do that.'''

    assert expected == actual


def test_build_info_no_possible_solutions():

    ex = ApiException()
    ex.cause = 'the cause'
    actual = build_info(ex)

    expected = '''

the cause.'''

    assert expected == actual
