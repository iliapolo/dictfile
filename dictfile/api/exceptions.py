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


class ApiException(BaseException):
    pass


class VersionNotFoundException(ApiException):

    def __init__(self, alias, version):
        self.alias = alias
        self.version = version
        super(VersionNotFoundException, self).__init__(self.__str__())

    def __str__(self):
        return 'Version {0} not found for alias: {1}'.format(self.version, self.alias)


class AliasNotFoundException(ApiException):

    def __init__(self, alias):
        self.alias = alias
        super(AliasNotFoundException, self).__init__(self.__str__())

    def __str__(self):
        return 'Alias {0} not found'.format(self.alias)


class FileIsDirectoryException(ApiException):

    def __init__(self, file_path):
        self.file_path = file_path
        super(FileIsDirectoryException, self).__init__(self.__str__())

    def __str__(self):
        return '{0} is a directory, not a file'.format(self.file_path)


class FileNotFoundException(ApiException):

    def __init__(self, file_path):
        self.file_path = file_path
        super(FileNotFoundException, self).__init__(self.__str__())

    def __str__(self):
        return 'File {0} does not exist'.format(self.file_path)


class AliasAlreadyExistsException(ApiException):

    def __init__(self, alias):
        self.file_path = alias
        super(AliasAlreadyExistsException, self).__init__(self.__str__())

    def __str__(self):
        return 'Alias {0} already exists'.format(self.file_path)


class KeyNotFoundException(ApiException):

    def __init__(self, key):
        self.key = key
        super(KeyNotFoundException, self).__init__(self.__str__())

    def __str__(self):
        return "Key '{0}' does not exist".format(self.key)


class InvalidKeyTypeException(ApiException):

    def __init__(self, key, expected_types, actual_type):
        self.expected_types = expected_types
        self.actual_type = actual_type
        self.key = key
        super(InvalidKeyTypeException, self).__init__(self.__str__())

    def __str__(self):
        return "Invalid key type: {0}. Expected: {1}, Actual: {2}".format(
            self.key,
            ','.join([str(t) for t in self.expected_types]),
            self.actual_type)


class InvalidValueTypeException(ApiException):

    def __init__(self, expected_types, actual_type):
        self.expected_types = expected_types
        self.actual_type = actual_type
        super(InvalidValueTypeException, self).__init__(self.__str__())

    def __str__(self):
        return "Invalid value type. Expected: {0}, Actual: {1}".format(
            ','.join([str(t) for t in self.expected_types]),
            self.actual_type)


class UnsupportedFormatException(ApiException):

    def __init__(self, fmt):
        self.fmt = fmt
        super(UnsupportedFormatException, self).__init__(self.__str__())

    def __str__(self):
        return 'Unsupported Format: {0}'.format(self.fmt)


class UnsupportedOperationException(ApiException):

    def __init__(self, fmt, operation):
        self.operation = operation
        self.fmt = fmt
        super(UnsupportedOperationException, self).__init__(self.__str__())

    def __str__(self):
        return "Unsupported operation: {0} (format={1}) ".format(self.operation, self.fmt)


class CorruptFileException(ApiException):

    def __init__(self, file_path, message, alias=None):
        self.alias = alias
        self.file_path = file_path
        self.message = message
        super(CorruptFileException, self).__init__(self.__str__())

    def __str__(self):
        return 'Corrupted File ({0}): {1}'.format(self.file_path, self.message)


class IllegalAliasException(ApiException):

    def __init__(self, alias):
        self.alias = alias
        super(IllegalAliasException, self).__init__(self.__str__())

    def __str__(self):
        return 'Alias is illegal (Must not contain spaces nor path separators)'


class InvalidArgumentsException(ApiException):

    def __init__(self, message):
        self.message = message
        super(InvalidArgumentsException, self).__init__(self.__str__())

    def __str__(self):
        return self.message
