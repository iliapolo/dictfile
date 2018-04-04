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

import javaproperties
import yaml
from yaml.scanner import ScannerError

from fileconfig.api import exceptions
from fileconfig.api import constants


def load(file_path, fmt):

    with open(file_path) as stream:
        try:
            return loads(stream.read(), fmt=fmt)
        except ScannerError as e:
            raise exceptions.CorruptFileException(file_path=file_path, message=str(e))


def loads(string, fmt):

    if fmt == constants.JSON:

        # we are using 'yaml' here instead of 'json' because json
        # parses the keys as unicode objects (instead of string,
        # see https://stackoverflow.com/questions/956867/how-to-get-string-objects-
        # instead-of-unicode-from-json),
        # which causes a problem with flatdict in identifying complex keys. (see flatdict.py#_
        # has_delimiter (json is a sub-set of yaml so it works)

        return yaml.safe_load(string)

    elif fmt == constants.YAML:

        return yaml.safe_load(string)

    elif fmt == constants.PROPERTIES:

        return javaproperties.loads(string)

    else:

        raise exceptions.UnsupportedFormatException(fmt=fmt)
