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


import shutil
import os

from fileconfig.api import utils
from fileconfig.api import exceptions
from fileconfig.api import parser
from fileconfig.api import writer
from fileconfig.api import constants


class Repository(object):

    BLANK_STATE = {
        'files': {}
    }

    _repo_dir = None
    _state_file = None

    def __init__(self, config_dir):

        self._repo_dir = os.path.join(config_dir, 'repo')
        self._state_file = os.path.join(self._repo_dir, 'repo.json')

        utils.smkdir(self._repo_dir)

        if not os.path.exists(self._state_file):
            writer.dump(obj=self.BLANK_STATE, file_path=self._state_file, fmt=constants.JSON)

    @property
    def root(self):
        return self._repo_dir

    def add(self, alias, file_path, fmt):

        file_path = os.path.abspath(file_path)

        if not os.path.exists(file_path):
            raise exceptions.FileNotFoundException(file_path=file_path)

        if os.path.isdir(file_path):
            raise exceptions.FileIsDirectoryException(file_path=file_path)

        if self._exists(alias):
            raise exceptions.AliasAlreadyExistsException(alias=alias)

        parser.load(file_path=file_path, fmt=fmt)

        state = self._load_state()
        state['files'][alias] = {'file_path': file_path, 'fmt': fmt}

        self._save_state(state)

        self.commit(alias)

    def remove(self, alias):

        if not self._exists(alias):
            raise exceptions.AliasNotFoundException(alias=alias)

        state = self._load_state()
        del state['files'][alias]

        self._save_state(state)

        shutil.rmtree(os.path.join(self._repo_dir, alias))

    def path(self, alias):

        if not self._exists(alias):
            raise exceptions.AliasNotFoundException(alias=alias)

        state = self._load_state()

        return state['files'][alias]['file_path']

    def fmt(self, alias):

        if not self._exists(alias):
            raise exceptions.AliasNotFoundException(alias=alias)

        state = self._load_state()

        return state['files'][alias]['fmt']

    def commit(self, alias):

        if not self._exists(alias):
            raise exceptions.AliasNotFoundException(alias=alias)

        utils.smkdir(os.path.join(self._repo_dir, alias))

        version = self._find_current_version(alias) + 1
        shutil.copy(src=self.path(alias), dst=os.path.join(self._repo_dir, alias, str(version)))

    def revisions(self, alias):

        if not self._exists(alias):
            raise exceptions.AliasNotFoundException(alias=alias)

        revisions = []

        for version in utils.lsf(os.path.join(self._repo_dir, alias)):
            timestamp = os.path.getmtime(os.path.join(self._repo_dir, alias, version))
            revisions.append(Revision(alias=alias,
                                      file_path=self.path(alias),
                                      timestamp=timestamp,
                                      version=int(version)))

        return revisions

    def files(self):

        state = self._load_state()

        result = []
        for alias in state['files']:
            result.append(File(alias=alias,
                               file_path=self.path(alias),
                               fmt=self.fmt(alias)))

        return result

    def contents(self, alias, version):

        if not self._exists(alias):
            raise exceptions.AliasNotFoundException(alias=alias)

        if version == 'latest':
            version = max([revision.version for revision in self.revisions(alias)])

        file_path = os.path.join(self._repo_dir, alias, str(version))

        if not os.path.exists(file_path):
            raise exceptions.VersionNotFoundException(alias=alias, version=version)

        with open(file_path) as f:
            return f.read()

    def _exists(self, alias):

        state = self._load_state()

        return alias in state['files']

    def _find_current_version(self, alias):

        versions = utils.lsf(os.path.join(self._repo_dir, alias))

        if not versions:
            return -1

        return max([int(version) for version in versions])

    def _load_state(self):
        return parser.load(file_path=self._state_file, fmt=constants.JSON)

    def _save_state(self, state):
        writer.dump(obj=state, file_path=self._state_file, fmt=constants.JSON)


# pylint: disable=too-few-public-methods
class File(object):

    def __init__(self, alias, file_path, fmt):
        super(File, self).__init__()
        self.fmt = fmt
        self.file_path = file_path
        self.alias = alias


# pylint: disable=too-few-public-methods
class Revision(object):

    def __init__(self, alias, file_path, timestamp, version):
        self.alias = alias
        self.timestamp = timestamp
        self.file_path = file_path
        self.version = version
