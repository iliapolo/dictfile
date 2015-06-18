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

import copy
import os

import click
import pytest

from dictfile.api import constants
from dictfile.api import writer
from dictfile.shell import solutions, causes
from dictfile.tests.shell.commands import CommandLineFixture, get_parse_error


@pytest.fixture(name='configure', params=constants.SUPPORTED_FORMATS)
def conf(request, home_dir, runner):

    class Configure(CommandLineFixture):

        def run(self, command, catch_exceptions=False, escape=False):

            command = 'configure {} {}'.format(self.alias, command)

            return runner.run(command, catch_exceptions=catch_exceptions, escape=escape)

    configure = Configure(request, home_dir)

    # create the file we intent to operate on
    file_path = os.path.join(home_dir, configure.alias)
    writer.dump(obj={},
                file_path=file_path,
                fmt=configure.fmt)

    # add the file to the repository
    runner.run('repository add --alias {} --file-path {} --fmt {}'
               .format(configure.alias, file_path, configure.fmt),
               catch_exceptions=False)

    yield configure


def read_file(configure):

    with open(configure.repo.path(configure.alias)) as stream:
        return stream.read()


def get_key(key, configure):

    return 'section1:{0}'.format(key) if configure.fmt == constants.INI else key


def write_file(dictionary, configure):

    if configure.fmt == constants.INI:
        # ini format must have its sections as the
        # first level keys of the dictionary
        dictionary = {'section1': copy.deepcopy(dictionary)}

    writer.dump(obj=dictionary,
                file_path=configure.repo.path(configure.alias),
                fmt=configure.fmt)
    configure.repo.commit(alias=configure.alias)


def write_string(dictionary, configure):

    if configure.fmt == constants.INI:
        # ini format must have its sections as the
        # first level keys of the dictionary
        dictionary = {'section1': copy.deepcopy(dictionary)}

    return writer.dumps(obj=dictionary, fmt=configure.fmt)


def skip_if_not_compound(configure):

    if configure.fmt not in constants.COMPOUND_FORMATS:
        pytest.skip('{0} format does not support this'.format(configure.fmt))


def test_put_with_simple_value(configure):

    write_file(
        dictionary={
            'key1': 'value1'
        },
        configure=configure
    )

    expected = write_string(
        dictionary={
            'key1': 'value2'
        },
        configure=configure)

    expected_message = configure.alias

    configure.run('put --key {0} --value value2 --message {1}'
                  .format(get_key('key1', configure), expected_message))

    actual = read_file(configure=configure)

    assert expected == actual
    assert expected_message == configure.repo.message(alias=configure.alias, version=2)


def test_put_with_int_value(configure):

    write_file(
        dictionary={
            'key1': 'value1'
        },
        configure=configure
    )

    expected = write_string(
        dictionary={
            'key1': 5
        },
        configure=configure)

    configure.run('put --key {0} --value 5'.format(get_key('key1', configure)))

    actual = read_file(configure=configure)

    assert expected == actual


def test_put_with_float_value(configure):

    write_file(
        dictionary={
            'key1': 'value1'
        },
        configure=configure
    )

    expected = write_string(
        dictionary={
            'key1': 5.5
        },
        configure=configure)

    configure.run('put --key {0} --value 5.5'.format(get_key('key1', configure)))

    actual = read_file(configure=configure)

    assert expected == actual


def test_put_compound_value(configure):

    write_file(
        dictionary={
            'key1': 'value1'
        },
        configure=configure
    )

    fmt = configure.fmt

    catch_exception = fmt not in constants.COMPOUND_FORMATS

    result = configure.run('put --key {0} --value {{"key2":"value1"}}'
                           .format(get_key('key1', configure)), catch_exceptions=catch_exception,
                           escape=True)

    if fmt not in constants.COMPOUND_FORMATS:
        expected = 'Error: Unsupported operation: put with complex values (format={0})'.format(
            fmt)
        actual = result.std_out
    else:
        expected = write_string(
            dictionary={
                'key1': {
                    'key2': 'value1'
                }
            },
            configure=configure)
        actual = read_file(configure=configure)

    assert expected in actual


