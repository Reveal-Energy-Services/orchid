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

import functools
import logging
import pathlib

import clr
import orchid

# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics import (MonitorExtensions, Leakoff, Observation)
# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics.Factories import FractureDiagnosticsFactory
# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics.Factories.Implementations import LeakoffCurves
# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics.SDKFacade import (
    ScriptAdapter,
)
# noinspection PyUnresolvedReferences
from System import (DateTime, String)
# noinspection PyUnresolvedReferences
from System.IO import (FileStream, FileMode, FileAccess, FileShare)
# noinspection PyUnresolvedReferences
import UnitsNet

clr.AddReference('Orchid.Math')
clr.AddReference('System.Collections')
# noinspection PyUnresolvedReferences
from Orchid.Math import Interpolation
# noinspection PyUnresolvedReferences
from System.Collections.Generic import List


object_factory = FractureDiagnosticsFactory.Create()


def calculate_leak_off_pressure(leak_off_curve, maximum_pressure_sample):
    query_times = List[DateTime]()
    query_times.Add(maximum_pressure_sample.Timestamp)
    leak_off_pressure = leak_off_curve.GetPressureValues(query_times)[0]
    return leak_off_pressure


def calculate_maximum_pressure_sample(stage_part, ticks):
    def maximum_pressure_reducer(so_far, candidate):
        if stage_part.StartTime <= candidate.Timestamp <= stage_part.StopTime and candidate.Value > so_far.Value:
            return candidate
        else:
            return so_far

    sentinel_maximum = object_factory.CreateTick[float](DateTime.MinValue, -1000)
    maximum_pressure_sample = functools.reduce(maximum_pressure_reducer, ticks, sentinel_maximum)
    return maximum_pressure_sample


def auto_pick_observation_details(unpicked_observation, native_monitor, stage_part):

    # Auto pick observation details
    # - Leak off curve type
    # - Control point times
    # - Visible range x-min time
    # - Visible range x-max time
    # - Position
    # - Delta pressure
    # - Notes
    # - Signal quality

    time_range = object_factory.CreateDateTimeOffsetRange(stage_part.StartTime.AddDays(-1),
                                                          stage_part.StopTime.AddDays(1))
    ticks = native_monitor.TimeSeries.GetOrderedTimeSeriesHistory(time_range)

    time_stamp_ticks = List[float]()
    magnitudes = List[float]()

    tick_count = ticks.Length
    for i in range(0, tick_count):
        tick = ticks[i]
        time_stamp_ticks.Add(tick.Timestamp.Ticks)
        magnitudes.Add(tick.Value)

    time_series_interpolant = Interpolation.Interpolant1DFactory.CreatePchipInterpolant(time_stamp_ticks.ToArray(),
                                                                                        magnitudes.ToArray())
    L1 = LeakoffCurves.LeakoffCurveControlPointTime()
    L1.Active = 1
    L1.Time = stage_part.StartTime.AddMinutes(-20)

    L2 = LeakoffCurves.LeakoffCurveControlPointTime()
    L2.Active = 1
    L2.Time = stage_part.StartTime

    L3 = LeakoffCurves.LeakoffCurveControlPointTime()
    L3.Active = 0
    L3.Time = stage_part.StartTime.AddMinutes(10)

    time_series_interpolation_points = List[float]()
    time_series_interpolation_points.Add(L1.Time.Ticks)
    time_series_interpolation_points.Add(L2.Time.Ticks)

    pressure_values = time_series_interpolant.Interpolate(time_series_interpolation_points.ToArray(), 0)

    control_point_times = List[Leakoff.ControlPoint]()
    control_point_times.Add(Leakoff.ControlPoint(
        DateTime=L1.Time, Pressure=UnitsNet.Pressure(pressure_values[0],
                                                     UnitsNet.Units.PressureUnit.PoundForcePerSquareInch)))
    control_point_times.Add(Leakoff.ControlPoint(
        DateTime=L2.Time,
        Pressure=UnitsNet.Pressure(pressure_values[1],
                                   UnitsNet.Units.PressureUnit.PoundForcePerSquareInch)))

    # Create leak off curve
    leak_off_curve = object_factory.CreateLeakoffCurve(Leakoff.LeakoffCurveType.Linear,
                                                       control_point_times)

    maximum_pressure_sample = calculate_maximum_pressure_sample(stage_part, ticks)
    leak_off_pressure = calculate_leak_off_pressure(leak_off_curve, maximum_pressure_sample)

    observation_control_points = List[DateTime]()
    observation_control_points.Add(L1.Time)
    observation_control_points.Add(L2.Time)

    picked_observation = unpicked_observation  # An alias to better communicate intent
    mutable_observation = picked_observation.ToMutable()
    # - Leak off curve type
    mutable_observation.LeakoffCurveType = Leakoff.LeakoffCurveType.Linear
    # - Control point times
    mutable_observation.ControlPointTimes = observation_control_points
    # - Visible range x-min time
    mutable_observation.VisibleRangeXminTime = stage_part.StartTime.AddHours(-1)
    # - Visible range x-max time
    mutable_observation.VisibleRangeXmaxTime = stage_part.StopTime.AddHours(1)
    mutable_observation.Position = maximum_pressure_sample.Timestamp
    # - Delta pressure
    mutable_observation.DeltaPressure = UnitsNet.Pressure.op_Subtraction(
        UnitsNet.Pressure(maximum_pressure_sample.Value, UnitsNet.Units.PressureUnit.PoundForcePerSquareInch),
        leak_off_pressure)
    # - Notes
    mutable_observation.Notes = "Auto-picked"
    # - Signal quality
    mutable_observation.SignalQuality = Observation.SignalQualityValue.UndrainedCompressive
    mutable_observation.Dispose()

    return picked_observation


