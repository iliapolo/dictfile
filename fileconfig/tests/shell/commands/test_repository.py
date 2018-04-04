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
import datetime
import os
import shutil
import tempfile

import pytest
from prettytable import PrettyTable

from fileconfig.api import writer, constants, exceptions
from fileconfig.api.repository import Repository as ApiRepository
from fileconfig.shell import build_info, solutions, causes
from fileconfig.tests.shell.commands import Runner
from fileconfig.shell import PROGRAM_NAME


TEST_DICT = {'key1': 'value1'}


@pytest.fixture(name='repository', params=constants.SUPPORTED_FORMATS)
def repo(request):

    class Repository(object):

        def __init__(self, _request):
            super(Repository, self).__init__()
            self._request = _request
            self._runner = Runner()
            self._repo = ApiRepository(os.path.join(tempdir, '.{0}'.format(PROGRAM_NAME)))

        def run(self, command, catch_exceptions=False):

            command = 'fileconfig repository {0}'.format(command)

            return self._runner.run(command, catch_exceptions=catch_exceptions)

        @property
        def request(self):
            return self._request

        @property
        def repo(self):
            return self._repo

        @property
        def alias(self):
            return self._request.node.name

        @property
        def fmt(self):
            return self._request.param

    # change the home directory because the configuration
    # folder is created there, and we don't want to pollute the actual
    # home directory.
    tempdir = tempfile.mkdtemp()
    os.environ['HOME'] = tempdir

    repository = Repository(request)

    # create the file we intent to alias
    file_path = os.path.join(tempdir, repository.alias)
    writer.dump(obj=TEST_DICT, file_path=file_path, fmt=repository.fmt)
    Runner().run('fileconfig repository add --alias {0} --file-path {1} --fmt {2}'
                 .format(repository.alias, file_path, repository.fmt),
                 catch_exceptions=False)

    yield repository

    # cleanup
    shutil.rmtree(tempdir)


def test_add_no_file(repository):

    result = repository.run('add --alias=dummy --file-path=doesnt-exist --fmt={0}'
                            .format(repository.fmt), catch_exceptions=True)

    expected_output = 'Error: File {0} does not exist\n'.format(
        os.path.join(os.getcwd(), 'doesnt-exist'))

    assert expected_output == result.output


def test_add_file_is_directory(repository, temp_dir):

    result = repository.run('add --alias=dummy --file-path={0} --fmt={1}'
                            .format(temp_dir, repository.fmt), catch_exceptions=True)

    expected_output = 'Error: {0} is a directory, not a file\n'.format(temp_dir)

    assert expected_output == result.output


def test_add_alias_exists(repository, temp_file):

    result = repository.run('add --alias={0} --file-path={1} --fmt={2}'
                            .format(repository.alias, temp_file, repository.fmt),
                            catch_exceptions=True)

    expected_output = 'Error: Alias {0} already exists\n'.format(repository.alias)

    assert expected_output == result.output


def test_show(repository):

    alias = repository.alias

    result = repository.run('show --alias {0} --version 0'.format(alias))

    expected = writer.dumps(obj=TEST_DICT, fmt=repository.fmt)

    assert expected + '\n' == result.output


def test_show_latest(repository):

    alias = repository.alias

    result = repository.run('show --alias {0} --version latest'.format(alias))

    expected = writer.dumps(obj=TEST_DICT, fmt=repository.fmt)

    assert expected + '\n' == result.output


def test_show_current(repository):

    alias = repository.alias

    expected = '{"key3": "value3"}'

    with open(repository.repo.path(alias), 'w') as stream:
        stream.write(expected)

    result = repository.run('show --alias {0} --version current'.format(alias))

    assert expected + '\n' == result.output


def test_show_wrong_alias(repository):

    result = repository.run('show --alias unknown --version 0', catch_exceptions=True)

    expected = 'Error: Alias unknown not found\n'

    assert expected == result.output


def test_show_wrong_version(repository):

    alias = repository.alias
    result = repository.run('show --alias {0} --version 1'.format(alias), catch_exceptions=True)

    expected = 'Error: Version 1 not found for alias: {0}\n'.format(alias)

    assert expected == result.output


