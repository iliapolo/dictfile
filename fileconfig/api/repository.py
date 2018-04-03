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


def _state_change(func):

    def wrapper(self, *args, **kwargs):

        state_file = os.path.join(self.repo_dir, 'repo.json')

        # read the state before any changes are made
        state = parser.load(file_path=state_file, fmt=constants.JSON)

        try:

            # apply the function to make changes.
            func(self, *args, **kwargs)

            # persist the new state if everything is ok
            # pylint: disable=protected-access
            writer.dump(obj=self._state, file_path=state_file, fmt=constants.JSON)

        except BaseException:

            # revert back to the state before any changes were made
            # in case of a failure
            # pylint: disable=protected-access
            self._state = state

            # re-raise
            raise

    return wrapper


class Repository(object):

    BLANK_STATE = {
        'files': {}
    }

    repo_dir = None
    _state = None

    def __init__(self, repo_dir):

        self.repo_dir = repo_dir

        utils.smkdir(self.repo_dir)

        state_file = os.path.join(self.repo_dir, 'repo.json')

        if not os.path.exists(state_file):
            writer.dump(obj=self.BLANK_STATE, file_path=state_file, fmt=constants.JSON)

        self._state = parser.load(file_path=state_file, fmt=constants.JSON)

    @_state_change
    def add(self, alias, file_path, fmt):

        file_path = os.path.abspath(file_path)

        if not os.path.exists(file_path):
            raise exceptions.FileNotFoundException(file_path=file_path)

        if os.path.isdir(file_path):
            raise exceptions.FileIsDirectoryException(file_path=file_path)

        if self._exists(alias):
            raise exceptions.FileAlreadyExistsException(file_path=file_path)

        parser.load(file_path=file_path, fmt=fmt)

        self._state['files'][alias] = {'file_path': file_path, 'fmt': fmt}
        self.commit(alias)

    @_state_change
    def remove(self, alias):

        if not self._exists(alias):
            raise exceptions.AliasNotFoundException(alias=alias)

        del self._state['files'][alias]

    def path(self, alias):

        if not self._exists(alias):
            raise exceptions.AliasNotFoundException(alias=alias)

        return self._state['files'][alias]['file_path']

    def fmt(self, alias):
        return self._state['files'][alias]['fmt']

    def commit(self, alias):

        utils.smkdir(os.path.join(self.repo_dir, alias))

        version = self._find_current_version(alias) + 1
        shutil.copy(src=self.path(alias), dst=os.path.join(self.repo_dir, alias, str(version)))

    def revisions(self, alias):

        if not self._exists(alias):
            raise exceptions.AliasNotFoundException(alias=alias)

        revisions = []

        for version in utils.lsf(os.path.join(self.repo_dir, alias)):
            timestamp = os.path.getmtime(os.path.join(self.repo_dir, alias, version))
            revisions.append(Revision(alias=alias,
                                      file_path=self.path(alias),
                                      timestamp=timestamp,
                                      version=int(version)))

        return revisions

    def files(self):

        result = []
        for alias in self._state['files']:
            result.append(File(alias=alias,
                               file_path=self.path(alias),
                               fmt=self.fmt(alias)))

        return result

    def contents(self, alias, version):

        if not self._exists(alias):
            raise exceptions.AliasNotFoundException(alias=alias)

        file_path = os.path.join(self.repo_dir, alias, version)

        if not os.path.exists(file_path):
            raise exceptions.VersionNotFoundException(file_path=alias, version=version)

        with open(file_path) as f:
            return f.read()

    def _exists(self, alias):

        return alias in self._state['files']

    def _find_current_version(self, alias):

        versions = utils.lsf(os.path.join(self.repo_dir, alias))

        if not versions:
            return -1

        return max([int(version) for version in versions])


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