def auto_pick_observations(native_project, native_monitor):
    stage_parts = MonitorExtensions.FindPossiblyVisibleStageParts(native_monitor, native_project.Wells.Items)

    object_factory = FractureDiagnosticsFactory.Create()

    observation_set = object_factory.CreateObservationSet(native_project, 'Auto-picked Observation Set3')
    for part in stage_parts:
        # Create unpicked observation
        unpicked_observation = object_factory.CreateObservation(native_monitor, part)

        # Auto-pick observation details
        picked_observation = auto_pick_observation_details(unpicked_observation, native_monitor, part)

        # Add picked observation to observation set
        mutable_observation_set = observation_set.ToMutable()
        mutable_observation_set.AddEvent(picked_observation)
        mutable_observation_set.Dispose()

    # Add observation set to project
    project_with_observation_set = native_project  # An alias to better communicate intent
    mutable_project = native_project.ToMutable()
    mutable_project.AddObservationSet(observation_set)
    mutable_project.Dispose()

    return project_with_observation_set


def main():
    logging.basicConfig(level=logging.INFO)

    orchid_training_data_path = orchid.training_data_path()
    source_project_file_name = 'frankNstein_Bakken_UTM13_FEET.ifrac'

    # Read Orchid project
    project = orchid.load_project(str(orchid_training_data_path.joinpath(source_project_file_name)))
    native_project = project.dom_object
    monitor_name = 'Demo_3H - MonitorWell'
    candidate_monitors = list(project.monitors().find_by_display_name(monitor_name))
    # I actually expect one or more monitors, but I only need one (arbitrarily the first one)
    assert len(candidate_monitors) > 0, f'One or monitors with display name, "{monitor_name}", expected.' \
                                        f' Found {len(candidate_monitors)}.'
    native_monitor = candidate_monitors[0].dom_object
    auto_pick_observations(native_project, native_monitor)

    # Log changed project data
    logging.info(f'{native_project.Name=}')
    logging.info(f'{len(native_project.ObservationSets.Items)=}')
    for observation_set in native_project.ObservationSets.Items:
        logging.info(f'{observation_set.Name=}')
        logging.info(f'{len(observation_set.LeakOffObservations.Items)=}')
    logging.info(f'{len(observation_set.GetObservations())=}')

    # Write Orchid project
    source_file_name = pathlib.Path(source_project_file_name)
    target_file_name = ''.join([source_file_name.stem, '.999', source_file_name.suffix])
    target_path_name = str(orchid_training_data_path.joinpath(target_file_name))
    with orchid.script_adapter_context.ScriptAdapterContext():
        writer = ScriptAdapter.CreateProjectFileWriter()
        use_binary_format = False
        writer.Write(native_project, target_path_name, use_binary_format)

    return


if __name__ == '__main__':
    main()
