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

import copy
import os

import pytest

from dictfile.api import writer, constants, log
from dictfile.tests.shell.commands import CommandLineFixture, get_parse_error

log = log.get_logger(__name__)


@pytest.fixture(name='repository', params=constants.SUPPORTED_FORMATS)
def repo(request, home_dir, runner):

    class Repository(CommandLineFixture):

        def run(self, command, catch_exceptions=False, escape=False):

            command = 'repository {}'.format(command)

            return runner.run(command, catch_exceptions=catch_exceptions, escape=escape)

    repository = Repository(request, home_dir)

    # create the file we intent to alias
    file_path = os.path.join(home_dir, repository.alias)

    writer.dump(obj=get_test_dict(repository), file_path=file_path, fmt=repository.fmt)
    repository.run('add --alias {0} --file-path {1} --fmt {2}'
                   .format(repository.alias, file_path, repository.fmt))

    yield repository


def get_test_dict(repository):

    return get_dict(base_dict={'key1': 'value1'}, repository=repository)


def get_dict(base_dict, repository):

    if repository.fmt == constants.INI:
        dictionary = {'section1': copy.deepcopy(base_dict)}
    else:
        dictionary = base_dict

    return dictionary


def test_add_alias_with_spaces(repository):

    result = repository.run('add --alias "alias with spaces" --file-path dummy --fmt {0}'
                            .format(repository.fmt), catch_exceptions=True)

    expected_output = 'Error: Alias is illegal (Must not contain spaces nor path separators)'

    assert expected_output in result.std_out


def test_add_alias_with_path_sep(repository):

    result = repository.run('add --alias="alias{0}with{0}sep" --file-path=dummy --fmt={1}'
                            .format(os.sep, repository.fmt), catch_exceptions=True)

    expected_output = 'Error: Alias is illegal (Must not contain spaces nor path separators)'

    assert expected_output in result.std_out


def test_add_no_file(repository):

    result = repository.run('add --alias=dummy --file-path=doesnt-exist --fmt={0}'
                            .format(repository.fmt), catch_exceptions=True)

    expected_output = 'Error: File {0} does not exist'.format(
        os.path.join(os.getcwd(), 'doesnt-exist'))

    assert expected_output in result.std_out


def test_add_file_is_directory(repository, temp_dir):

    result = repository.run('add --alias=dummy --file-path={0} --fmt={1}'
                            .format(temp_dir, repository.fmt), catch_exceptions=True)

    expected_output = 'Error: {0} is a directory, not a file'.format(temp_dir)

    assert expected_output in result.std_out


def test_add_alias_exists(repository, temp_file):

    result = repository.run('add --alias={0} --file-path={1} --fmt={2}'
                            .format(repository.alias, temp_file, repository.fmt),
                            catch_exceptions=True)

    expected_output = 'Error: Alias {0} already exists'.format(repository.alias)

    assert expected_output in result.std_out


def test_show(repository):

    alias = repository.alias

    result = repository.run('show --alias {0} --version 0'.format(alias))

    expected = writer.dumps(obj=get_test_dict(repository), fmt=repository.fmt)

    assert expected.strip() in result.std_out


def test_show_latest(repository):

    alias = repository.alias

    result = repository.run('show --alias {0} --version latest'.format(alias))

    expected = writer.dumps(obj=get_test_dict(repository), fmt=repository.fmt)

    assert expected.strip() in result.std_out


def test_show_current(repository):

    alias = repository.alias

    expected = '{"key3": "value3"}'

    with open(repository.repo.path(alias), 'w') as stream:
        stream.write(expected)

    result = repository.run('show --alias {0} --version current'.format(alias))

    assert expected in result.std_out


def test_show_wrong_alias(repository):

    result = repository.run('show --alias unknown --version 0', catch_exceptions=True)

    expected = 'Error: Alias unknown not found'

    assert expected in result.std_out


def test_show_wrong_version(repository):

    alias = repository.alias
    result = repository.run('show --alias {0} --version 1'.format(alias), catch_exceptions=True)

    expected = 'Error: Version 1 not found for alias: {0}'.format(alias)

    assert expected in result.std_out


