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


import unittest

from hamcrest import assert_that, equal_to, calling, raises
import toolz.curried as toolz

from orchid import (
    measurement as om,
    native_stage_adapter as nsa,
)


# Test ideas
# - Create stage DTO with negative cluster count throws exception
# - Create stage DTO with maybe_isip not a pressure throws exception
# - Create stage DTO with maybe_shmin not a pressure throws exception
class TestCreateStageDto(unittest.TestCase):
    DONT_CARE_STAGE_DETAILS = {
            'stage_no': 22,
            'connection_type': nsa.ConnectionType.PLUG_AND_PERF,
            'md_top': 14582.1 * om.registry.ft,
            'md_bottom': 14720.1 * om.registry.ft,
        }

    def test_canary(self):
        self.assertEqual(2 + 2, 4)

    def test_create_stage_dto_returns_correct_order_of_completion_on_well(self):
        created_stage = nsa.CreateStageDto(**toolz.merge(self.DONT_CARE_STAGE_DETAILS,
                                                         {'stage_no': 34}))

        assert_that(created_stage.order_of_completion_on_well, equal_to(33))

    def test_create_stage_dto_throws_exception_if_stage_no_not_positive(self):
        assert_that(calling(nsa.CreateStageDto).with_args(**toolz.merge(self.DONT_CARE_STAGE_DETAILS,
                                                                        {'stage_no': 0})),
                    raises(ValueError, pattern='Found 0'))

    def test_create_stage_dto_throws_exception_if_md_top_not_length(self):
        assert_that(calling(nsa.CreateStageDto).with_args(**toolz.merge(self.DONT_CARE_STAGE_DETAILS,
                                                                        {'md_top': 227.661 * om.registry.deg})),
                    raises(ValueError,
                           pattern=f'Expected md_top to be a length. Found {(227.661 * om.registry.deg):~P}'))

    def test_create_stage_dto_throws_exception_if_md_bottom_not_length(self):
        assert_that(calling(nsa.CreateStageDto).with_args(**toolz.merge(self.DONT_CARE_STAGE_DETAILS,
                                                                        {'md_bottom': 7260.14 * om.registry.psi})),
                    raises(ValueError,
                           pattern=f'Expected md_bottom to be a length. Found {(7260.14 * om.registry.psi):~P}'))


if __name__ == '__main__':
    unittest.main()
