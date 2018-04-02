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


def write_properties(dproperties, filename):

    javaproperties.dump(props=dproperties, fp=open(filename, 'w'), timestamp=False)


def write_json(djson, filename):

    json.dump(obj=djson, fp=open(filename, 'w'), indent=2)


def write_yaml(dyaml, filename):

    yaml.safe_dump(data=dyaml, stream=open(filename, 'w'), default_flow_style=False)


def get_json_string(djson):

    return json.dumps(obj=djson, indent=2)


def get_yaml_string(dyaml):

    stream = StringIO.StringIO()
    yaml.safe_dump(data=dyaml, stream=stream, default_flow_style=False)

    return stream.getvalue()
