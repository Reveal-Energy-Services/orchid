#
# This file is part of IMAGEFrac (R) and related technologies.
#
# Copyright (c) 2017-2020 Reveal Energy Services.  All Rights Reserved.
#
# LEGAL NOTICE:
# IMAGEFrac contains trade secrets and otherwise confidential information
# owned by Reveal Energy Services. Access to and use of this information is
# strictly limited and controlled by the Company. This file may not be copied,
# distributed, or otherwise disclosed outside of the Company's facilities
# except under appropriate precautions to maintain the confidentiality hereof,
# and may not be used in any way not expressly authorized by the Company.
#

import datetime
import unittest

from hamcrest import assert_that, is_, equal_to
import pandas as pd

from orchid.time_series import transform_net_time_series

from tests.stub_net import StubNetSample


def create_30_second_time_points(start_time_point: datetime.datetime, count: int):
    """
    Create a sequence of `count` time points, 30-seconds apart.
    :param start_time_point: The starting time point of the sequence.
    :param count: The number of time points in the sequence.
    :return: The sequence of time points.
    """
    return [start_time_point + i * datetime.timedelta(seconds=30) for i in range(count)]


def create_time_series(sample_values, start_time_point):
    sample_time_points = create_30_second_time_points(start_time_point, len(sample_values))
    samples = [StubNetSample(st, sv) for (st, sv) in zip(sample_time_points, sample_values)]
    return samples


class TestTimeSeries(unittest.TestCase):
    def test_canary(self):
        assert_that(2 + 2, is_(equal_to(4)))

    def test_time_series_transform_returns_no_items_when_no_net_samples(self):
        sample_values = []
        actual_time_series = transform_net_time_series(sample_values)

        assert_that(actual_time_series.empty, is_(True))

    def test_time_series_transform_returns_one_item_when_one_net_samples(self):
        start_time_point = datetime.datetime(2021, 7, 30, 15, 44, 22)
        sample_values = [3.684]
        net_time_series = create_time_series(sample_values, start_time_point)
        actual_time_series = transform_net_time_series(net_time_series)

        pd.testing.assert_series_equal(actual_time_series,
                                       pd.Series(data=sample_values,
                                                 index=create_30_second_time_points(start_time_point,
                                                                                    len(sample_values))))

    def test_time_series_transform_returns_many_items_when_many_net_samples(self):
        start_time_point = datetime.datetime(2018, 11, 7, 17, 50, 18)
        sample_values = [68.67, 67.08, 78.78]
        net_time_series = create_time_series(sample_values, start_time_point)
        actual_time_series = transform_net_time_series(net_time_series)

        pd.testing.assert_series_equal(actual_time_series,
                                       pd.Series(data=sample_values,
                                                 index=create_30_second_time_points(start_time_point,
                                                                                    len(sample_values))))


if __name__ == '__main__':
    unittest.main()
