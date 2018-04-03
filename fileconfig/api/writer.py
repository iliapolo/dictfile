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

import StringIO
import json

import javaproperties
import yaml

from fileconfig.api import constants
from fileconfig.api import exceptions


def dump(obj, file_path, fmt):

    string = dumps(obj=obj, fmt=fmt)
    with open(file_path, 'w') as stream:
        stream.write(string)


def dumps(obj, fmt):

    if fmt == constants.JSON:
        return json.dumps(obj=obj, indent=2)

    elif fmt == constants.YAML:
        stream = StringIO.StringIO()
        yaml.safe_dump(data=obj, stream=stream, default_flow_style=False)
        return stream.getvalue()

    elif fmt == constants.PROPERTIES:

        # only dictionaries can be represented as a string
        # in the java properties file format
        if not isinstance(obj, dict):
            raise exceptions.InvalidValueTypeException(key=None,
                                                       expected_type=dict,
                                                       actual_type=type(obj))
        for key, value in obj.items():
            if isinstance(value, (dict, list, set)):
                raise exceptions.InvalidValueTypeException(key=key,
                                                           expected_type='str, int, float',
                                                           actual_type=type(value))
            obj[key] = str(value)

        return javaproperties.dumps(props=obj, timestamp=False)

    else:
        raise exceptions.UnsupportedFormatException(fmt=fmt)
