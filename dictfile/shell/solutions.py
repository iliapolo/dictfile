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

from dictfile.api import constants


def edit_manually():

    return 'Edit the file manually and correct it.'


def reset_to_latest(alias):

    return 'Reset the file to its last working version by running: {} repository reset ' \
           '--alias {} --version latest'.format(constants.PROGRAM_NAME, alias)


def commit(alias):

    return 'Commit the current contents by running: {} repository commit --alias {}'\
           .format(constants.PROGRAM_NAME, alias)