def test_revisions(repository):

    alias = repository.alias

    result = repository.run('revisions --alias {0}'.format(alias))

    expected = 'original version committed automatically upon adding the file'
    actual = result.std_out

    assert expected in actual


def test_revisions_wrong_alias(repository):

    result = repository.run('revisions --alias unknown', catch_exceptions=True)

    expected = 'Error: Alias unknown not found'

    assert expected in result.std_out


def test_files(repository):

    result = repository.run('files')

    expected = repository.alias

    assert expected in result.std_out


def test_reset(repository):

    alias = repository.alias
    file_path = repository.repo.path(alias)
    with open(file_path, 'w') as stream:
        stream.write('corrupted')

    repository.run('reset --alias {0} --version 0 --message {0}'.format(alias))

    with open(file_path) as stream:
        expected = writer.dumps(obj=get_test_dict(repository), fmt=repository.fmt)
        actual = stream.read()

    revisions = repository.repo.revisions(alias)

    expected_number_of_revisions = 2

    assert expected == actual
    assert expected_number_of_revisions == len(revisions)
    assert alias == repository.repo.message(alias=alias, version=1)


def test_reset_latest(repository):

    alias = repository.alias
    file_path = repository.repo.path(alias)
    with open(file_path, 'w') as stream:
        stream.write('corrupted')

    repository.run('reset --alias {0} --version latest'.format(alias))

    with open(file_path) as stream:
        expected = writer.dumps(obj=get_test_dict(repository), fmt=repository.fmt)
        actual = stream.read()

    revisions = repository.repo.revisions(alias)

    expected_number_of_revisions = 2

    assert expected == actual
    assert expected_number_of_revisions == len(revisions)


def test_reset_wrong_alias(repository):

    result = repository.run('reset --alias unknown --version 1', catch_exceptions=True)

    expected = 'Error: Alias unknown not found'

    assert expected in result.std_out


def test_reset_wrong_version(repository):

    result = repository.run('reset --alias {0} --version 1'.format(repository.alias),
                            catch_exceptions=True)

    expected = 'Error: Version 1 not found for alias: {0}'.format(repository.alias)

    assert expected in result.std_out


def test_remove(repository):

    alias = repository.alias

    repository.run('remove --alias {0}'.format(alias))

    files = repository.repo.files()

    expected_number_of_files = 0

    assert expected_number_of_files == len(files)


def test_remove_wrong_alias(repository):

    result = repository.run('remove --alias unknown', catch_exceptions=True)

    expected = 'Error: Alias unknown not found'

    assert expected in result.std_out


def test_commit(repository):

    alias = repository.alias

    file_path = repository.repo.path(alias)

    with open(file_path, 'w') as stream:

        changed = get_dict(base_dict={'key5': 'value5'}, repository=repository)

        contents = writer.dumps(obj=changed, fmt=repository.fmt)
        stream.write(contents)

    expected_message = "my message"

    repository.run('commit --alias {0} --message "{1}"'.format(alias, expected_message))

    revisions = repository.repo.revisions(alias)

    expected_number_of_revisions = 2

    assert expected_number_of_revisions == len(revisions)
    assert contents == repository.repo.contents(alias=alias, version=1)
    assert expected_message in repository.repo.message(alias=alias, version=1)


def test_commit_corrupt_file(repository):

    fmt = repository.fmt

    if fmt == constants.PROPERTIES:
        pytest.skip('Need to find a way of corrupting a .properties file')

    alias = repository.alias

    file_path = repository.repo.path(alias)

    corrupted_string = '''corruption
{
  "key1": "key2"
}'''

    with open(file_path, 'w') as stream:
        stream.write(corrupted_string)

    result = repository.run('commit --alias {0}'.format(alias), catch_exceptions=True)

    expected = get_parse_error(fmt)

    assert expected in result.std_out


def test_commit_unknown_alias(repository):

    result = repository.run('commit --alias unknown', catch_exceptions=True)

    expected = 'Error: Alias unknown not found'

    assert expected in result.std_out
