#  Copyright 2017-2022 Reveal Energy Services, Inc 
#
#  Licensed under the Apache License, Version 2.0 (the "License"); 
#  you may not use this file except in compliance with the License. 
#  You may obtain a copy of the License at 
#
#      http://www.apache.org/licenses/LICENSE-2.0 
#
#  Unless required by applicable law or agreed to in writing, software 
#  distributed under the License is distributed on an "AS IS" BASIS, 
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
#  See the License for the specific language governing permissions and 
#  limitations under the License. 
#
# This file is part of Orchid and related technologies.
#


import shutil


import orchid


def test_save_project(benchmark):
    load_path = orchid.training_data_path().joinpath('Project_frankNstein_Permian_UTM13_FEET.ifrac')
    loaded_project = orchid.load_project(str(load_path))
    save_path = orchid.training_data_path().joinpath('Project_frankNstein_Permian_UTM13_FEET.benchmark.ifrac')
    benchmark(orchid.save_project, loaded_project, str(save_path))
    save_path.unlink()


def test_optimized_but_possibly_unsafe_save_new_file(benchmark):
    load_path = orchid.training_data_path().joinpath('Project_frankNstein_Permian_UTM13_FEET.ifrac')
    loaded_project = orchid.load_project(str(load_path))
    save_path = orchid.training_data_path().joinpath('Project_frankNstein_Permian_UTM13_FEET.benchmark.ifrac')
    benchmark(orchid.optimized_but_possibly_unsafe_save, loaded_project, str(load_path), str(save_path))
    save_path.unlink()


def test_optimized_but_possibly_unsafe_save_same_file(benchmark):
    source_path = orchid.training_data_path().joinpath('Project_frankNstein_Permian_UTM13_FEET.ifrac')
    load_path = orchid.training_data_path().joinpath('Project_frankNstein_Permian_UTM13_FEET.benchmark.ifrac')
    shutil.copyfile(source_path, load_path)
    loaded_project = orchid.load_project(str(load_path))
    benchmark(orchid.optimized_but_possibly_unsafe_save, loaded_project, str(load_path))
    load_path.unlink()
