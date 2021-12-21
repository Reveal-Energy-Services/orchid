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

import deal

import numpy as np
import option
import toolz.curried as toolz

import orchid.base
from orchid import (
    dot_net_dom_access as dna,
    net_quantity as onq,
    reference_origins as origins,
    unit_system as units,
    validation,
)

# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics import IWellTrajectory

# noinspection PyUnresolvedReferences
import UnitsNet


def _trajectory_array_in_unit(tgt_unit, raw_array):
    result = toolz.pipe(raw_array,
                        toolz.map(option.maybe),
                        toolz.map(onq.as_measurement(tgt_unit)),
                        toolz.map(lambda m: m.magnitude),
                        lambda magnitudes: np.fromiter(magnitudes, dtype='float'))
    return result


class NativeTrajectoryAdapter(dna.DotNetAdapter):
    def __init__(self, net_trajectory: IWellTrajectory):
        """
        Construct an instance adapting a .NET `IWellTrajectory`.

        One need not construct an instance directly; instead, one constructs an instance by accessing the
        Orchid domain object model (DOM) of a project. For example,

        >>> project_path = orchid.training_data_path().joinpath('frankNstein_Bakken_UTM13_FEET.ifrac')
        >>> project = orchid.load_project(str(project_path))
        >>> well = list(project.wells().find_by_name('Demo_1H'))[0]
        >>> trajectory = well.trajectory

        Args:
            net_trajectory: The .NET trajectory to be adapted.
        """
        super().__init__(net_trajectory, orchid.base.constantly(net_trajectory.Well.Project))

    # TODO: Consider alternative interface, get_eastings()
    # See [pint Numpy support](https://pint.readthedocs.io/en/stable/numpy.html) or the
    # [pint pandas extension](https://github.com/hgrecco/pint-pandas)
    @deal.pre(validation.arg_not_none)
    def get_easting_array(self, reference_frame: origins.WellReferenceFrameXy) -> np.array:
        """
        Calculate the magnitudes of eastings of this trajectory relative to the specified `reference_frame`
        in project length units.

        Once one has a trajectory (from a well of a project), one can access the (Numpy) array of easting
        values. For example,

        >>> project_path = orchid.training_data_path().joinpath('frankNstein_Bakken_UTM13_FEET.ifrac')
        >>> project = orchid.load_project(str(project_path))
        >>> well = list(project.wells().find_by_name('Demo_3H'))[0]
        >>> trajectory = well.trajectory
        >>> eastings = trajectory.get_easting_array(origins.WellReferenceFrameXy.PROJECT)
        >>> f'{units.make_measurement(project.project_units.LENGTH, eastings[213]):.0f~P}'
        '-21008 ft'

        Argsk
            reference_frame: The reference frame for the easting coordinates.

        Returns:
            The array of eastings of this trajectory.
        """
        return self._trajectory_length_array(self.dom_object.GetEastingArray(reference_frame))

    # TODO: Consider alternative interface, get_northings()
    # See [pint Numpy support](https://pint.readthedocs.io/en/stable/numpy.html) or the
    # [pint pandas extension](https://github.com/hgrecco/pint-pandas)
    @deal.pre(validation.arg_not_none)
    def get_northing_array(self, reference_frame: origins.WellReferenceFrameXy) -> np.array:
        """
        Calculate the magnitudes of northings of this trajectory relative to the specified `reference_frame`
        in project length units.

        Args:
            reference_frame: The reference frame for the northing coordinates.

        Returns:
            The array of northings of this trajectory.

        """
        return self._trajectory_length_array(self.dom_object.GetNorthingArray(reference_frame))

    # TODO: Consider alternative interface, get_tvd_ss()
    # See [pint Numpy support](https://pint.readthedocs.io/en/stable/numpy.html) or the
    # [pint pandas extension](https://github.com/hgrecco/pint-pandas)
    def get_tvd_ss_array(self) -> np.array:
        """
        Calculate the array of total vertical depth values relative to `depth_datum` in project length units.

        Returns:
            The array of total vertical depths of this trajectory.
        """
        return self._get_tvd_array(origins.DepthDatum.SEA_LEVEL)

    # TODO: Consider alternative interface, get_northings()
    # See [pint Numpy support](https://pint.readthedocs.io/en/stable/numpy.html) or the
    # [pint pandas extension](https://github.com/hgrecco/pint-pandas)
    def get_inclination_array(self) -> np.array:
        """
        Calculate the array of inclination values.

        Returns:
            The array of inclinations of this trajectory.
        """
        return self._trajectory_angle_array(self.dom_object.GetInclinationArray())

    # TODO: Consider alternative interface, get_northings()
    # See [pint Numpy support](https://pint.readthedocs.io/en/stable/numpy.html) or the
    # [pint pandas extension](https://github.com/hgrecco/pint-pandas)
    def get_azimuth_east_of_north_array(self) -> np.array:
        """
        Calculate the array of azimuth values.

        Returns:
            The array of azimuths of this trajectory.
        """
        return self._trajectory_angle_array(self.dom_object.GetAzimuthEastOfNorthArray())

    # TODO: Consider alternative interface, get_md_kbs()
    # See [pint Numpy support](https://pint.readthedocs.io/en/stable/numpy.html) or the
    # [pint pandas extension](https://github.com/hgrecco/pint-pandas)
    def get_md_kb_array(self) -> np.array:
        """
        Calculate the array of MD KB values.

        Returns:
            The array of MD KB values of this trajectory.
        """
        return self._trajectory_length_array(self.dom_object.GetMdKbArray())

    @deal.pre(validation.arg_not_none)
    def _get_tvd_array(self, depth_datum: origins.DepthDatum) -> np.array:
        """
        Calculate the array of total vertical depth values relative to `depth_datum` in project length units.

        Args:
            depth_datum: The depth datum for the vertical depth values.

        Returns:
            The array of total vertical depths of this trajectory.
        """
        return self._trajectory_length_array(self.dom_object.GetTvdArray(depth_datum))

    @staticmethod
    def _trajectory_angle_array(raw_array):
        return _trajectory_array_in_unit(units.Common.ANGLE, raw_array)

    def _trajectory_length_array(self, raw_array):
        return _trajectory_array_in_unit(self.expect_project_units.LENGTH, raw_array)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