def test_put_complex_key_compound_value(configure):

    fmt = configure.fmt
    if fmt in constants.COMPOUND_FORMATS:
        write_file(
            dictionary={
                'key1': {
                    'key2': 'value1'
                }
            },
            configure=configure)

    result = configure.run('put --key key1:key2 --value {"key3":"value2"}',
                           catch_exceptions=True, escape=True)

    if fmt not in constants.COMPOUND_FORMATS:
        expected = 'Error: Unsupported operation: put with complex {0} (format={1})'.format(
            'keys' if fmt == constants.PROPERTIES else 'values', fmt)
        actual = result.std_out
    else:
        expected = writer.dumps(
            obj={
                'key1': {
                    'key2': {
                        'key3': 'value2'
                    }
                }
            },
            fmt=configure.fmt)
        actual = read_file(configure=configure)

    assert expected in actual


def test_delete_complex_key(configure):

    fmt = configure.fmt
    if fmt in constants.COMPOUND_FORMATS:
        write_file(
            dictionary={
                'key1': {
                    'key2': 'value1',
                    'key3': 'value2'
                }
            },
            configure=configure)

    result = configure.run('delete --key key1:key3', catch_exceptions=True)

    if fmt not in constants.COMPOUND_FORMATS:
        expected = 'Error: Unsupported operation: delete with complex keys (format={0})'\
                   .format(fmt)
        if fmt == constants.INI:
            expected = "Error: Key 'key1:key3' does not exist"
        actual = result.std_out
    else:
        expected = writer.dumps(
            obj={
                'key1': {
                    'key2': 'value1'
                }
            },
            fmt=configure.fmt)
        actual = read_file(configure=configure)

    assert expected in actual


def test_delete_non_existing_key(configure):

    write_file(
        dictionary={
            'key1': 'value1'
        },
        configure=configure)

    expected = "Error: Key '{0}' does not exist".format(get_key('key2', configure))

    result = configure.run('delete --key {0}'.format(get_key('key2', configure)),
                           catch_exceptions=True)

    actual = result.std_out

    assert expected in actual


def test_delete(configure):

    write_file(
        dictionary={
            'key1': 'value1',
            'key2': 'value2'
        },
        configure=configure)

    expected = write_string(
        dictionary={
            'key2': 'value2'
        },
        configure=configure)

    expected_message = configure.alias

    result = configure.run('delete --key {0} --message {1}'
                           .format(get_key('key1', configure), expected_message))

    actual = read_file(configure=configure)

    expected_deleted_value = 'value1'

    assert expected == actual
    assert expected_deleted_value in result.std_out
    assert expected_message == configure.repo.message(alias=configure.alias, version=2)


def test_get(configure):

    write_file(
        dictionary={
            'key1': 'value1'
        },
        configure=configure)

    expected = 'value1'

    result = configure.run('get --key {0}'.format(get_key('key1', configure)))

    actual = result.std_out

    assert expected in actual


def test_get_non_existing_key(configure):

    write_file(
        dictionary={
            'key1': 'value1'
        },
        configure=configure)

    key = get_key('key2', configure)
    expected = "Error: Key '{0}' does not exist".format(key)

    result = configure.run('get --key {0}'.format(key), catch_exceptions=True)

    actual = result.std_out

    assert expected in actual


def test_get_compound_value(configure):

    # there is no way to create a file with compound
    # values if the format is not compound, so this test
    # is un-necessary in that case.
    skip_if_not_compound(configure)

    write_file(
        dictionary={
            'key1': {
                'key2': 'value1'
            }
        },
        configure=configure)

    expected = write_string(
        dictionary={
            "key2": "value1"
        },
        configure=configure)

    result = configure.run('get --key {0}'.format(get_key('key1', configure)))

    actual = result.std_out

    assert expected.strip() in actual


def test_get_complex_key(configure):

    fmt = configure.fmt
    if fmt in constants.COMPOUND_FORMATS:
        write_file(
            dictionary={
                'key1': {
                    'key2': 'value1'
                }
            },
            configure=configure)

    result = configure.run('get --key key1:key2', catch_exceptions=True)

    if fmt not in constants.COMPOUND_FORMATS:
        expected = 'Error: Unsupported operation: get with complex keys (format={0})'.format(fmt)

        if fmt == constants.INI:
            expected = "Error: Key 'key1:key2' does not exis"

        actual = result.std_out
    else:
        expected = 'value1'
        actual = result.std_out

    assert expected in actual


