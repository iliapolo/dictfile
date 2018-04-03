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

from fileconfig.api import writer
from fileconfig.api import constants


def read_file(configurer):

    with open(configurer.request.node.name) as stream:
        return stream.read()


def write_file(dictionary, configurer):

    writer.dump(obj=dictionary,
                file_path=configurer.request.node.name,
                fmt=configurer.request.param)


def skip_if_not_compound(configurer):

    if configurer.request.param in [constants.PROPERTIES]:
        pytest.skip('{0} format does not support this'.format(configurer.request.param))


def test_put_with_simple_value(configurer):

    write_file(
        dictionary={
            'key1': 'value1'
        },
        configurer=configurer
    )

    expected = writer.dumps(
        obj={
            'key1': 'value2'
        },
        fmt=configurer.request.param)

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

    expected = writer.dumps(
        obj={
            'key1': 5
        },
        fmt=configurer.request.param)

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

    expected = writer.dumps(
        obj={
            'key1': 5.5
        },
        fmt=configurer.request.param)

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

    fmt = configurer.request.param
    result = configurer.run('put --key key1 --value {"key2":"value1"}', catch_exceptions=True)

    if fmt not in constants.COMPOUND_FORMATS:
        expected = 'Error: Unsupported operation: put with complex values (format={0}) \n'.format(
            fmt)
        actual = result.output
    else:
        expected = writer.dumps(
            obj={
                'key1': {
                    'key2': 'value1'
                }
            },
            fmt=configurer.request.param)
        actual = read_file(configurer=configurer)

    assert expected == actual


def test_put_complex_key_compound_value(configurer):

    fmt = configurer.request.param
    if fmt in constants.COMPOUND_FORMATS:
        write_file(
            dictionary={
                'key1': {
                    'key2': 'value1'
                }
            },
            configurer=configurer)

    result = configurer.run('put --key key1:key2 --value {"key3":"value2"}', catch_exceptions=True)

    if fmt not in constants.COMPOUND_FORMATS:
        expected = 'Error: Unsupported operation: put with complex keys (format={0}) \n'.format(
            fmt)
        actual = result.output
    else:
        expected = writer.dumps(
            obj={
                'key1': {
                    'key2': {
                        'key3': 'value2'
                    }
                }
            },
            fmt=configurer.request.param)
        actual = read_file(configurer=configurer)

    assert expected == actual


def test_delete_complex_key(configurer):

    fmt = configurer.request.param
    if fmt in constants.COMPOUND_FORMATS:
        write_file(
            dictionary={
                'key1': {
                    'key2': 'value1',
                    'key3': 'value2'
                }
            },
            configurer=configurer)

    result = configurer.run('delete --key key1:key3', catch_exceptions=True)

    if fmt not in constants.COMPOUND_FORMATS:
        expected = 'Error: Unsupported operation: delete with complex keys (format={0}) \n'.format(
            fmt)
        actual = result.output
    else:
        expected = writer.dumps(
            obj={
                'key1': {
                    'key2': 'value1'
                }
            },
            fmt=configurer.request.param)
        actual = read_file(configurer=configurer)

    assert expected == actual


def test_delete_non_existing_key(configurer):

    write_file(
        dictionary={
            'key1': 'value1'
        },
        configurer=configurer)

    expected = "Error: Key 'key2' does not exist\n"

    result = configurer.run('delete --key key2', catch_exceptions=True)

    actual = result.output

    assert expected == actual


def test_delete(configurer):

    write_file(
        dictionary={
            'key1': 'value1',
            'key2': 'value2'
        },
        configurer=configurer)

    expected = writer.dumps(
        obj={
            'key2': 'value2'
        },
        fmt=configurer.request.param)

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


def test_get_non_existing_key(configurer):

    write_file(
        dictionary={
            'key1': 'value1'
        },
        configurer=configurer)

    expected = "Error: Key 'key2' does not exist\n"

    result = configurer.run('get --key key2', catch_exceptions=True)

    actual = result.output

    assert expected == actual