def test_revisions(repository):

    alias = repository.alias

    result = repository.run('revisions --alias {0}'.format(alias))

    timestamp = repository.repo.revisions(alias)[0].timestamp

    table = PrettyTable(field_names=['alias', 'path', 'timestamp', 'version'])
    table.add_row([repository.alias, repository.repo.path(alias),
                   datetime.datetime.fromtimestamp(timestamp).isoformat(), '0'])

    expected = table.get_string()

    assert expected + '\n' == result.output


def test_revisions_wrong_alias(repository):

    result = repository.run('revisions --alias unknown', catch_exceptions=True)

    expected = 'Error: Alias unknown not found\n'

    assert expected == result.output


def test_files(repository):

    result = repository.run('files')

    table = PrettyTable(field_names=['alias', 'path', 'format'])
    table.add_row([repository.alias, repository.repo.path(repository.alias), repository.fmt])

    expected = table.get_string()

    assert expected + '\n' == result.output


def test_reset(repository):

    alias = repository.alias
    file_path = repository.repo.path(alias)
    with open(file_path, 'w') as stream:
        stream.write('corrupted')

    repository.run('reset --alias {0} --version 0'.format(alias))

    with open(file_path) as stream:
        expected = writer.dumps(obj=TEST_DICT, fmt=repository.fmt)
        actual = stream.read()

    revisions = repository.repo.revisions(alias)

    expected_number_of_revisions = 2

    assert expected == actual
    assert expected_number_of_revisions == len(revisions)


def test_reset_latest(repository):

    alias = repository.alias
    file_path = repository.repo.path(alias)
    with open(file_path, 'w') as stream:
        stream.write('corrupted')

    repository.run('reset --alias {0} --version latest'.format(alias))

    with open(file_path) as stream:
        expected = writer.dumps(obj=TEST_DICT, fmt=repository.fmt)
        actual = stream.read()

    revisions = repository.repo.revisions(alias)

    expected_number_of_revisions = 2

    assert expected == actual
    assert expected_number_of_revisions == len(revisions)


def test_reset_wrong_alias(repository):

    result = repository.run('reset --alias unknown --version 1', catch_exceptions=True)

    expected = 'Error: Alias unknown not found\n'

    assert expected == result.output


def test_reset_wrong_version(repository):

    result = repository.run('reset --alias {0} --version 1'.format(repository.alias),
                            catch_exceptions=True)

    expected = 'Error: Version 1 not found for alias: {0}\n'.format(repository.alias)

    assert expected == result.output


def test_remove(repository):

    alias = repository.alias

    repository.run('remove --alias {0}'.format(alias))

    files = repository.repo.files()

    expected_number_of_files = 0

    assert expected_number_of_files == len(files)


def test_remove_wrong_alias(repository):

    result = repository.run('remove --alias unknown', catch_exceptions=True)

    expected = 'Error: Alias unknown not found\n'

    assert expected == result.output


def test_commit(repository):

    alias = repository.alias

    file_path = repository.repo.path(alias)

    with open(file_path, 'w') as stream:

        changed = copy.deepcopy(TEST_DICT)
        for key, value in TEST_DICT.items():
            changed[key] = value + '-' + repository.alias

        contents = writer.dumps(obj=changed, fmt=repository.fmt)
        stream.write(contents)

    repository.run('commit --alias {0}'.format(alias))

    revisions = repository.repo.revisions(alias)

    expected_number_of_revisions = 2

    assert expected_number_of_revisions == len(revisions)
    assert contents == repository.repo.contents(alias=alias, version=1)


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

    ex = exceptions.CorruptFileException(file_path=file_path,
                                         message='''mapping values are not allowed here
  in "<string>", line 3, column 9:
      "key1": "key2"
            ^''')
    ex.possible_solutions = [solutions.edit_manually(), solutions.reset_to_latest(alias)]
    ex.cause = causes.EDITED_MANUALLY

    expected = 'Error: ' + str(ex) + build_info(ex) + '\n'

    assert expected == result.output


def test_commit_unknown_alias(repository):

    result = repository.run('commit --alias unknown', catch_exceptions=True)

    expected = 'Error: Alias unknown not found\n'

    assert expected == result.output
