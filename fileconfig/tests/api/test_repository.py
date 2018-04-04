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

import os
import tempfile

import pytest

from fileconfig.api import constants
from fileconfig.api import exceptions
from fileconfig.api import writer
from fileconfig.api.repository import Repository


class TestRepository(object):

    @staticmethod
    @pytest.fixture(scope='class')
    def tracked_file():
        return tempfile.mkstemp()[1]

    @staticmethod
    @pytest.fixture(params=constants.SUPPORTED_FORMATS)
    def repo(tracked_file, temp_dir, request):

        alias = request.node.name
        fmt = request.param

        writer.dump(obj={'key1': 'value1'},
                    file_path=tracked_file,
                    fmt=fmt)

        repo = Repository(config_dir=temp_dir)
        repo.add(alias=alias, file_path=tracked_file, fmt=fmt)

        # attach the format to the repo instance so that
        # test functions will have it.
        repo.test_fmt = fmt

        yield repo

    @staticmethod
    def test_add_no_file(repo):

        with pytest.raises(exceptions.FileNotFoundException):
            repo.add(alias='dummy', file_path='doesnt-exist', fmt=repo.test_fmt)

    @staticmethod
    def test_add_file_is_directory(repo, temp_dir):

        with pytest.raises(exceptions.FileIsDirectoryException):
            repo.add(alias='dummy', file_path=temp_dir, fmt=repo.test_fmt)

    @staticmethod
    def test_add_alias_exists(repo, temp_file, request):

        with pytest.raises(exceptions.AliasAlreadyExistsException):
            repo.add(alias=request.node.name, file_path=temp_file, fmt=repo.test_fmt)

    @staticmethod
    def test_path(repo, request, tracked_file):

        alias = request.node.name
        assert tracked_file == repo.path(alias)

    @staticmethod
    def test_path_unknown_alias(repo):

        alias = 'unknown'

        with pytest.raises(exceptions.AliasNotFoundException):
            repo.path(alias)

    @staticmethod
    def test_fmt(repo, request):

        alias = request.node.name
        assert repo.test_fmt == repo.fmt(alias)

    @staticmethod
    def test_fmt_unknown_alias(repo):

        alias = 'unknown'

        with pytest.raises(exceptions.AliasNotFoundException):
            repo.fmt(alias)

    @staticmethod
    def test_commit(repo, request):

        alias = request.node.name

        repo.commit(alias)

        # make sure the correct file was created
        version_path = os.path.join(repo.root, alias, '1')

        assert os.path.isfile(version_path)

    @staticmethod
    def test_commit_unknown_alias(repo):

        alias = 'unknown'

        with pytest.raises(exceptions.AliasNotFoundException):
            repo.commit(alias)

    @staticmethod
    def test_revisions(repo, tracked_file, request):

        alias = request.node.name
        revisions = repo.revisions(alias)

        expected_number_of_revisions = 1
        expected_version_number = 0

        assert expected_number_of_revisions == len(revisions)
        assert alias == revisions[0].alias
        assert tracked_file == revisions[0].file_path
        assert expected_version_number == revisions[0].version

    @staticmethod
    def test_revisions_unknown_alias(repo):

        alias = 'unknown'

        with pytest.raises(exceptions.AliasNotFoundException):
            repo.revisions(alias)

    @staticmethod
    def test_files(repo, request, tracked_file):

        files = repo.files()

        expected_number_of_files = 1

        assert expected_number_of_files == len(files)
        assert request.node.name == files[0].alias
        assert tracked_file == files[0].file_path
        assert repo.test_fmt == files[0].fmt

    @staticmethod
    def test_contents(repo, request):

        alias = request.node.name
        contents = repo.contents(alias=alias, version=0)

        assert writer.dumps({'key1': 'value1'}, fmt=repo.test_fmt) == contents

    @staticmethod
    def test_contents_unknown_alias(repo):

        with pytest.raises(exceptions.AliasNotFoundException):
            repo.contents(alias='unknown', version=1)

    @staticmethod
    def test_contents_wrong_version(repo, request):

        with pytest.raises(exceptions.VersionNotFoundException):
            repo.contents(alias=request.node.name, version=1)

    @staticmethod
    def test_remove(repo, request):

        alias = request.node.name

        repo.remove(alias=alias)

        with pytest.raises(exceptions.AliasNotFoundException):
            repo.remove(alias)

        files = repo.files()

        expected_number_of_files = 0

        assert expected_number_of_files == len(files)
        assert not os.path.exists(os.path.join(repo.root, alias))

    @staticmethod
    def test_remove_unknown_alias(repo):

        with pytest.raises(exceptions.AliasNotFoundException):
            repo.remove(alias='unknown')
