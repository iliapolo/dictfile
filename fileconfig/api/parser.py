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


def parse_properties(sproperties):

    return javaproperties.loads(sproperties)


def parse_json(sjson):

    # we are using 'yaml' here instead of 'json' because json
    # parses the keys as unicode objects (instead of string,
    # see https://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-from-json),
    # which causes a problem with flatdict in identifying complex keys. (see flatdict.py#_has_delimiter
    # (json is a sub-set of yaml so it works)

    return parse_yaml(sjson)


def parse_yaml(syaml):

    return yaml.safe_load(syaml)
