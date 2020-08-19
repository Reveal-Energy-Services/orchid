#  Copyright 2017-2020 Reveal Energy Services, Inc 
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

from collections import namedtuple
import datetime
import unittest
import unittest.mock as mock

from hamcrest import assert_that, equal_to
import numpy as np
import pandas as pd
import pandas.testing as pdt
import toolz.curried as toolz

import orchid.native_well_time_series_adapter as nwtsa
from orchid.net_quantity import as_net_date_time
from orchid.physical_quantity import PhysicalQuantity


StubSample = namedtuple('StubSample', ['Timestamp', 'Value'], module=__name__)


@toolz.curry
def make_raw_sample(start, index, value):
    return start + datetime.timedelta(seconds=30) * index, value


class TestWellTimeSeries(unittest.TestCase):
    def test_canary(self):
        assert_that(2 + 2, equal_to(4))

    def test_name(self):
        expected_display_name = 'excoriaverunt'
        stub_native_well_time_series = mock.MagicMock(name='stub_native_well_time_series')
        stub_native_well_time_series.DisplayName = expected_display_name
        sut = nwtsa.NativeWellTimeSeriesAdapter(stub_native_well_time_series)

        assert_that(sut.display_name, equal_to(expected_display_name))

    def test_sampled_quantity_name(self):
        expected_quantity_name = 'perspici'
        stub_native_well_time_series = mock.MagicMock(name='stub_native_well_time_series')
        stub_native_well_time_series.SampledQuantityName = expected_quantity_name
        sut = nwtsa.NativeWellTimeSeriesAdapter(stub_native_well_time_series)

        assert_that(sut.sampled_quantity_name, equal_to(expected_quantity_name))

    def test_sampled_quantity_type(self):
        native_quantity_types = [68, 83]  # hard-coded UnitsNet.QuantityType.Pressure and Temperature
        physical_quantities = [PhysicalQuantity.PRESSURE, PhysicalQuantity.TEMPERATURE]
        for native_quantity_type, physical_quantity in zip(native_quantity_types, physical_quantities):
            with self.subTest(native_quantity_type=native_quantity_type, physical_quantity=physical_quantity):
                stub_native_well_time_series = mock.MagicMock(name='stub_native_well_time_series')
                stub_native_well_time_series.SampledQuantityType = native_quantity_type
                sut = nwtsa.NativeWellTimeSeriesAdapter(stub_native_well_time_series)

                assert_that(sut.sampled_quantity_type, equal_to(physical_quantity))

    def test_empty_time_series_if_no_samples(self):
        display_name = 'trucem'
        values = []
        start_time_point = datetime.datetime(2021, 4, 2, 15, 17, 57, 510000)
        samples = toolz.pipe(enumerate(values),
                             toolz.map(lambda index_value_pair: (
                                 start_time_point + datetime.timedelta(seconds=30) * index_value_pair[0],
                                 index_value_pair[1])))

        stub_native_well_time_series = mock.MagicMock(name='stub_native_well_time_series')
        stub_native_well_time_series.DisplayName = display_name
        stub_native_well_time_series.GetOrderedTimeSeriesHistory = mock.MagicMock(name='stub_time_series',
                                                                                  return_value=samples)
        sut = nwtsa.NativeWellTimeSeriesAdapter(stub_native_well_time_series)

        expected = pd.Series(data=[], index=[], name=display_name, dtype=np.float64)
        pdt.assert_series_equal(sut.time_series(), expected)

    def test_single_sample_time_series_if_single_sample(self):
        display_name = 'aquilinum'
        values = [26.3945]
        start_time_point = datetime.datetime(2016, 2, 9, 4, 50, 39, 340000)

        make_raw_sample_from_start = make_raw_sample(start_time_point)
        samples = toolz.pipe(enumerate(values),
                             toolz.map(lambda index_value_pair: make_raw_sample_from_start(*index_value_pair)),
                             toolz.map(lambda point_value_pair: (as_net_date_time(point_value_pair[0]),
                                                                 point_value_pair[1])),
                             toolz.map(lambda net_point_value_pair: StubSample(*net_point_value_pair)))

        stub_native_well_time_series = mock.MagicMock(name='stub_native_well_time_series')
        stub_native_well_time_series.DisplayName = display_name
        stub_native_well_time_series.GetOrderedTimeSeriesHistory = mock.MagicMock(name='stub_time_series',
                                                                                  return_value=samples)
        sut = nwtsa.NativeWellTimeSeriesAdapter(stub_native_well_time_series)

        expected_time_points = [start_time_point + n * datetime.timedelta(seconds=30) for n in range(len(values))]
        expected = pd.Series(data=values, index=expected_time_points, name=display_name)
        pdt.assert_series_equal(sut.time_series(), expected)

    def test_many_sample_time_series_if_many_sample(self):
        display_name = 'vulnerabatis'
        values = [75.75, 62.36, 62.69]
        start_time_point = datetime.datetime(2016, 11, 25, 12, 8, 15, 241000)

        make_raw_sample_from_start = make_raw_sample(start_time_point)
        samples = toolz.pipe(enumerate(values),
                             toolz.map(lambda index_value_pair: make_raw_sample_from_start(*index_value_pair)),
                             toolz.map(lambda point_value_pair: (as_net_date_time(point_value_pair[0]),
                                                                 point_value_pair[1])),
                             toolz.map(lambda net_point_value_pair: StubSample(*net_point_value_pair)))

        stub_native_well_time_series = mock.MagicMock(name='stub_native_well_time_series')
        stub_native_well_time_series.DisplayName = display_name
        stub_native_well_time_series.GetOrderedTimeSeriesHistory = mock.MagicMock(name='stub_time_series',
                                                                                  return_value=samples)
        sut = nwtsa.NativeWellTimeSeriesAdapter(stub_native_well_time_series)

        expected_time_points = [start_time_point + n * datetime.timedelta(seconds=30) for n in range(len(values))]
        expected = pd.Series(data=values, index=expected_time_points, name=display_name)
        pdt.assert_series_equal(sut.time_series(), expected)


if __name__ == '__main__':
    unittest.main()
