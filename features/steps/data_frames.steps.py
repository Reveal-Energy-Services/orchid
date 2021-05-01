#  Copyright 2017-2021 Reveal Energy Services, Inc
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

# noinspection PyPackageRequirements
from behave import *
use_step_matcher("parse")

import uuid

from hamcrest import assert_that, not_none, equal_to, has_length
import toolz.curried as toolz


@when("I query the data frames for the project for '{field}'")
def step_impl(context, field):
    """
    Args:
        context (behave.runner.Context): The test context.
        field (str): The name of the field of the loaded project.
    """
    context.project_data_frames = context.project.data_frames()


@then("I see a single data frame identified by {object_id}, {name} and {display_name}")
def step_impl(context, object_id, name, display_name):
    """
    Args:
        context (behave.runner.Context): The test context.
        object_id (str): The textual representation of the UUID identifying the data frame of interest.
        name (str): The name of the data frame of interest.
        display_name (str): The name of the data frame of interest used for display purposes.
    """
    data_frame_object_id = _as_uuid(object_id)
    data_frame_of_interest = _find_data_frame_by_id(data_frame_object_id, context.project_data_frames)
    assert_that(data_frame_of_interest, not_none())

    assert_that(data_frame_of_interest.object_id, equal_to(data_frame_object_id))
    assert_that(data_frame_of_interest.name, equal_to(name))
    assert_that(data_frame_of_interest.display_name, equal_to(display_name))


@when("I query the loaded project for the data frame named '{data_frame_name}'")
def step_impl(context, data_frame_name):
    """
    Args:
        context (behave.runner.Context): The test context.
        data_frame_name (str): The name of the data frame of interest.
    """
    candidates = list(context.project.data_frames_by_name(data_frame_name))
    assert_that(len(candidates), equal_to(1))

    context.data_frame = candidates[0]


@then("I see the sampled cells")
def step_impl(context):
    """
    Args:
        context (behave.runner.Context): The test context
    """
    for expected_sample in context.table:
        sample_no = int(expected_sample['sample'])
        for table_column in context.table.headings:
            frame_column = _table_column_to_data_frame_column(table_column)
            actual_cell = context.data_frame.pandas_data_frame().iloc[sample_no, :][frame_column]
            assert_that(actual_cell, equal_to(expected_sample[table_column]))


# TODO: Adapted from `dot_net_dom_access.py`
def _as_uuid(guid_text: str):
    return uuid.UUID(guid_text)


def _table_column_to_data_frame_column(table_column_name):
    """
    Convert a table column heading ta a data frame column heading.

    Args:
        table_column_name: The expected table column heading.

    Returns:
        The data frame column name corresponding to `table_column_name`.
    """
    table_data_frame_columns = {
        'sample': 'Sample',
        'sh_easting': 'Surface  Hole Easting',
        'bh_northing': 'Bottom Hole Northing ',
        'bh_tdv': 'Bottom Hole TDV ',
        'stage_no': 'StageNumber',
        'stage_length': 'StageLength',
        'p_net': 'Pnet',
    }
    return toolz.get(table_column_name, table_data_frame_columns)


def _find_data_frame_by_id(object_id, data_frames):
    candidates = toolz.pipe(
        data_frames,
        toolz.filter(lambda df: df.object_id == object_id),
        list
    )
    assert_that(candidates, has_length(1))

    return toolz.first(candidates)
