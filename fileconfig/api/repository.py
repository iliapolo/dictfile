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
import base64

from fileconfig.api import utils
from fileconfig.api import exceptions


class Repository(object):

    _repo_dir = None

    def __init__(self, repo_dir):
        self._repo_dir = repo_dir

    def commit(self, filename):

        file_dir = base64.b64encode(filename)

        utils.smkdir(os.path.join(self._repo_dir, file_dir))

        version = self._find_current_version(filename) + 1
        shutil.copy(src=filename, dst=os.path.join(self._repo_dir, file_dir, str(version)))

    def exists(self, filename):

        file_dir = base64.b64encode(filename)

        return os.path.isdir(os.path.join(self._repo_dir, file_dir))

    def revisions(self, filename):

        if not self.exists(filename):
            raise exceptions.FileNotFoundException(filename=filename)

        revisions = []

        file_dir = base64.b64encode(filename)

        for version in utils.lsf(os.path.join(self._repo_dir, file_dir)):
            timestamp = os.path.getmtime(os.path.join(self._repo_dir, file_dir, version))
            revisions.append(Revision(filename=filename, timestamp=timestamp, version=int(version)))

        return revisions

    def files(self):

        return map(lambda encoded: base64.b64decode(encoded), utils.lsd(self._repo_dir))

    def contents(self, filename, version):

        file_dir = base64.b64encode(filename)

        if not self.exists(filename):
            raise exceptions.FileNotFoundException(filename=filename)

        file_path = os.path.join(self._repo_dir, file_dir, version)

        if not os.path.exists(file_path):
            raise exceptions.VersionNotFoundException(filename=filename, version=version)

        with open(file_path) as f:
            return f.read()

    def init(self):
        utils.smkdir(self._repo_dir)

    def _find_current_version(self, filename):

        file_dir = base64.b64encode(filename)

        versions = utils.lsf(os.path.join(self._repo_dir, file_dir))

        if not versions:
            return -1

        return max(map(lambda version: int(version), versions))


class Revision(object):

    _filename = None
    _timestamp = None
    _version = None

    def __init__(self, filename, timestamp, version):
        self._timestamp = timestamp
        self._filename = filename
        self._version = version

    @property
    def filename(self):
        return self._filename

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def version(self):
        return self._version