def test_get_compound_value(configurer):

    # there is no way to create a file with compound
    # values if the format is not compound, so this test
    # is un-necessary in that case.
    skip_if_not_compound(configurer)

    write_file(
        dictionary={
            'key1': {
                'key2': 'value1'
            }
        },
        configurer=configurer)

    expected = writer.dumps({
        "key2": "value1"
    }, fmt=configurer.request.param) + '\n'

    result = configurer.run('get --key key1')

    actual = result.output

    assert expected == actual


def test_get_complex_key(configurer):

    fmt = configurer.request.param
    if fmt in constants.COMPOUND_FORMATS:
        write_file(
            dictionary={
                'key1': {
                    'key2': 'value1'
                }
            },
            configurer=configurer)

    result = configurer.run('get --key key1:key2', catch_exceptions=True)

    if fmt not in constants.COMPOUND_FORMATS:
        expected = 'Error: Unsupported operation: get with complex keys (format={0}) \n'.format(fmt)
        actual = result.output
    else:
        expected = 'value1\n'
        actual = result.output

    assert expected == actual


def test_add(configurer):

    fmt = configurer.request.param
    if fmt in constants.COMPOUND_FORMATS:
        write_file(
            dictionary={
                'key1': ['value1']
            },
            configurer=configurer)

    result = configurer.run('add --key key1 --value value2', catch_exceptions=True)

    if fmt not in constants.COMPOUND_FORMATS:
        expected = 'Error: Unsupported operation: add (format={0}) \n'.format(fmt)
        actual = result.output
    else:
        expected = writer.dumps(
            obj={
                'key1': ['value1', 'value2']
            },
            fmt=fmt)
        actual = read_file(configurer=configurer)

    assert expected == actual


def test_add_to_complex_key(configurer):

    fmt = configurer.request.param
    if fmt in constants.COMPOUND_FORMATS:
        write_file(
            dictionary={
                'key1': {
                    'key2': ['value1']
                }
            },
            configurer=configurer)

    result = configurer.run('add --key key1:key2 --value value2', catch_exceptions=True)

    if fmt not in constants.COMPOUND_FORMATS:
        expected = 'Error: Unsupported operation: add (format={0}) \n'.format(fmt)
        actual = result.output
    else:
        expected = writer.dumps(
            obj={
                'key1': {
                    'key2': ['value1', 'value2']
                }
            },
            fmt=configurer.request.param)
        actual = read_file(configurer=configurer)

    assert expected == actual


def test_remove(configurer):

    fmt = configurer.request.param
    if fmt in constants.COMPOUND_FORMATS:
        write_file(
            dictionary={
                'key1': ['value1', 'value2']
            },
            configurer=configurer)

    result = configurer.run('remove --key key1 --value value2', catch_exceptions=True)

    if fmt not in constants.COMPOUND_FORMATS:
        expected = 'Error: Unsupported operation: remove (format={0}) \n'.format(fmt)
        actual = result.output
    else:
        expected = writer.dumps(
            obj={
                'key1': ['value1']
            },
            fmt=configurer.request.param)
        actual = read_file(configurer=configurer)

    assert expected == actual


def test_remove_from_complex_key(configurer):

    fmt = configurer.request.param
    if fmt in constants.COMPOUND_FORMATS:
        write_file(
            dictionary={
                'key1': {
                    'key2': ['value1', 'value2']
                }
            },
            configurer=configurer)

    result = configurer.run('remove --key key1:key2 --value value2', catch_exceptions=True)

    if fmt not in constants.COMPOUND_FORMATS:
        expected = 'Error: Unsupported operation: remove (format={0}) \n'.format(fmt)
        actual = result.output
    else:
        expected = writer.dumps(
            obj={
                'key1': {
                    'key2': ['value1']
                }
            },
            fmt=configurer.request.param)
        actual = read_file(configurer=configurer)

    assert expected == actual
