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

from dictfile.api import utils
from dictfile.api import exceptions
from dictfile.api import parser
from dictfile.api import writer
from dictfile.api import constants
from dictfile.api import logger


ADD_COMMIT_MESSAGE = 'original version committed automatically upon adding the file'


class Repository(object):

    BLANK_STATE = {
        'files': {}
    }

    _repo_dir = None
    _state_file = None
    _logger = None

    def __init__(self, config_dir):

        self._repo_dir = os.path.join(config_dir, 'repo')
        self._state_file = os.path.join(self._repo_dir, 'repo.json')
        self._logger = logger.get_logger('{0}.api.repository.Repository'
                                         .format(constants.PROGRAM_NAME))

        utils.smkdir(self._repo_dir)

        if not os.path.exists(self._state_file):
            writer.dump(obj=self.BLANK_STATE, file_path=self._state_file, fmt=constants.JSON)

    @property
    def root(self):
        return self._repo_dir

    def add(self, alias, file_path, fmt):

        if ' ' in alias or os.sep in alias:
            raise exceptions.IllegalAliasException(alias=alias)

        file_path = os.path.abspath(file_path)
        self._logger.debug('Absolute path translation resulted in {0}'.format(file_path))

        if not os.path.exists(file_path):
            raise exceptions.FileNotFoundException(file_path=file_path)

        if os.path.isdir(file_path):
            raise exceptions.FileIsDirectoryException(file_path=file_path)

        if self._exists(alias):
            raise exceptions.AliasAlreadyExistsException(alias=alias)

        self._logger.debug('Verifying the file can be parsed to {0}'.format(fmt))
        parser.load(file_path=file_path, fmt=fmt)

        state = self._load_state()
        state['files'][alias] = {'file_path': file_path, 'fmt': fmt}

        self._save_state(state)

        self._logger.debug('Committing this file ({0}) to retain its original version'
                           .format(file_path))
        self.commit(alias, message=ADD_COMMIT_MESSAGE)

    def remove(self, alias):

        if not self._exists(alias):
            raise exceptions.AliasNotFoundException(alias=alias)

        state = self._load_state()
        del state['files'][alias]

        self._save_state(state)

        alias_dir = os.path.join(self._repo_dir, alias)
        self._logger.debug('Deleting directory: {0}'.format(alias_dir))
        shutil.rmtree(alias_dir)

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

    def commit(self, alias, message=None):

        if not self._exists(alias):
            raise exceptions.AliasNotFoundException(alias=alias)

        utils.smkdir(os.path.join(self._repo_dir, alias))

        version = self._find_current_version(alias) + 1

        src = self.path(alias)
        revision_dir = os.path.join(self._repo_dir, alias, str(version))
        utils.smkdir(revision_dir)
        dst = os.path.join(revision_dir, 'contents')

        self._logger.debug('Copying {0} --> {1}'.format(src, dst))
        shutil.copy(src=src, dst=dst)

        commit_message_file = os.path.join(revision_dir, 'commit-message')

        self._logger.debug('Creating a commit message file: {0}'.format(commit_message_file))
        with open(commit_message_file, 'w') as stream:
            stream.write(message or '')

    def revisions(self, alias):

        if not self._exists(alias):
            raise exceptions.AliasNotFoundException(alias=alias)

        revisions = []

        for version in utils.lsd(os.path.join(self._repo_dir, alias)):
            self._logger.debug('Found revision {0} for alias {1}'.format(version, alias))
            timestamp = os.path.getmtime(os.path.join(self._repo_dir, alias, version))
            revisions.append(Revision(alias=alias,
                                      file_path=self.path(alias),
                                      timestamp=timestamp,
                                      version=int(version),
                                      commit_message=self.message(alias, version)))

        return revisions

    def files(self):

        state = self._load_state()

        result = []
        for alias in state['files']:
            self._logger.debug('Found alias: {0}'.format(alias))
            result.append(File(alias=alias,
                               file_path=self.path(alias),
                               fmt=self.fmt(alias)))

        return result

    def contents(self, alias, version):

        if not self._exists(alias):
            raise exceptions.AliasNotFoundException(alias=alias)

        version = self._convert_version(alias, version)

        file_path = os.path.join(self._repo_dir, alias, str(version), 'contents')

        if not os.path.exists(file_path):
            raise exceptions.VersionNotFoundException(alias=alias, version=version)

        with open(file_path) as f:
            self._logger.debug('Returning contents of file {0}'.format(file_path))
            return f.read()

    def message(self, alias, version):

        if not self._exists(alias):
            raise exceptions.AliasNotFoundException(alias=alias)

        version = self._convert_version(alias, version)

        file_path = os.path.join(self._repo_dir, alias, str(version), 'commit-message')

        if not os.path.exists(file_path):
            raise exceptions.VersionNotFoundException(alias=alias, version=version)

        with open(file_path) as f:
            self._logger.debug('Returning contents of file {0}'.format(file_path))
            return f.read()

    def _convert_version(self, alias, version):
        if version == 'latest':
            version = max([revision.version for revision in self.revisions(alias)])
            self._logger.debug("Converted version 'latest' to last version: {0}".format(version))
        return version

    def _exists(self, alias):

        state = self._load_state()

        return alias in state['files']

    def _find_current_version(self, alias):

        versions = utils.lsd(os.path.join(self._repo_dir, alias))

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


# pylint: disable=too-few-public-methods,too-many-arguments
class Revision(object):

    def __init__(self, alias, file_path, timestamp, version, commit_message):
        self.commit_message = commit_message
        self.alias = alias
        self.timestamp = timestamp
        self.file_path = file_path
        self.version = version
