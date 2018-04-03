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
import json
import yaml
import StringIO

from fileconfig.api import exceptions
from fileconfig.api.parser import YAML
from fileconfig.api.parser import JSON
from fileconfig.api.parser import PROPERTIES


def write_properties(dproperties, file_path):

    with open(file_path, 'w') as stream:
        javaproperties.dump(props=dproperties, fp=stream, timestamp=False)


def write_json(djson, file_path):

    with open(file_path, 'w') as stream:
        json.dump(obj=djson, fp=stream, indent=2)


def write_yaml(dyaml, file_path):

    with open(file_path, 'w') as stream:
        yaml.safe_dump(data=dyaml, stream=stream, default_flow_style=False)


def write(dictionary, file_path, fmt):

    if fmt.lower() not in [JSON, YAML, PROPERTIES]:
        raise exceptions.UnsupportedFormatException(fmt=fmt)

    if fmt == JSON:
        return write_json(djson=dictionary, file_path=file_path)

    if fmt == YAML:
        return write_yaml(dyaml=dictionary, file_path=file_path)

    if fmt == PROPERTIES:
        return write_properties(dproperties=dictionary, file_path=file_path)


def get_json_string(djson):

    return json.dumps(obj=djson, indent=2)


def get_yaml_string(dyaml):

    stream = StringIO.StringIO()
    yaml.safe_dump(data=dyaml, stream=stream, default_flow_style=False)

    return stream.getvalue()


def get_properties_string(dproperties):
    raise NotImplementedError()


def get_string(dictionary, fmt):

    if fmt.lower() not in [JSON, YAML, PROPERTIES]:
        raise exceptions.UnsupportedFormatException(fmt=fmt)

    if fmt == JSON:
        return get_json_string(djson=dictionary)

    if fmt == YAML:
        return get_yaml_string(dyaml=dictionary)

    if fmt == PROPERTIES:
        return get_properties_string(dproperties=dictionary)