def test_add(configure):

    fmt = configure.fmt
    if fmt in constants.COMPOUND_FORMATS:
        write_file(
            dictionary={
                'key1': ['value1']
            },
            configure=configure)

    expected_message = configure.alias

    result = configure.run('add --key {0} --value value2 --message {1}'
                           .format(get_key('key1', configure), expected_message),
                           catch_exceptions=True)

    if fmt not in constants.COMPOUND_FORMATS:
        expected = 'Error: Unsupported operation: add (format={0})'.format(fmt)
        actual = result.std_out
        assert expected in actual
    else:
        expected = write_string(
            dictionary={
                'key1': ['value1', 'value2']
            },
            configure=configure)
        actual = read_file(configure=configure)

        assert expected == actual

        expected = writer.dumps(obj=['value1', 'value2'], fmt=fmt)

        assert expected.strip() in result.std_out
        assert expected_message == configure.repo.message(alias=configure.alias, version=2)


def test_add_to_complex_key(configure):

    fmt = configure.fmt
    if fmt in constants.COMPOUND_FORMATS:
        write_file(
            dictionary={
                'key1': {
                    'key2': ['value1']
                }
            },
            configure=configure)

    result = configure.run('add --key {0} --value value2'
                           .format(get_key('key1:key2', configure)),
                           catch_exceptions=True)

    if fmt not in constants.COMPOUND_FORMATS:
        expected = 'Error: Unsupported operation: add (format={0})'.format(fmt)
        actual = result.std_out
    else:
        expected = write_string(
            dictionary={
                'key1': {
                    'key2': ['value1', 'value2']
                }
            },
            configure=configure)
        actual = read_file(configure=configure)

    assert expected in actual


def test_remove(configure):

    fmt = configure.fmt
    if fmt in constants.COMPOUND_FORMATS:
        write_file(
            dictionary={
                'key1': ['value1', 'value2']
            },
            configure=configure)

    expected_message = configure.alias

    result = configure.run('remove --key {0} --value value2 --message {1}'
                           .format(get_key('key1', configure), expected_message),
                           catch_exceptions=True)

    if fmt not in constants.COMPOUND_FORMATS:
        expected = 'Error: Unsupported operation: remove (format={0})'.format(fmt)
        actual = result.std_out
        assert expected in actual
    else:
        expected = write_string(
            dictionary={
                'key1': ['value1']
            },
            configure=configure)
        actual = read_file(configure=configure)

        assert expected == actual

        expected = writer.dumps(obj=['value1'], fmt=fmt)

        assert expected.strip() in result.std_out
        assert expected_message == configure.repo.message(alias=configure.alias, version=2)


def test_remove_from_complex_key(configure):

    fmt = configure.fmt
    if fmt in constants.COMPOUND_FORMATS:
        write_file(
            dictionary={
                'key1': {
                    'key2': ['value1', 'value2']
                }
            },
            configure=configure)

    result = configure.run('remove --key {0} --value value2'
                           .format(get_key('key1:key2', configure)),
                           catch_exceptions=True)

    if fmt not in constants.COMPOUND_FORMATS:
        expected = 'Error: Unsupported operation: remove (format={0})'.format(fmt)
        actual = result.std_out
    else:
        expected = write_string(
            dictionary={
                'key1': {
                    'key2': ['value1']
                }
            },
            configure=configure)
        actual = read_file(configure=configure)

    assert expected in actual


def test_corrupt_file(configure):

    fmt = configure.fmt
    alias = configure.alias

    if fmt == constants.PROPERTIES:
        pytest.skip('Need to find a way of corrupting a .properties file')

    corrupted_string = '''corruption
{
  "key1": "key2"
}'''

    file_path = configure.repo.path(alias)
    with open(file_path, 'w') as stream:
        stream.write(corrupted_string)

    result = configure.run('get --key key1:key2', catch_exceptions=True)

    expected = get_parse_error(fmt)

    assert expected in result.std_out


def test_different_file(configure):

    exception = click.ClickException(message='Cannot perform operation')

    expected = 'Error: ' + str(exception)

    file_path = configure.repo.path(configure.alias)
    with open(file_path, 'w') as stream:

        changed = {'key1': 'value1'}

        stream.write(write_string(dictionary=changed, configure=configure))

    result = configure.run('get --key {0}'.format(get_key('key1:key2', configure)),
                           catch_exceptions=True)

    assert expected in result.std_out
    assert causes.DIFFER_FROM_LATEST in result.std_out
    assert solutions.reset_to_latest(configure.alias) in result.std_out
    assert solutions.commit(configure.alias) in result.std_out
