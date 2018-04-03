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
import json
import pytest

from fileconfig.api.repository import Repository


class TestRepository(object):

    @staticmethod
    @pytest.fixture
    def repo():
        mkdtemp = tempfile.mkdtemp()
        return Repository(repo_dir=mkdtemp)

    @staticmethod
    def test_add(repo, request):

        mkdtemp = tempfile.mkdtemp()
        alias = request.node.name

        file_path = os.path.join(mkdtemp, alias)
        with open(file_path, 'w') as stream:
            stream.write(json.dumps(obj={'key1': 'value1'}))

        repo.add(alias=alias, file_path=file_path, fmt='json')

        assert file_path == repo.path(alias=alias)
        assert repo.fmt(alias=alias) == 'json'

        # create a new instance to make sure the state
        # changes were persisted to disk
        repo = Repository(repo.repo_dir)

        assert file_path == repo.path(alias=alias)
        assert repo.fmt(alias=alias) == 'json'
