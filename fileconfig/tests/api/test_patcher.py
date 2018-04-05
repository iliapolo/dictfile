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

# pylint: disable=too-many-public-methods

import pytest

from fileconfig.api.patcher import Patcher
from fileconfig.api import exceptions, writer
from fileconfig.api import constants


def test_delete():

    dictionary = {'key1': 'value1', 'key2': 'value2'}

    expected_dictionary = {'key2': 'value2'}

    patcher = Patcher(dictionary)
    dictionary = patcher.delete('key1').finish()

    assert expected_dictionary == dictionary


def test_delete_complex_key():

    dictionary = {
        'key1': {
            'key2': 'value1',
            'key3': 'value2'
        }
    }

    expected_dictionary = {
        'key1': {
            'key2': 'value1'
        }
    }

    patcher = Patcher(dictionary)
    dictionary = patcher.delete('key1:key3').finish()

    assert expected_dictionary == dictionary


def test_set():

    dictionary = {'key1': 'value1'}

    expected_dictionary = {'key1': 'value2'}

    patcher = Patcher(dictionary)
    dictionary = patcher.set('key1', 'value2').finish()

    assert expected_dictionary == dictionary


def test_set_unicode():

    dictionary = {'key1': 'value1'}

    expected_dictionary = {'key1': 'value2'}

    patcher = Patcher(dictionary)
    dictionary = patcher.set('key1', u'value2').finish()

    assert expected_dictionary == dictionary


def test_set_not_string():

    dictionary = {'key1': 'value1'}

    patcher = Patcher(dictionary)
    with pytest.raises(exceptions.InvalidValueTypeException):
        patcher.set('key1', 5).finish()


def test_set_dict():

    dictionary = {'key1': 'value1'}

    expected_dictionary = {
        'key1': {
            'key2': 'value2'
        }}

    patcher = Patcher(dictionary)
    dictionary = patcher.set('key1', '{"key2":"value2"}').finish()

    assert expected_dictionary == dictionary


def test_set_list():

    dictionary = {'key1': 'value1'}

    expected_dictionary = {
        'key1': ['value1', 'value2']
    }

    patcher = Patcher(dictionary)
    dictionary = patcher.set('key1', '["value1", "value2"]').finish()

    assert expected_dictionary == dictionary


def test_set_integer():

    dictionary = {'key1': 'value1'}

    expected_dictionary = {
        'key1': 5
    }

    patcher = Patcher(dictionary)
    dictionary = patcher.set('key1', '5').finish()

    assert expected_dictionary == dictionary


def test_set_float():

    dictionary = {'key1': 'value1'}

    expected_dictionary = {
        'key1': 5.5
    }

    patcher = Patcher(dictionary)
    dictionary = patcher.set('key1', '5.5').finish()

    assert expected_dictionary == dictionary


def test_set_complex_key_compound_value():

    dictionary = {
        'key1': {
            'key2': 'value1'
        }
    }

    expected_dictionary = {
        'key1': {
            'key2': {
                'key3': 'value2'
            }
        }}

    patcher = Patcher(dictionary)
    dictionary = patcher.set('key1:key2', '{"key3":"value2"}').finish()

    assert expected_dictionary == dictionary


def test_set_non_existing_one_level_complex_key():

    dictionary = {
        'key1': {
            'key2': 'value1'
        }
    }

    expected_dictionary = {
        'key1': {
            'key2': 'value1',
            'key3': 'value2'
        }
    }

    patcher = Patcher(dictionary)
    dictionary = patcher.set('key1:key3', 'value2').finish()

    assert expected_dictionary == dictionary


def test_set_existing_one_level_complex_key():

    dictionary = {
        'key1': {
            'key2': 'value1'
        }
    }

    expected_dictionary = {
        'key1': {
            'key2': 'value2'
        }
    }

    patcher = Patcher(dictionary)
    dictionary = patcher.set('key1:key2', 'value2').finish()

    assert expected_dictionary == dictionary


def test_set_non_existing_two_level_complex_key():

    dictionary = {
        'key1': {
            'key2': {
                'key3': 'value1'
            }
        }
    }

    expected_dictionary = {
        'key1': {
            'key2': {
                'key3': 'value1',
                'key4': 'value2'
            }
        }
    }

    patcher = Patcher(dictionary)
    dictionary = patcher.set('key1:key2:key4', 'value2').finish()

    assert expected_dictionary == dictionary


def test_set_existing_two_level_complex_key():

    dictionary = {
        'key1': {
            'key2': {
                'key3': 'value1'
            }
        }
    }

    expected_dictionary = {
        'key1': {
            'key2': {
                'key3': 'value2'
            }
        }
    }

    patcher = Patcher(dictionary)
    dictionary = patcher.set('key1:key2:key3', 'value2').finish()

    assert expected_dictionary == dictionary


