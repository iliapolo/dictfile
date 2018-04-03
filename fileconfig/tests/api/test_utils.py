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

import os
import tempfile
import shutil

from fileconfig.api import utils


def test_lsd():

    temp_dir = tempfile.mkdtemp()
    os.makedirs(os.path.join(temp_dir, 'dir1'))
    os.makedirs(os.path.join(temp_dir, 'dir2'))
    with open(os.path.join(temp_dir, 'file1'), 'w') as stream:
        stream.write('hello')

    lsd = utils.lsd(temp_dir)

    assert {'dir1', 'dir2'} == set(lsd)


def test_lsf():

    temp_dir = tempfile.mkdtemp()
    os.makedirs(os.path.join(temp_dir, 'dir1'))
    os.makedirs(os.path.join(temp_dir, 'dir2'))
    with open(os.path.join(temp_dir, 'file1'), 'w') as stream:
        stream.write('hello')

    lsf = utils.lsf(temp_dir)

    assert {'file1'} == set(lsf)


def test_smkdir_directory_exists():

    temp_dir = tempfile.mkdtemp()
    utils.smkdir(temp_dir)


def test_smkdir_directory_does_not_exist():

    temp_dir = tempfile.mkdtemp()
    shutil.rmtree(temp_dir)

    utils.smkdir(temp_dir)

    assert os.path.isdir(temp_dir)
