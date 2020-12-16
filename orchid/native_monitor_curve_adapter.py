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
import enum
from typing import Union

from orchid import (base_curve_adapter as bca,
                    dot_net_dom_access as dna,
                    physical_quantity as opq,
                    unit_system as units)

# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics import UnitSystem

AboutMonitorCurveType = namedtuple('AboutCurveType', ['curve_type', 'net_curve_type'])


class MonitorCurveTypes(enum.Enum):
    MONITOR_PRESSURE = AboutMonitorCurveType('Pressure', 'Pressure')
    MONITOR_TEMPERATURE = AboutMonitorCurveType('Temperature', 'Temperature')


class NativeMonitorCurveAdapter(bca.BaseCurveAdapter):
    sampled_quantity_type = dna.transformed_dom_property('sampled_quantity_type',
                                                         'The physical quantity of each sample.',
                                                         opq.to_physical_quantity)

    def sampled_quantity_unit(self) -> Union[units.UsOilfield, units.Metric]:
        """
        Return the measurement unit of the samples in this treatment curve.

        Returns:
            A `UnitSystem` member containing the unit for the sample in this treatment curve.
        """
        net_project_units = self._adaptee.Well.Project.ProjectUnits
        if net_project_units == UnitSystem.USOilfield():
            project_units = units.UsOilfield
        elif net_project_units == UnitSystem.Metric():
            project_units = units.Metric
        else:
            raise ValueError(f'Unrecognised unit system for {self._adaptee.Stage.Well.Project.Name}')

        sampled_quantity_name_unit_map = {
            MonitorCurveTypes.MONITOR_PRESSURE.value.net_curve_type: project_units.PRESSURE,
            MonitorCurveTypes.MONITOR_TEMPERATURE.value.net_curve_type: project_units.TEMPERATURE,
        }
        return sampled_quantity_name_unit_map[self.sampled_quantity_name]
