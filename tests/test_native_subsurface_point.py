#
# This file is part of Orchid and related technologies.
#
# Copyright (c) 2017-2020 Reveal Energy Services.  All Rights Reserved.
#
# LEGAL NOTICE:
# Orchid contains trade secrets and otherwise confidential information
# owned by Reveal Energy Services. Access to and use of this information is 
# strictly limited and controlled by the Company. This file may not be copied,
# distributed, or otherwise disclosed outside of the Company's facilities 
# except under appropriate precautions to maintain the confidentiality hereof, 
# and may not be used in any way not expressly authorized by the Company.
#

import unittest.mock

from hamcrest import assert_that, equal_to
import toolz.curried as toolz

import orchid.measurement as om
import orchid.native_subsurface_point as nsp
import orchid.reference_origins as origins
import orchid.unit_system as units

import tests.custom_matchers as tcm
import tests.stub_net as stub_net


def create_sut(x=None, y=None, depth=None, xy_origin=None, depth_origin=None):
    stub_subsurface_point = stub_net.create_stub_net_subsurface_point(x, y, depth, xy_origin, depth_origin)

    sut = nsp.SubsurfacePoint(stub_subsurface_point)
    return sut


# Test ideas
class TestNativeSubsurfacePoint(unittest.TestCase):
    def test_canary(self):
        self.assertEqual(2 + 2, 4)

    def test_x(self):
        scalar_x = tcm.ScalarQuantity(-2725.83, units.Metric.LENGTH)
        sut = create_sut(x=scalar_x)

        expected_x = om.make_measurement(scalar_x.magnitude, scalar_x.unit)
        tcm.assert_that_scalar_quantities_close_to(sut.x, expected_x, 6e-2)

    def test_y(self):
        scalar_y = tcm.ScalarQuantity(1656448.10, units.Metric.LENGTH)
        sut = create_sut(y=scalar_y)

        expected_y = om.make_measurement(scalar_y.magnitude, scalar_y.unit)
        tcm.assert_that_scalar_quantities_close_to(sut.y, expected_y, 6e-2)

    def test_depth(self):
        scalar_depth = tcm.ScalarQuantity(8945.60, units.UsOilfield.LENGTH)
        sut = create_sut(depth=scalar_depth)

        expected_depth = om.make_measurement(scalar_depth.magnitude, scalar_depth.unit)
        tcm.assert_that_scalar_quantities_close_to(sut.depth, expected_depth, 6e-2)

    def test_xy_origin(self):
        expected_xy_origin = origins.WellReferenceFrameXy.PROJECT
        sut = create_sut(xy_origin=expected_xy_origin)

        # The expected Python Enum equals the .NET Enum because the expected value of the Python Enum **is**
        # the .NET Enum.
        assert_that(sut.xy_origin, equal_to(expected_xy_origin))

    def test_depth_origin(self):
        expected_depth_origin = origins.DepthDatum.GROUND_LEVEL
        sut = create_sut(depth_origin=expected_depth_origin)

        # The expected Python Enum equals the .NET Enum because the expected value of the Python Enum **is**
        # the .NET Enum.
        assert_that(sut.depth_origin, equal_to(expected_depth_origin))

    def test_as_length_unit(self):
        @toolz.curry
        def make_scalar_quantity(magnitude, unit):
            return tcm.ScalarQuantity(magnitude=magnitude, unit=unit)

        all_test_data = [((126834.6, 321614.0, 1836.6, 3136.3), units.Metric.LENGTH,
                          (416124, 1055164, 6025.56, 10289.7), units.UsOilfield.LENGTH),
                         ((444401, 9009999, 7799.91, 6722.57), units.UsOilfield.LENGTH,
                          (135453.42, 2746247.70, 2377.41, 2049.04), units.Metric.LENGTH)]
        for length_magnitudes, length_unit, as_length_magnitudes, as_length_unit in all_test_data:
            with self.subTest(length_magnitudes=length_magnitudes, length_unit=length_unit,
                              as_length_magnitudes=as_length_magnitudes,
                              as_length_unit=as_length_unit):
                from_lengths = list(toolz.map(toolz.flip(tcm.ScalarQuantity, length_unit), length_magnitudes))
                sut = create_sut(x=from_lengths[0], y=from_lengths[1], depth=from_lengths[2])
                actual_as_length_unit = sut.as_length_unit(as_length_unit)

                expected_lengths = list(toolz.map(toolz.flip(om.make_measurement, as_length_unit),
                                                  as_length_magnitudes))
                tcm.assert_that_scalar_quantities_close_to(actual_as_length_unit.x,
                                                           expected_lengths[0], 6e-2)
                tcm.assert_that_scalar_quantities_close_to(actual_as_length_unit.y,
                                                           expected_lengths[1], 6e-2)
                tcm.assert_that_scalar_quantities_close_to(actual_as_length_unit.depth,
                                                           expected_lengths[2], 6e-2)


if __name__ == '__main__':
    unittest.main()
