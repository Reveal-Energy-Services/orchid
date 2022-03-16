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


import unittest
import uuid

from hamcrest import assert_that, equal_to, is_, none

from orchid import (
    native_project_user_data_adapter as uda,
    net_stage_qc as nqc,
)

from tests import stub_net as tsn


# Test ideas
# - Raise error if failed to supplied stage ID is None
class TestNativeProjectUserDataAdapter(unittest.TestCase):
    def test_canary(self):
        self.assertEqual(2 + 2, 4)

    def test_stage_qc_has_correct_stage_id_if_stage_id_and_start_stop_confirmation_in_user_data(self):
        stage_id_dto = '78edb717-0528-4710-8b61-15ebc8f283c1'
        key = nqc.make_start_stop_confirmation_key(stage_id_dto)
        value = {'Type': 'System.String', 'Value': 'Confirmed'}
        stub_project_user_data = tsn.ProjectUserDataDto(to_json={key: value}).create_net_stub()
        sut = uda.NativeProjectUserData(stub_project_user_data)

        assert_that(sut.stage_qc(uuid.UUID(stage_id_dto)).stage_id, equal_to(uuid.UUID(stage_id_dto)))

    def test_stage_qc_has_correct_stage_id_if_stage_id_and_qc_notes_in_user_data(self):
        stage_id_dto = 'c93dcd1a-b156-46b6-b7fd-3d0c8205675c'
        key = nqc.make_qc_notes_key(stage_id_dto)
        value = {'Type': 'System.String', 'Value': 'animus meus aedificio repudiat'}
        stub_project_user_data = tsn.ProjectUserDataDto(to_json={key: value}).create_net_stub()
        sut = uda.NativeProjectUserData(stub_project_user_data)

        assert_that(sut.stage_qc(uuid.UUID(stage_id_dto)).stage_id, equal_to(uuid.UUID(stage_id_dto)))

    def test_stage_qc_is_none_if_stage_id_not_in_user_data_but_user_data_not_empty(self):
        key = nqc.make_start_stop_confirmation_key(tsn.DONT_CARE_ID_A)
        value = {'Type': 'System.String', 'Value': 'Unconfirmed'}
        stub_project_user_data = tsn.ProjectUserDataDto(to_json={key: value}).create_net_stub()
        sut = uda.NativeProjectUserData(stub_project_user_data)

        sought_stage_id = uuid.UUID('a53695d4-df87-419a-8ede-ce151383d527')
        assert_that(sut.stage_qc(sought_stage_id), is_(none()))

    def test_stage_qc_is_none_if_neither_stage_id_nor_notes_nor_start_stop_confirmation_available(self):
        stub_project_user_data = tsn.ProjectUserDataDto(to_json={}).create_net_stub()
        sut = uda.NativeProjectUserData(stub_project_user_data)

        sought_stage_id = uuid.UUID('05573bcc-be82-4243-954e-0815bb25fa70')
        assert_that(sut.stage_qc(sought_stage_id), is_(none()))


if __name__ == '__main__':
    unittest.main()
