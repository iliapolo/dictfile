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

from fileconfig.api import constants
from fileconfig.api import exceptions
from fileconfig.api import writer
from fileconfig.shell import PROGRAM_NAME
from fileconfig.shell import solutions, build_info, causes
from fileconfig.tests.shell.commands import CommandLineFixture
from fileconfig.tests.shell.commands import Runner

TEST_DICT = {'key1': 'value1'}


@pytest.fixture(name='configure', params=constants.SUPPORTED_FORMATS)
def conf(request, home_dir):

    class Configure(CommandLineFixture):

        def run(self, command, catch_exceptions=False):

            command = '{0} configure {1} {2}'.format(PROGRAM_NAME, self.alias, command)

            return self._runner.run(command, catch_exceptions=catch_exceptions)

    configure = Configure(request, home_dir)

    # create the file we intent to operate on
    file_path = os.path.join(home_dir, configure.alias)
    writer.dump(obj=TEST_DICT,
                file_path=file_path,
                fmt=configure.fmt)

    # add the file to the repository
    Runner().run('{0} repository add --alias {1} --file-path {2} --fmt {3}'
                 .format(PROGRAM_NAME, configure.alias, file_path, configure.fmt),
                 catch_exceptions=False)

    yield configure


def read_file(configure):

    with open(configure.repo.path(configure.alias)) as stream:
        return stream.read()


def write_file(dictionary, configure):

    writer.dump(obj=dictionary,
                file_path=configure.repo.path(configure.alias),
                fmt=configure.fmt)
    configure.repo.commit(alias=configure.alias)


def skip_if_not_compound(configure):

    if configure.fmt in [constants.PROPERTIES]:
        pytest.skip('{0} format does not support this'.format(configure.fmt))


def test_put_with_simple_value(configure):

    write_file(
        dictionary={
            'key1': 'value1'
        },
        configure=configure
    )

    expected = writer.dumps(
        obj={
            'key1': 'value2'
        },
        fmt=configure.fmt)

    configure.run('put --key key1 --value value2')

    actual = read_file(configure=configure)

    assert expected == actual


def test_put_with_int_value(configure):

    write_file(
        dictionary={
            'key1': 'value1'
        },
        configure=configure
    )

    expected = writer.dumps(
        obj={
            'key1': 5
        },
        fmt=configure.fmt)

    configure.run('put --key key1 --value 5')

    actual = read_file(configure=configure)

    assert expected == actual


def test_put_with_float_value(configure):

    write_file(
        dictionary={
            'key1': 'value1'
        },
        configure=configure
    )

    expected = writer.dumps(
        obj={
            'key1': 5.5
        },
        fmt=configure.fmt)

    configure.run('put --key key1 --value 5.5')

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
    result = configure.run('put --key key1 --value {"key2":"value1"}', catch_exceptions=True)

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
            fmt=configure.fmt)
        actual = read_file(configure=configure)

    assert expected == actual


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

    result = configure.run('put --key key1:key2 --value {"key3":"value2"}', catch_exceptions=True)

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
            fmt=configure.fmt)
        actual = read_file(configure=configure)

    assert expected == actual


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
            fmt=configure.fmt)
        actual = read_file(configure=configure)

    assert expected == actual


def test_delete_non_existing_key(configure):

    write_file(
        dictionary={
            'key1': 'value1'
        },
        configure=configure)

    expected = "Error: Key 'key2' does not exist\n"

    result = configure.run('delete --key key2', catch_exceptions=True)

    actual = result.output

    assert expected == actual


def test_delete(configure):

    write_file(
        dictionary={
            'key1': 'value1',
            'key2': 'value2'
        },
        configure=configure)

    expected = writer.dumps(
        obj={
            'key2': 'value2'
        },
        fmt=configure.fmt)

    configure.run('delete --key key1')

    actual = read_file(configure=configure)

    assert expected == actual


def test_get(configure):

    write_file(
        dictionary={
            'key1': 'value1'
        },
        configure=configure)

    expected = 'value1\n'

    result = configure.run('get --key key1')

    actual = result.output

    assert expected == actual


def test_get_non_existing_key(configure):

    write_file(
        dictionary={
            'key1': 'value1'
        },
        configure=configure)

    expected = "Error: Key 'key2' does not exist\n"

    result = configure.run('get --key key2', catch_exceptions=True)

    actual = result.output

    assert expected == actual


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

    expected = writer.dumps({
        "key2": "value1"
    }, fmt=configure.fmt) + '\n'

    result = configure.run('get --key key1')

    actual = result.output

    assert expected == actual


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
        expected = 'Error: Unsupported operation: get with complex keys (format={0}) \n'.format(fmt)
        actual = result.output
    else:
        expected = 'value1\n'
        actual = result.output

    assert expected == actual


def test_add(configure):

    fmt = configure.fmt
    if fmt in constants.COMPOUND_FORMATS:
        write_file(
            dictionary={
                'key1': ['value1']
            },
            configure=configure)

    result = configure.run('add --key key1 --value value2', catch_exceptions=True)

    if fmt not in constants.COMPOUND_FORMATS:
        expected = 'Error: Unsupported operation: add (format={0}) \n'.format(fmt)
        actual = result.output
    else:
        expected = writer.dumps(
            obj={
                'key1': ['value1', 'value2']
            },
            fmt=fmt)
        actual = read_file(configure=configure)

    assert expected == actual


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

    result = configure.run('add --key key1:key2 --value value2', catch_exceptions=True)

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
            fmt=configure.fmt)
        actual = read_file(configure=configure)

    assert expected == actual


def test_remove(configure):

    fmt = configure.fmt
    if fmt in constants.COMPOUND_FORMATS:
        write_file(
            dictionary={
                'key1': ['value1', 'value2']
            },
            configure=configure)

    result = configure.run('remove --key key1 --value value2', catch_exceptions=True)

    if fmt not in constants.COMPOUND_FORMATS:
        expected = 'Error: Unsupported operation: remove (format={0}) \n'.format(fmt)
        actual = result.output
    else:
        expected = writer.dumps(
            obj={
                'key1': ['value1']
            },
            fmt=configure.fmt)
        actual = read_file(configure=configure)

    assert expected == actual


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

    result = configure.run('remove --key key1:key2 --value value2', catch_exceptions=True)

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
            fmt=configure.fmt)
        actual = read_file(configure=configure)

    assert expected == actual


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

    exception = exceptions.CorruptFileException(file_path=file_path,
                                                message='''mapping values are not allowed here
  in "<string>", line 3, column 9:
      "key1": "key2"
            ^''')
    exception.possible_solutions = [solutions.edit_manually(), solutions.reset_to_latest(alias)]
    exception.cause = causes.EDITED_MANUALLY

    expected = 'Error: ' + str(exception) + build_info(exception) + '\n'

    assert expected == result.output


def test_different_file(configure):

    exception = click.ClickException(message='Cannot perform operation')
    exception.cause = causes.DIFFER_FROM_LATEST
    exception.possible_solutions = [solutions.reset_to_latest(configure.alias),
                                    solutions.commit(configure.alias)]

    expected = 'Error: ' + str(exception) + build_info(exception) + '\n'

    fmt = configure.fmt

    file_path = configure.repo.path(configure.alias)
    with open(file_path, 'w') as stream:

        changed = copy.deepcopy(TEST_DICT)
        for key, value in TEST_DICT.items():
            changed[key] = value + '-' + configure.alias

        stream.write(writer.dumps(obj=changed, fmt=fmt))

    result = configure.run('get --key key1:key2', catch_exceptions=True)

    assert expected == result.output
