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

import datetime as dt
import unittest
import uuid

import dateutil.parser as dup
from hamcrest import assert_that, equal_to
import pandas as pd
import pandas.testing as pdt
import toolz.curried as toolz

from orchid import native_data_frame_adapter as dfa

from tests import stub_net as tsn


# Test ideas
# - DataTable with DateTime column produces DataFrame with correct datetime cells
# - DataTable with DBNull cells produces DataFrame with corresponding cells containing `None`
class TestNativeDataFrameAdapter(unittest.TestCase):
    def test_canary(self):
        assert_that(2 + 2, equal_to(4))

    def test_display_name(self):
        for net_display_name, expected_display_name in [('lucrum', 'lucrum'), (None, 'Not set')]:
            with self.subTest(f'Testing .NET display name, "{net_display_name}",'
                              f' and display name "{expected_display_name}"'):
                stub_net_data_frame = tsn.create_stub_net_data_frame(display_name=net_display_name)
                sut = dfa.NativeDataFrameAdapter(stub_net_data_frame)

                assert_that(sut.display_name, equal_to(expected_display_name))

    def test_name(self):
        stub_net_data_frame = tsn.create_stub_net_data_frame(name='avus')
        sut = dfa.NativeDataFrameAdapter(stub_net_data_frame)

        assert_that(sut.name, equal_to('avus'))

    def test_object_id(self):
        stub_net_data_frame = tsn.create_stub_net_data_frame(object_id='35582fd2-7499-4259-99b8-04b01876f309')
        sut = dfa.NativeDataFrameAdapter(stub_net_data_frame)

        assert_that(sut.object_id, equal_to(uuid.UUID('35582fd2-7499-4259-99b8-04b01876f309')))

    def test_empty_data_table_produces_empty_pandas_data_frame(self):
        stub_net_data_frame = tsn.create_stub_net_data_frame(table_data_dto=tsn.TableDataDto([], [], toolz.identity))
        sut = dfa.NativeDataFrameAdapter(stub_net_data_frame)

        pdt.assert_frame_equal(sut.pandas_data_frame(), pd.DataFrame())

    def test_single_cell_data_table_produces_correct_pandas_data_frame(self):
        table_data_dto = tsn.TableDataDto([float], [{'oratio': 57.89}], toolz.identity)
        stub_net_data_frame = tsn.create_stub_net_data_frame(table_data_dto=table_data_dto)
        sut = dfa.NativeDataFrameAdapter(stub_net_data_frame)

        actual_data_frame = sut.pandas_data_frame()
        expected_data_frame = pd.DataFrame(data=toolz.merge_with(toolz.identity, *table_data_dto.table_data),
                                           columns=toolz.first(table_data_dto.table_data).keys())
        pdt.assert_frame_equal(actual_data_frame, expected_data_frame)

    def test_single_cell_data_table_with_column_mapping_produces_correct_pandas_data_frame(self):
        rename_column_func = toolz.flip(toolz.get)({'stultus': 'fulmino'})
        table_data_dto = tsn.TableDataDto([str], [{'stultus': 'timeo'}], rename_column_func)
        stub_net_data_frame = tsn.create_stub_net_data_frame(table_data_dto=table_data_dto)
        sut = dfa.NativeDataFrameAdapter(stub_net_data_frame)

        actual_data_frame = sut.pandas_data_frame()

        expected_data = toolz.keymap(rename_column_func, toolz.merge_with(toolz.identity, *table_data_dto.table_data))
        expected_columns = list(toolz.map(rename_column_func, toolz.first(table_data_dto.table_data).keys()))
        expected_data_frame = pd.DataFrame(data=expected_data,
                                           columns=expected_columns)
        pdt.assert_frame_equal(actual_data_frame, expected_data_frame)

    def test_single_column_many_rows_data_table_produces_correct_pandas_data_frame(self):
        table_data_dto = tsn.TableDataDto([str],
                                          [{'rident': 'pauci'},
                                           {'rident': 'sapientes'},
                                           {'rident': 'rident'}],
                                          toolz.identity)
        stub_net_data_frame = tsn.create_stub_net_data_frame(table_data_dto=table_data_dto)
        sut = dfa.NativeDataFrameAdapter(stub_net_data_frame)

        actual_data_frame = sut.pandas_data_frame()
        expected_data_frame = pd.DataFrame(data=toolz.merge_with(toolz.identity, *table_data_dto.table_data),
                                           columns=toolz.first(table_data_dto.table_data).keys())
        pdt.assert_frame_equal(actual_data_frame, expected_data_frame)

    def test_single_column_many_rows_data_table_with_column_mapping_produces_correct_pandas_data_frame(self):
        rename_column_func = toolz.flip(toolz.get)({'rident': 'hic'})
        table_data_dto = tsn.TableDataDto([str],
                                          [{'rident': 'pauci'},
                                           {'rident': 'sapientes'},
                                           {'rident': 'rident'}],
                                          rename_column_func)
        stub_net_data_frame = tsn.create_stub_net_data_frame(table_data_dto=table_data_dto)
        sut = dfa.NativeDataFrameAdapter(stub_net_data_frame)

        actual_data_frame = sut.pandas_data_frame()
        expected_data = toolz.keymap(rename_column_func, toolz.merge_with(toolz.identity, *table_data_dto.table_data))
        expected_columns = list(toolz.map(rename_column_func, toolz.first(table_data_dto.table_data).keys()))
        expected_data_frame = pd.DataFrame(data=expected_data,
                                           columns=expected_columns)
        pdt.assert_frame_equal(actual_data_frame, expected_data_frame)

    def test_many_columns_single_row_data_table_produces_correct_pandas_data_frame(self):
        table_data_dto = tsn.TableDataDto([str, float, int],
                                          [{'nespila': 'pendet', 'scrupum': -23.14, 'nascor': -116}],
                                          toolz.identity)
        stub_net_data_frame = tsn.create_stub_net_data_frame(table_data_dto=table_data_dto)
        sut = dfa.NativeDataFrameAdapter(stub_net_data_frame)

        actual_data_frame = sut.pandas_data_frame()
        expected_data_frame = pd.DataFrame(data=toolz.merge_with(toolz.identity, *table_data_dto.table_data),
                                           columns=toolz.first(table_data_dto.table_data).keys())
        pdt.assert_frame_equal(actual_data_frame, expected_data_frame)

    def test_many_columns_single_row_data_table_with_column_mapping_produces_correct_pandas_data_frame(self):
        rename_column_func = toolz.flip(toolz.get)({'Servius': 'calcaverimus',
                                                    'onus': 'Patavium',
                                                    'timoris': 'timoris'})
        table_data_dto = tsn.TableDataDto([float, int, str],
                                          [{'Servius': 3.414, 'onus': 8, 'timoris': 'alescet'}],
                                          rename_column_func)
        stub_net_data_frame = tsn.create_stub_net_data_frame(table_data_dto=table_data_dto)
        sut = dfa.NativeDataFrameAdapter(stub_net_data_frame)

        actual_data_frame = sut.pandas_data_frame()
        expected_data = toolz.keymap(rename_column_func, toolz.merge_with(toolz.identity, *table_data_dto.table_data))
        expected_columns = list(toolz.map(rename_column_func, toolz.first(table_data_dto.table_data).keys()))
        expected_data_frame = pd.DataFrame(data=expected_data,
                                           columns=expected_columns)
        pdt.assert_frame_equal(actual_data_frame, expected_data_frame)

    def test_many_columns_many_rows_data_table_produces_correct_pandas_data_frame(self):
        table_data_dto = tsn.TableDataDto([str, int, float],
                                          [{'cana': 'imbris', 'querula': -203, 'recidebimus': 8.700},
                                           {'cana': 'privat', 'querula': 111, 'recidebimus': 52.02},
                                           {'cana': 'desperant', 'querula': -44, 'recidebimus': 19.52}],
                                          toolz.identity)
        stub_net_data_frame = tsn.create_stub_net_data_frame(table_data_dto=table_data_dto)
        sut = dfa.NativeDataFrameAdapter(stub_net_data_frame)

        actual_data_frame = sut.pandas_data_frame()
        expected_data_frame = pd.DataFrame(data=toolz.merge_with(toolz.identity, *table_data_dto.table_data),
                                           columns=toolz.first(table_data_dto.table_data).keys())
        pdt.assert_frame_equal(actual_data_frame, expected_data_frame)

    def test_many_columns_many_rows_data_table_with_column_mapping_produces_correct_pandas_data_frame(self):
        rename_column_func = toolz.flip(toolz.get)({'commoda': 'Manius', 'mutabilis': 'annui', 'lenit': 'lenit'})
        table_data_dto = tsn.TableDataDto([int, str, float],
                                          [{'mutabilis': 6, 'lenit': 'imbris', 'commoda': 31.71},
                                           {'mutabilis': 52, 'lenit': 'privat', 'commoda': 65.52},
                                           {'mutabilis': 36, 'lenit': 'desperant', 'commoda': -95.01}],
                                          rename_column_func)
        stub_net_data_frame = tsn.create_stub_net_data_frame(table_data_dto=table_data_dto)
        sut = dfa.NativeDataFrameAdapter(stub_net_data_frame)

        actual_data_frame = sut.pandas_data_frame()
        expected_data = toolz.keymap(rename_column_func, toolz.merge_with(toolz.identity, *table_data_dto.table_data))
        expected_columns = list(toolz.map(rename_column_func, toolz.first(table_data_dto.table_data).keys()))
        expected_data_frame = pd.DataFrame(data=expected_data,
                                           columns=expected_columns)
        pdt.assert_frame_equal(actual_data_frame, expected_data_frame)

    @unittest.skip('failing date time column')
    def test_single_cell_data_table_with_date_time_column_produces_correct_pandas_data_frame(self):
        rename_column_func = toolz.flip(toolz.get)({'pulchritudo': 'probum'})
        table_data_dto = tsn.TableDataDto([dt.datetime],
                                          [{'pulchritudo': dup.isoparse('2024-03-15T10:09:18Z')}],
                                          rename_column_func)
        # TODO: Repair this test that will fail.
        # This failure occurs because Python.NET helpfully converts a value `DateTimeKind`, a .NET `Enum`,
        # to a Python `int`. Because of this conversion, Python.NET calls the incorrect overload of the
        # .NET `DateTime` constructor. It cannot distinguish between a `DateTimeKind` converted to an `int`
        # and attempting to set the `Millisecond` property.
        #
        # Because of the number of changes needed to reliably address this issue, I plan to create a
        # separate story and branch and then return.
        #
        # Note that these changes affect the DBNull test also (because that test includes a `DateTime` column.
        #
        stub_net_data_frame = tsn.create_stub_net_data_frame(table_data_dto=table_data_dto)
        sut = dfa.NativeDataFrameAdapter(stub_net_data_frame)

        actual_data_frame = sut.pandas_data_frame()
        expected_data = toolz.keymap(rename_column_func, toolz.merge_with(toolz.identity, *table_data_dto.table_data))
        expected_columns = list(toolz.map(rename_column_func, toolz.first(table_data_dto.table_data).keys()))
        expected_data_frame = pd.DataFrame(data=expected_data,
                                           columns=expected_columns)
        pdt.assert_frame_equal(actual_data_frame, expected_data_frame)

    @unittest.skip('failing db null')
    def test_many_columns_many_rows_data_table_with_db_null_values_produces_correct_pandas_data_frame(self):
        table_data_dto = tsn.TableDataDto(
            [str, float, dt.datetime, int],
            [
                {
                    'vitis': None,
                    'controversum': -14.52,
                    'indicis': dt.datetime.now(dt.timezone.utc),
                    'inane': -92,
                },
                {
                    'vitis': 'magistri',
                    'controversum': None,
                    'indicis': dt.datetime.now(dt.timezone.utc),
                    'inane': 169,
                },
                {
                    'vitis': 'inter cenam',
                    'controversum': -73.83,
                    'indicis': None,
                    'inane': 148,
                },
                {
                    'vitis': 'profuit',
                    'controversum': -40.88,
                    'indicis': dt.datetime.now(dt.timezone.utc),
                    'inane': None,
                },
            ],
            toolz.identity)
        stub_net_data_frame = tsn.create_stub_net_data_frame(table_data_dto=table_data_dto)
        sut = dfa.NativeDataFrameAdapter(stub_net_data_frame)

        actual_data_frame = sut.pandas_data_frame()
        expected_data_frame = pd.DataFrame(data=toolz.merge_with(toolz.identity, *table_data_dto.table_data),
                                           columns=toolz.first(table_data_dto.table_data).keys())
        pdt.assert_frame_equal(actual_data_frame, expected_data_frame)


if __name__ == '__main__':
    unittest.main()
