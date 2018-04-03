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


class VersionNotFoundException(BaseException):

    def __init__(self, file_path, version):
        self.file_path = file_path
        self.version = version

    def __str__(self):
        return 'Version {0} not found for file: {0}'.format(self.version, self.file_path)


class AliasNotFoundException(BaseException):

    def __init__(self, alias):
        self.alias = alias

    def __str__(self):
        return 'Alias {0} not found'.format(self.alias)


class FileIsDirectoryException(BaseException):

    def __init__(self, file_path):
        self.file_path = file_path

    def __str__(self):
        return '{0} is a directory, not a file'.format(self.file_path)


class FileNotFoundException(BaseException):

    def __init__(self, file_path):
        self.file_path = file_path

    def __str__(self):
        return 'File {0} does not exist'.format(self.file_path)


class FileAlreadyExistsException(BaseException):

    def __init__(self, file_path):
        self.file_path = file_path

    def __str__(self):
        return 'File {0} already exists'.format(self.file_path)


class KeyNotFoundException(BaseException):

    def __init__(self, key):
        self.key = key

    def __str__(self):
        return "Key '{0}' does not exist".format(self.key)


class InvalidValueTypeException(BaseException):

    def __init__(self, key, expected_type, actual_type):
        self.expected_type = expected_type
        self.key = key
        self.actual_type = actual_type

    def __str__(self):
        return "Invalid value type for key '{0}. Expected: {1}, Actual: {2}".format(
            self.key,
            self.expected_type,
            self.actual_type)


class UnsupportedFormatException(BaseException):

    def __init__(self, fmt):
        self.fmt = fmt

    def __str__(self):
        return 'Unsupported Format: {0}'.format(self.fmt)