def test_get_existing_two_level_complex_key():

    dictionary = {
        'key1': {
            'key2': {
                'key3': 'value1'
            }
        }
    }

    expected_value = 'value1'

    patcher = Patcher(dictionary)
    value = patcher.get('key1:key2:key3')

    assert expected_value == value


def test_get_existing_one_level_complex_key():

    dictionary = {
        'key1': {
            'key2': 'value1'
        }
    }

    expected_value = 'value1'

    patcher = Patcher(dictionary)
    value = patcher.get('key1:key2')

    assert expected_value == value


def test_get_ini_section():

    dictionary = {
        'section': {
            'key1': 'key2'
        }
    }

    expected_value = writer.dumps(obj={'key1': 'key2'}, fmt=constants.PROPERTIES)

    patcher = Patcher(dictionary)
    value = patcher.get('section', fmt=constants.INI)

    assert expected_value == value


def test_get_string():

    dictionary = {
        'key1': 'value1'
    }

    expected_value = 'value1'

    patcher = Patcher(dictionary)
    value = patcher.get('key1')

    assert expected_value == value


def test_get_integer():

    dictionary = {
        'key1': 5
    }

    expected_value = '5'

    patcher = Patcher(dictionary)
    value = patcher.get('key1')

    assert expected_value == value


def test_get_float():

    dictionary = {
        'key1': 5.5
    }

    expected_value = '5.5'

    patcher = Patcher(dictionary)
    value = patcher.get('key1')

    assert expected_value == value


def test_get_compund_object_unsupported_format():

    dictionary = {
        'key1': ['value1', 'value2']
    }

    patcher = Patcher(dictionary)

    with pytest.raises(exceptions.UnsupportedFormatException):
        patcher.get('key1', fmt='unsupported')


def test_get_list_as_json():

    dictionary = {
        'key1': ['value1', 'value2']
    }

    expected_value = '''[
  "value1", 
  "value2"
]'''

    patcher = Patcher(dictionary)
    value = patcher.get('key1')

    assert expected_value == value


def test_get_list_as_yaml():

    dictionary = {
        'key1': ['value1', 'value2']
    }

    expected_value = '''- value1
- value2\n'''

    patcher = Patcher(dictionary)
    value = patcher.get('key1', fmt=constants.YAML)

    assert expected_value == value


def test_get_dict_as_json():

    dictionary = {
        'key1': {
            'key2': 'value1'
        }
    }

    expected_value = '''{
  "key2": "value1"
}'''

    patcher = Patcher(dictionary)
    value = patcher.get('key1')

    assert expected_value == value


def test_get_dict_as_yaml():

    dictionary = {
        'key1': {
            'key2': 'value1'
        }
    }

    expected_value = 'key2: value1\n'

    patcher = Patcher(dictionary)
    value = patcher.get('key1', fmt=constants.YAML)

    assert expected_value == value


def test_get_non_existing_two_level_complex_key():

    dictionary = {
        'key1': {
            'key2': {
                'key3': 'value1'
            }
        }
    }

    patcher = Patcher(dictionary)

    with pytest.raises(exceptions.KeyNotFoundException):
        patcher.get('key1:key2:key4')


def test_delete_non_existing_key():

    dictionary = {'key': 'value'}

    patcher = Patcher(dictionary)

    with pytest.raises(exceptions.KeyNotFoundException):
        patcher.delete('non-existing')


def test_add():

    dictionary = {'key': ['value1']}

    expected_dictionary = {'key': ['value1', 'value2']}

    patcher = Patcher(dictionary)
    patcher.add(key='key', value='value2')

    assert expected_dictionary == dictionary


def test_add_to_complex_key():

    dictionary = {
        'key1': {
            'key2': ['value1']
        }
    }

    expected_dictionary = {
        'key1': {
            'key2': ['value1', 'value2']
        }
    }

    patcher = Patcher(dictionary)
    patcher.add(key='key1:key2', value='value2')

    assert expected_dictionary == dictionary


def test_add_to_non_list():

    dictionary = {'key': 'value1'}

    patcher = Patcher(dictionary)

    with pytest.raises(exceptions.InvalidKeyTypeException):
        patcher.add(key='key', value='value2')


def test_remove_from_complex_key():

    dictionary = {
        'key1': {
            'key2': ['value1', 'value2']
        }
    }

    expected_dictionary = {
        'key1': {
            'key2': ['value1']
        }
    }

    patcher = Patcher(dictionary)
    patcher.remove(key='key1:key2', value='value2')

    assert expected_dictionary == dictionary


def test_remove():

    dictionary = {
        'key1': ['value1', 'value2']
    }

    expected_dictionary = {
        'key1': ['value1']
    }

    patcher = Patcher(dictionary)
    patcher.remove(key='key1', value='value2')

    assert expected_dictionary == dictionary
