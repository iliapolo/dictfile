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

import configparser
import json

import six

import javaproperties
import yaml

from dictfile.api import constants
from dictfile.api import exceptions


def dump(obj, file_path, fmt):

    string = dumps(obj=obj, fmt=fmt)
    with open(file_path, 'w') as stream:
        stream.write(string)


def dumps(obj, fmt):

    if fmt == constants.JSON:
        return json.dumps(obj=obj, sort_keys=True, indent=2)

    elif fmt == constants.YAML:
        stream = six.StringIO()
        yaml.safe_dump(data=obj, stream=stream, default_flow_style=False)
        return stream.getvalue()

    elif fmt == constants.PROPERTIES:

        # only dictionaries can be represented as a string
        # in the java properties file format
        if not isinstance(obj, dict):
            raise exceptions.InvalidValueTypeException(expected_types=[dict],
                                                       actual_type=type(obj))
        for key, value in obj.items():
            if isinstance(value, (dict, list, set)):
                raise exceptions.InvalidValueTypeException(expected_types=[str, int, float],
                                                           actual_type=type(value))
            obj[key] = str(value)

        return javaproperties.dumps(props=obj, timestamp=False)

    elif fmt == constants.INI:

        ini_parser = configparser.ConfigParser()
        string = six.StringIO()
        ini_parser.read_dict(dictionary=obj)
        ini_parser.write(fp=string, space_around_delimiters=False)

        return string.getvalue()

    else:
        raise exceptions.UnsupportedFormatException(fmt=fmt)
