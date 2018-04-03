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

from fileconfig.api import parser
from fileconfig.api import writer


def read_file(configurer):

    with open(configurer.request.node.name) as stream:
        return parser.parse(string=stream.read(), fmt=configurer.request.param)


def write_file(dictionary, configurer):

    writer.write(dictionary=dictionary,
                 file_path=configurer.request.node.name,
                 fmt=configurer.request.param)


def test_put_with_simple_value(configurer):

    write_file(
        dictionary={
            'key1': 'value1'
        },
        configurer=configurer
    )

    expected = {
        'key1': 'value2'
    }

    configurer.run('put --key key1 --value value2')

    actual = read_file(configurer=configurer)

    assert expected == actual


def test_put_with_int_value(configurer):

    write_file(
        dictionary={
            'key1': 'value1'
        },
        configurer=configurer
    )

    expected = {
        'key1': 5
    }

    configurer.run('put --key key1 --value 5')

    actual = read_file(configurer=configurer)

    assert expected == actual


def test_put_with_float_value(configurer):

    write_file(
        dictionary={
            'key1': 'value1'
        },
        configurer=configurer
    )

    expected = {
        'key1': 5.5
    }

    configurer.run('put --key key1 --value 5.5')

    actual = read_file(configurer=configurer)

    assert expected == actual


def test_put_compound_value(configurer):

    write_file(
        dictionary={
            'key1': 'value1'
        },
        configurer=configurer
    )

    expected = {
        'key1': {
            'key2': 'value1'
        }
    }

    configurer.run('put --key key1 --value {"key2":"value1"}')

    actual = read_file(configurer=configurer)

    assert expected == actual


def test_put_complex_key_compound_value(configurer):

    write_file(
        dictionary={
            'key1': {
                'key2': 'value1'
            }
        },
        configurer=configurer)

    expected = {
        'key1': {
            'key2': {
                'key3': 'value2'
            }
        }
    }

    configurer.run('put --key key1:key2 --value {"key3":"value2"}')

    actual = read_file(configurer=configurer)

    assert expected == actual


def test_delete_complex_key(configurer):

    write_file(
        dictionary={
            'key1': {
                'key2': 'value1',
                'key3': 'value2'
            }
        },
        configurer=configurer)

    expected = {
        'key1': {
            'key2': 'value1'
        }
    }

    configurer.run('delete --key key1:key3')

    actual = read_file(configurer=configurer)

    assert expected == actual


def test_delete(configurer):

    write_file(
        dictionary={
            'key1': 'value1',
            'key2': 'value2'
        },
        configurer=configurer)

    expected = {
        'key2': 'value2'
    }

    configurer.run('delete --key key1')

    actual = read_file(configurer=configurer)

    assert expected == actual


def test_get(configurer):

    write_file(
        dictionary={
            'key1': 'value1'
        },
        configurer=configurer)

    expected = 'value1\n'

    result = configurer.run('get --key key1')

    actual = result.output

    assert expected == actual


def test_get_compound_value(configurer):

    write_file(
        dictionary={
            'key1': {
                'key2': 'value1'
            }
        },
        configurer=configurer)

    expected = writer.get_string({
        "key2": "value1"
    }, fmt=configurer.request.param) + '\n'

    result = configurer.run('get --key key1')

    actual = result.output

    assert expected == actual


def test_get_complex_key(configurer):

    write_file(
        dictionary={
            'key1': {
                'key2': 'value1'
            }
        },
        configurer=configurer)

    expected = 'value1\n'

    result = configurer.run('get --key key1:key2')

    actual = result.output

    assert expected == actual


def test_add(configurer):

    write_file(
        dictionary={
            'key1': ['value1']
        },
        configurer=configurer)

    expected = {
        'key1': ['value1', 'value2']
    }

    configurer.run('add --key key1 --value value2')

    actual = read_file(configurer=configurer)

    assert expected == actual


def test_add_to_complex_key(configurer):

    write_file(
        dictionary={
            'key1': {
                'key2': ['value1']
            }
        },
        configurer=configurer)

    expected = {
        'key1': {
            'key2': ['value1', 'value2']
        }
    }

    configurer.run('add --key key1:key2 --value value2')

    actual = read_file(configurer=configurer)

    assert expected == actual


def test_remove(configurer):

    write_file(
        dictionary={
            'key1': ['value1', 'value2']
        },
        configurer=configurer)

    expected = {
        'key1': ['value1']
    }

    configurer.run('remove --key key1 --value value2')

    actual = read_file(configurer=configurer)

    assert expected == actual


def test_remove_from_complex_key(configurer):

    write_file(
        dictionary={
            'key1': {
                'key2': ['value1', 'value2']
            }
        },
        configurer=configurer)

    expected = {
        'key1': {
            'key2': ['value1']
        }
    }

    configurer.run('remove --key key1:key2 --value value2')

    actual = read_file(configurer=configurer)

    assert expected == actual
