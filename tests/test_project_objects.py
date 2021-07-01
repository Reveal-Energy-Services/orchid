#
# This file is part of Orchid and related technologies.
#
# Copyright (c) 2017-2021 Reveal Energy Services.  All Rights Reserved.
#
# LEGAL NOTICE:
# Orchid contains trade secrets and otherwise confidential information
# owned by Reveal Energy Services. Access to and use of this information is 
# strictly limited and controlled by the Company. This file may not be copied,
# distributed, or otherwise disclosed outside of the Company's facilities 
# except under appropriate precautions to maintain the confidentiality hereof, 
# and may not be used in any way not expressly authorized by the Company.
#

import unittest
import uuid

from hamcrest import assert_that, equal_to, contains_exactly
import toolz.curried as toolz

from orchid import (
    native_data_frame_adapter as dfa,
    native_trajectory_adapter as nta,
    project_objects as poc,
)

from tests import stub_net as tsn


# Test ideas
# - Query all names from collection of no .NET DOM objects returns empty sequence
# - Query all names from single-item .NET DOM object collection returns single name
# - Query all names from many-item .NET DOM object collection returns many names
# - Query all display names from collection of no .NET DOM objects returns empty sequence
# - Query all display names from single-item .NET DOM object collection returns single name
# - Query all display names from many-item .NET DOM object collection returns many names
# - Search by id for item in collection returns item with id
# - Search by id for item not in collection returns no item
# - Search collection by name with no match returns empty sequence
# - Search collection by name with only one match returns single DOM object with name
# - Search collection by name with many matching names returns many DOM objects with name
# - Search collection by display name with no match returns empty sequence
# - Search collection by display name with only one match returns single DOM object with display name
# - Search collection by display name with many matches returns many DOM objects with display name
#
# Here are the DOM objects that may be collections:
# - Data frames
# - Monitors
# - Stages
# - Well trajectory
# - Wells
class TestProjectObjects(unittest.TestCase):
    def test_canary(self):
        assert_that(2 + 2, equal_to(4))

    def test_constructed_collection_has_correct_number_of_elements(self):
        for net_items, item_callable in [
            ([], tsn.create_stub_net_data_frame),
            ([{}], tsn.create_stub_net_well_trajectory),
            ([{}, {}, {}], tsn.create_stub_net_well),
        ]:
            with self.subTest(f'Verify {len(net_items)} in collection'):
                sut = create_sut(net_items, item_callable)

                assert_that(len(sut), equal_to(len(net_items)))

    def test_query_all_object_ids_from_collection(self):
        for net_items, item_callable in [
            ([], tsn.create_stub_net_monitor),
            ([{'object_id': 'fbb6edad-2379-4bde-8eac-e42bf472c8f8'}],
             toolz.compose(dfa.NativeDataFrameAdapter, tsn.create_stub_net_data_frame)),
            ([{'object_id': 'a5f8ebd1-d6f2-49c2-aeb5-a8646857f1b7'},
              {'object_id': '83462051-6fb0-4810-92b2-3802fbd55e19'},
              {'object_id': '154af216-6e13-4a10-85ab-24085a674550'}],
             toolz.compose(nta.NativeTrajectoryAdapter, tsn.create_stub_net_well_trajectory)),
        ]:
            with self.subTest(f'Verify {len(net_items)} in collection'):
                sut = create_sut(net_items, item_callable)

                # noinspection PyTypeChecker
                expected = toolz.pipe(net_items,
                                      toolz.map(toolz.get('object_id')),
                                      toolz.map(uuid.UUID),
                                      list)
                actual = list(sut.object_ids())
                # noinspection PyTypeChecker
                assert_that(actual, contains_exactly(*expected))


def create_sut(net_items, create_func):
    return poc.ProjectObjects(create_func, net_items)


if __name__ == '__main__':
    unittest.main()
