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

import decimal
import datetime
import unittest
import unittest.mock

import deal
from hamcrest import assert_that, equal_to, contains_exactly, is_, empty, calling, raises
import toolz.curried as toolz

from orchid import (
    measurement as om,
    project as onp,
    project_loader as loader,
    unit_system as units)
from tests import (
    stub_net as tsn,
    custom_matchers as tcm,
)


@toolz.curry
def make_sample(start, value):
    return start, value


@toolz.curry
def make_samples(start, values):
    return toolz.map(make_sample(start), values)


@toolz.curry
def make_samples_for_starts(starts, values_for_starts):
    return toolz.pipe(zip(starts, values_for_starts),
                      toolz.map(lambda start_values_pair: make_samples(start_values_pair[0], start_values_pair[1])))


# Test ideas
class TestProject(unittest.TestCase):
    def test_canary(self):
        assert_that(2 + 2, equal_to(4))

    def test_ctor_no_loader_raises_exception(self):
        assert_that(calling(onp.Project).with_args(None), raises(deal.PreContractError))

    def test_azimuth_returns_azimuth_in_project_units(self):
        for actual_azimuth, project_units, expected_azimuth, tolerance in (
                (tsn.MeasurementDto(30.32, units.Common.ANGLE), units.UsOilfield,
                 30.32 * om.registry.deg, decimal.Decimal('0.01')),
                (tsn.MeasurementDto(60.35, units.Common.ANGLE), units.Metric,
                 60.35 * om.registry.deg, decimal.Decimal('0.01')),
        ):
            with self.subTest(f'Testing azimuth in same units {expected_azimuth}'):
                stub_native_project = tsn.create_stub_net_project(project_units=project_units,
                                                                  azimuth=actual_azimuth)
                sut = create_sut(stub_native_project)
                tcm.assert_that_measurements_close_to(sut.azimuth, expected_azimuth, tolerance)

    def test_default_well_colors_if_no_default_well_colors(self):
        stub_native_project = tsn.create_stub_net_project(name='exsistet')
        sut = create_sut(stub_native_project)
        assert_that(sut.default_well_colors(), equal_to([tuple([])]))

    def test_default_well_colors_if_one_default_well_color(self):
        stub_native_project = tsn.create_stub_net_project(name='exsistet', default_well_colors=[[0.142, 0.868, 0.220]])
        sut = create_sut(stub_native_project)
        # noinspection PyTypeChecker
        assert_that(sut.default_well_colors(), contains_exactly((0.142, 0.868, 0.220)))

    def test_default_well_colors_if_many_default_well_colors(self):
        expected_default_well_colors = [(0.610, 0.779, 0.675), (0.758, 0.982, 0.720), (0.297, 0.763, 0.388)]
        stub_native_project = tsn.create_stub_net_project(name='exsistet',
                                                          default_well_colors=[list(t) for t
                                                                               in expected_default_well_colors])
        sut = create_sut(stub_native_project)
        # noinspection PyTypeChecker
        assert_that(sut.default_well_colors(), contains_exactly(*expected_default_well_colors))

    def test_fluid_density_returns_fluid_density_in_project_units(self):
        for actual_density, project_units, expected_density, tolerance in (
                (tsn.MeasurementDto(47.02, units.UsOilfield.DENSITY), units.UsOilfield,
                 47.02 * om.registry.lb / om.registry.ft ** 3, decimal.Decimal('0.01')),
                # (tsn.MeasurementDto(1053, units.Metric.DENSITY), units.Metric,
                #  1053 * om.registry.kg / om.registry.m ** 3, decimal.Decimal('1')),
                # (tsn.MeasurementDto(47.02, units.UsOilfield.DENSITY), units.Metric,
                #  753.2 * om.registry.kg / om.registry.m ** 3, decimal.Decimal('0.2')),
                # (tsn.MeasurementDto(1053, units.Metric.DENSITY), units.UsOilfield,
                #  65.74 * om.registry.lb / om.registry.ft ** 3, decimal.Decimal('0.07')),
        ):
            with self.subTest(f'Testing fluid density in same units {expected_density}'):
                stub_native_project = tsn.create_stub_net_project(project_units=project_units,
                                                                  fluid_density=actual_density)
                sut = create_sut(stub_native_project)
                tcm.assert_that_measurements_close_to(sut.fluid_density, expected_density, tolerance)

    def test_name(self):
        stub_native_project = tsn.create_stub_net_project(name='commodorum')
        sut = create_sut(stub_native_project)
        assert_that(sut.name, equal_to('commodorum'))

    def test_project_center_relative_to_well_head_in_project_units(self):
        for orchid_actual, expected, project_units, tolerances in [
            (tsn.StubSurfaceLocation(tsn.MeasurementDto(-106505, units.UsOilfield.LENGTH),
                                     tsn.MeasurementDto(-1777697, units.UsOilfield.LENGTH)),
             tsn.StubSurfaceLocation(-106505 * om.registry.ft, -1777697 * om.registry.ft),
             units.UsOilfield, tsn.StubSurfaceLocation(decimal.Decimal('1'), decimal.Decimal('1'))),
            # (tsn.StubSurfaceLocation(tsn.MeasurementDto(-106.5e3, units.UsOilfield.LENGTH),
            #                          tsn.MeasurementDto(-1.778e6, units.UsOilfield.LENGTH)),
            #  tsn.StubSurfaceLocation(tsn.MeasurementDto(-32.46e3, units.Metric.LENGTH),
            #                          tsn.MeasurementDto(-541.9e3, units.Metric.LENGTH)),
            #  units.Metric, tsn.StubSurfaceLocation(decimal.Decimal('20'), decimal.Decimal('0.4e3'))),
            # (tsn.StubSurfaceLocation(tsn.MeasurementDto(106.7e3, units.Metric.LENGTH),
            #                          tsn.MeasurementDto(870.0e3, units.Metric.LENGTH)),
            #  tsn.StubSurfaceLocation(tsn.MeasurementDto(106.7e3, units.Metric.LENGTH),
            #                          tsn.MeasurementDto(870.0e3, units.Metric.LENGTH)),
            #  units.Metric, tsn.StubSurfaceLocation(decimal.Decimal('0.1e3'), decimal.Decimal('0.1e3'))),
            # (tsn.StubSurfaceLocation(tsn.MeasurementDto(106.7e3, units.Metric.LENGTH),
            #                          tsn.MeasurementDto(870.0e3, units.Metric.LENGTH)),
            #  tsn.StubSurfaceLocation(tsn.MeasurementDto(350.1e3, units.UsOilfield.LENGTH),
            #                          tsn.MeasurementDto(2.854e6, units.UsOilfield.LENGTH)),
            #  units.UsOilfield, tsn.StubSurfaceLocation(decimal.Decimal('0.4e3'), decimal.Decimal('0.4e3'))),
        ]:
            with self.subTest(f'Test project center {expected} in project units {project_units}'):
                stub_native_project = tsn.create_stub_net_project(project_units=project_units,
                                                                  project_center=orchid_actual)
                sut = create_sut(stub_native_project)
                tcm.assert_that_measurements_close_to(sut.project_center().x, expected.x, tolerances.x)
                tcm.assert_that_measurements_close_to(sut.project_center().y, expected.y, tolerances.y)

    def test_project_units_if_known(self):
        for expected_project_units in [units.Metric, units.UsOilfield]:
            with self.subTest(f'Testing if project has known units, "{expected_project_units}"'):
                stub_native_project = tsn.create_stub_net_project(project_units=expected_project_units)
                sut = create_sut(stub_native_project)

                assert_that(sut.project_units, equal_to(expected_project_units))

    def test_project_units_raises_type_error_if_unknown(self):
        stub_native_project = tsn.create_stub_net_project()
        sut = create_sut(stub_native_project)

        # I define this "phony" function because the expression returned by a property **is not** a
        # `callable`. By wrapping this expression in a function, I can than use `calling` and `raises`
        # to test for an expected exception.
        def phony_function():
            print(sut.project_units)

        # noinspection PyTypeChecker
        assert_that(calling(phony_function), raises(ValueError, pattern='^Unrecognized unit system'))

    def test_proppant_concentration_mass_unit(self):
        for expected_unit_system in [units.UsOilfield, units.Metric]:
            with self.subTest(f'Test proppant concentration mass unit: {expected_unit_system.MASS}'):
                stub_native_project = tsn.create_stub_net_project(project_units=expected_unit_system)
                sut = create_sut(stub_native_project)

                assert_that(sut.proppant_concentration_mass_unit(), equal_to(expected_unit_system.MASS))

    def test_proppant_concentration_mass_unit_raises_error_if_unit_system_unknown(self):
        stub_native_project = tsn.create_stub_net_project()
        sut = create_sut(stub_native_project)

        assert_that(calling(onp.Project.proppant_concentration_mass_unit).with_args(sut), raises(ValueError))

    def test_slurry_rate_volume_unit(self):
        for expected_unit_system in [units.UsOilfield, units.Metric]:
            with self.subTest(f'Test slurry rate volume unit: {expected_unit_system.VOLUME}'):
                stub_native_project = tsn.create_stub_net_project(project_units=expected_unit_system)
                sut = create_sut(stub_native_project)

                assert_that(sut.slurry_rate_volume_unit(), equal_to(expected_unit_system.VOLUME))

    def test_slurry_rate_volume_unit_raises_error_if_unit_system_unknown(self):
        stub_native_project = tsn.create_stub_net_project()
        sut = create_sut(stub_native_project)

        assert_that(calling(onp.Project.slurry_rate_volume_unit).with_args(sut), raises(ValueError))

    def test_wells_if_no_wells(self):
        stub_native_project = tsn.create_stub_net_project(name='exsistet')
        sut = create_sut(stub_native_project)
        assert_that(sut.wells, contains_exactly())

    def test_wells_if_one_well(self):
        expected_well_names = ['clunibus']
        stub_native_project = tsn.create_stub_net_project(name='exsistet', well_names=expected_well_names)
        sut = create_sut(stub_native_project)
        assert_that(map(lambda w: w.name, sut.wells), contains_exactly(*expected_well_names))

    def test_wells_if_many_wells(self):
        expected_well_names = ['cordam', 'turbibus', 'collaris']
        stub_native_project = tsn.create_stub_net_project(name='exsistet', well_names=expected_well_names)
        sut = create_sut(stub_native_project)
        assert_that(map(lambda w: w.name, sut.wells), contains_exactly(*expected_well_names))

    def test_wells_by_name_if_no_wells(self):
        stub_native_project = tsn.create_stub_net_project(name='exsistet')
        sut = create_sut(stub_native_project)
        assert_that(sut.wells_by_name('clunibus'), contains_exactly())

    def test_wells_by_name_if_no_well_with_name_found(self):
        expected_well_names = ['clunibus']
        stub_native_project = tsn.create_stub_net_project(name='exsistet', well_names=expected_well_names)
        sut = create_sut(stub_native_project)
        assert_that(map(lambda w: w.name, sut.wells_by_name('clunibus')), contains_exactly(*expected_well_names))

    def test_wells_by_name_if_one_well_with_name_found(self):
        expected_well_names = ['clunibus']
        stub_native_project = tsn.create_stub_net_project(name='exsistet', well_names=['clunibus'])
        sut = create_sut(stub_native_project)
        assert_that(map(lambda w: w.name, sut.wells_by_name('clunibus')), contains_exactly(*expected_well_names))

    def test_wells_by_name_if_many_wells_with_name_found(self):
        stub_native_project = tsn.create_stub_net_project(name='exsistet',
                                                          well_names=['cordam', 'turbibus',
                                                                      'cordam', 'collaris',
                                                                      'cordam'],
                                                          uwis=["93-167-64050-25-81", "54-107-49537-17-76",
                                                                "80-693-58647-57-44", "66-101-46368-44-99",
                                                                "06-390-40886-62-60"])
        sut = create_sut(stub_native_project)
        assert_that(map(lambda w: w.name, sut.wells_by_name('cordam')), contains_exactly(*(['cordam'] * 3)))

    def test_well_time_series_returns_empty_if_no_well_time_series(self):
        expected_well_time_series = []
        stub_native_project = tsn.create_stub_net_project(samples=expected_well_time_series)
        sut = create_sut(stub_native_project)

        # noinspection PyTypeChecker
        assert_that(sut.monitor_curves(), is_(empty()))

    def test_well_time_series_returns_one_if_one_well_time_series(self):
        curve_name = 'gestum'
        curve_quantity = 'pressure'
        sample_start = datetime.datetime(2018, 11, 14, 0, 58, 32, 136000)
        sample_values = [0.617, 0.408, 2.806]

        samples = make_samples(sample_start, sample_values)
        stub_native_project = tsn.create_stub_net_project(name='non curo', curve_names=[curve_name],
                                                          curves_physical_quantities=[curve_quantity],
                                                          samples=[samples])
        sut = create_sut(stub_native_project)

        # noinspection PyTypeChecker
        assert_that(len(list(sut.monitor_curves())), equal_to(1))

    def test_well_time_series_returns_many_if_many_well_time_series(self):
        curve_names = ['superseduisti', 'mulctaverim', 'veniae']
        curve_quantity_names = ['temperature', 'pressure', 'pressure']
        sample_starts = [datetime.datetime(2019, 3, 7, 10, 2, 13, 131000),
                         datetime.datetime(2019, 8, 1, 16, 50, 45, 500000),
                         datetime.datetime(2016, 3, 21, 20, 15, 19, 54000)]
        samples_values = [[152.4, 155.3, 142.0], [246.6, 219.4, 213.0], [219.9, 191.5, 187.6]]

        samples = list(make_samples_for_starts(sample_starts, samples_values))
        stub_native_project = tsn.create_stub_net_project(name='non curo', curve_names=curve_names,
                                                          curves_physical_quantities=curve_quantity_names,
                                                          samples=samples)
        sut = create_sut(stub_native_project)

        # noinspection PyTypeChecker
        assert_that(len(list(sut.monitor_curves())), equal_to(3))


def create_sut(stub_net_project):
    patched_loader = loader.ProjectLoader('dont_care')
    patched_loader.native_project = unittest.mock.MagicMock(name='stub_project', return_value=stub_net_project)

    sut = onp.Project(patched_loader)
    return sut


if __name__ == '__main__':
    unittest.main()
