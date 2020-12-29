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

"""This module contains functions for converting between instances of the (Python) `Measurement` class and
instances of .NET classes like `UnitsNet.Quantity` and `DateTime`."""

import datetime

import toolz.curried as toolz

from orchid import (physical_quantity as opq,
                    unit_system as units)

# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics.RatioTypes import (ProppantConcentration, SlurryRate)
# noinspection PyUnresolvedReferences
from System import DateTime, Decimal
# noinspection PyUnresolvedReferences
import UnitsNet


_UNIT_CREATE_NET_UNIT_MAP = {
    units.common[opq.ANGLE]: lambda q: UnitsNet.Angle.FromDegrees(q),
    units.common[opq.DURATION]: lambda q: UnitsNet.Duration.FromMinutes(q),
    units.us_oilfield[opq.DENSITY]: lambda q: UnitsNet.Density.FromPoundsPerCubicFoot(q),
    units.us_oilfield[opq.LENGTH]: lambda q: UnitsNet.Length.FromFeet(q),
    units.metric[opq.LENGTH]: lambda q: UnitsNet.Length.FromMeters(q),
    units.us_oilfield[opq.MASS]: lambda q: UnitsNet.Mass.FromPounds(q),
    units.metric[opq.MASS]: lambda q: UnitsNet.Mass.FromKilograms(q),
    units.us_oilfield[opq.PRESSURE]: lambda q: UnitsNet.Pressure.FromPoundsForcePerSquareInch(q),
    units.metric[opq.PRESSURE]: lambda q: UnitsNet.Pressure.FromKilopascals(q),
    units.us_oilfield[opq.VOLUME]: lambda q: UnitsNet.Volume.FromOilBarrels(q),
    units.metric[opq.VOLUME]: lambda q: UnitsNet.Volume.FromCubicMeters(q),
}

_UNIT_NET_UNIT_MAP = {
    units.common[opq.DURATION]: UnitsNet.Units.DurationUnit.Minute,
    units.us_oilfield[opq.LENGTH]: UnitsNet.Units.LengthUnit.Foot,
    units.metric[opq.LENGTH]: UnitsNet.Units.LengthUnit.Meter,
    units.us_oilfield[opq.MASS]: UnitsNet.Units.MassUnit.Pound,
    units.metric[opq.MASS]: UnitsNet.Units.MassUnit.Kilogram,
    units.us_oilfield[opq.PRESSURE]: UnitsNet.Units.PressureUnit.PoundForcePerSquareInch,
    units.metric[opq.PRESSURE]: UnitsNet.Units.PressureUnit.Kilopascal,
    units.us_oilfield[opq.VOLUME]: UnitsNet.Units.VolumeUnit.OilBarrel,
    units.metric[opq.VOLUME]: UnitsNet.Units.VolumeUnit.CubicMeter,
}


def as_datetime(net_time_point: DateTime) -> datetime.datetime:
    """
    Convert a .NET `DateTime` instance to a `datetime.datetime` instance.

    Args:
        net_time_point: A point in time of type .NET `DateTime`.

    Returns:
        The `datetime.datetime` equivalent to the `net_time_point`.
    """
    return datetime.datetime(net_time_point.Year, net_time_point.Month, net_time_point.Day,
                             net_time_point.Hour, net_time_point.Minute, net_time_point.Second,
                             net_time_point.Millisecond * 1000)


def as_measurement(net_quantity: UnitsNet.IQuantity,
                   physical_quantity: opq.PhysicalQuantity) -> units.Quantity:
    """
    Convert a .NET UnitsNet.IQuantity to a `Measurement` instance.

    Args:
        net_quantity: The .NET IQuantity instance to convert.
        physical_quantity: The optional `PhysicalQuantity`. Although we try to determine a unique mapping
        between units in the `unit_system` module and .NET `UnitsNet` units, we cannot perform a unique
        mapping for density and proppant concentration measured in the metric system (the units of these
        physical quantities are "kg/m**3"".

    Returns:
        The equivalent `Measurement` instance.
    """
    unit = _unit_from_net_quantity(net_quantity, physical_quantity)
    # UnitsNet, for an unknown reason, handles the `Value` property of `Power` **differently** from almost all
    # other units (`Information` and `BitRate` appear to be handled in the same way). Specifically, the
    # `Value` property **does not** return a value of type `double` but of type `Decimal`. Python.NET
    # expectedly converts the value returned by `Value` to a Python `decimal.Decimal`. Then, additionally,
    # Pint has a problem handling a unit whose value is `decimal.Decimal`. I do not quite understand this
    # problem, but I have seen other issues on GitHub that seem to indicate similar problems.
    result = (net_quantity.Value * unit if physical_quantity != opq.PhysicalQuantity.POWER
              else Decimal.ToDouble(net_quantity.Value) * unit)
    return result


def as_net_date_time(time_point: datetime.datetime) -> DateTime:
    """
    Convert a `datetime.datetime` instance to a .NET `DateTime` instance.

    Args:
        time_point: The `datetime.datetime` instance to covert.

    Returns:
        The equivalent .NET `DateTime` instance.
    """
    return DateTime(time_point.year, time_point.month, time_point.day, time_point.hour, time_point.minute,
                    time_point.second, round(time_point.microsecond / 1e3))


def as_net_quantity(measurement: units.Quantity) -> UnitsNet.IQuantity:
    """
    Convert a `Quantity` instance to a .NET `UnitsNet.IQuantity` instance.

    Args:
        measurement: The `Quantity` instance to convert.

    Returns:
        The equivalent `UnitsNet.IQuantity` instance.
    """
    quantity = UnitsNet.QuantityValue.op_Implicit(measurement.magnitude)
    try:
        return _UNIT_CREATE_NET_UNIT_MAP[measurement.units](quantity)
    except KeyError:
        if measurement.units == units.us_oilfield[opq.PROPPANT_CONCENTRATION]:
            return ProppantConcentration(measurement.magnitude,
                                         UnitsNet.Units.MassUnit.Pound,
                                         UnitsNet.Units.VolumeUnit.UsGallon)
        elif measurement.units == units.metric[opq.PROPPANT_CONCENTRATION]:
            return ProppantConcentration(measurement.magnitude,
                                         UnitsNet.Units.MassUnit.Kilogram,
                                         UnitsNet.Units.VolumeUnit.CubicMeter)
        elif measurement.units == units.us_oilfield[opq.SLURRY_RATE]:
            return SlurryRate(measurement.magnitude,
                              UnitsNet.Units.VolumeUnit.OilBarrel,
                              UnitsNet.Units.DurationUnit.Minute)
        elif measurement.units == units.metric[opq.SLURRY_RATE]:
            return SlurryRate(measurement.magnitude,
                              UnitsNet.Units.VolumeUnit.CubicMeter,
                              UnitsNet.Units.DurationUnit.Minute)
        else:
            raise ValueError(f'Unrecognized unit: "{measurement.unit}".')


def as_net_quantity_in_different_unit(measurement: units.Quantity, target_unit: units.Unit) -> UnitsNet.IQuantity:
    """
    Convert a `Quantity` into a .NET `UnitsNet.IQuantity` instance but in a different unit, `in_unit`.

    Args:
        measurement: The `Quantity` instance to convert.
        target_unit: The target unit of the converted `Quantity`.

    Returns:
        The  `NetUnits.IQuantity` instance equivalent to `measurement`.
    """
    net_to_convert = as_net_quantity(measurement)
    return net_to_convert.ToUnit(_UNIT_NET_UNIT_MAP[target_unit])


@toolz.curry
def convert_net_quantity_to_different_unit(net_quantity: UnitsNet.IQuantity,
                                           target_unit: units.Unit) -> UnitsNet.IQuantity:
    """
    Convert one .NET `UnitsNet.IQuantity` to another .NET `UnitsNet.IQuantity` in a different unit `target_unit`
    Args:
        net_quantity: The `UnitsNet.IQuantity` instance to convert.
        target_unit: The unit to which to convert `net_quantity`.

    Returns:
        The .NET `UnitsNet.IQuantity` converted to `target_unit`.
    """
    result = net_quantity.ToUnit(target_unit.value.net_unit)
    return result


_NET_UNIT_UNIT_MAP = {
    (UnitsNet.Units.AngleUnit.Degree, opq.PhysicalQuantity.ANGLE): units.common[opq.ANGLE],
    (UnitsNet.Units.DurationUnit.Minute, opq.PhysicalQuantity.DURATION): units.common[opq.DURATION],
    (UnitsNet.Units.DensityUnit.PoundPerCubicFoot, opq.PhysicalQuantity.DENSITY): units.us_oilfield[opq.DENSITY],
    (UnitsNet.Units.DensityUnit.KilogramPerCubicMeter, opq.PhysicalQuantity.DENSITY): units.metric[opq.DENSITY],
    (UnitsNet.Units.EnergyUnit.FootPound, opq.PhysicalQuantity.ENERGY): units.us_oilfield[opq.ENERGY],
    (UnitsNet.Units.EnergyUnit.Joule, opq.PhysicalQuantity.ENERGY): units.metric[opq.ENERGY],
    (UnitsNet.Units.ForceUnit.PoundForce, opq.PhysicalQuantity.FORCE): units.us_oilfield[opq.FORCE],
    (UnitsNet.Units.ForceUnit.Newton, opq.PhysicalQuantity.FORCE): units.metric[opq.FORCE],
    (UnitsNet.Units.LengthUnit.Foot, opq.PhysicalQuantity.LENGTH): units.us_oilfield[opq.LENGTH],
    (UnitsNet.Units.LengthUnit.Meter, opq.PhysicalQuantity.LENGTH): units.metric[opq.LENGTH],
    (UnitsNet.Units.MassUnit.Pound, opq.PhysicalQuantity.MASS): units.us_oilfield[opq.MASS],
    (UnitsNet.Units.MassUnit.Kilogram, opq.PhysicalQuantity.MASS): units.metric[opq.MASS],
    (UnitsNet.Units.PowerUnit.MechanicalHorsepower, opq.PhysicalQuantity.POWER): units.us_oilfield[opq.POWER],
    (UnitsNet.Units.PowerUnit.Watt, opq.PhysicalQuantity.POWER): units.metric[opq.POWER],
    (UnitsNet.Units.PressureUnit.PoundForcePerSquareInch, opq.PhysicalQuantity.PRESSURE):
        units.us_oilfield[opq.PRESSURE],
    (UnitsNet.Units.PressureUnit.Kilopascal, opq.PhysicalQuantity.PRESSURE): units.metric[opq.PRESSURE],
}


def _unit_from_net_quantity(net_quantity, physical_quantity):
    def is_proppant_concentration(quantity):
        return quantity == opq.PhysicalQuantity.PROPPANT_CONCENTRATION

    def is_slurry_rate(quantity):
        return quantity == opq.PhysicalQuantity.SLURRY_RATE

    def ratio_units(quantity):
        return quantity.NumeratorUnit, quantity.DenominatorUnit

    def is_us_oilfield_proppant_concentration(numerator, denominator):
        return numerator == UnitsNet.Units.MassUnit.Pound and denominator == UnitsNet.Units.VolumeUnit.UsGallon

    def is_metric_proppant_concentration(numerator, denominator):
        return numerator == UnitsNet.Units.MassUnit.Kilogram and denominator == UnitsNet.Units.VolumeUnit.CubicMeter

    def is_us_oilfield_slurry_rate(numerator, denominator):
        return numerator == UnitsNet.Units.VolumeUnit.OilBarrel and denominator == UnitsNet.Units.DurationUnit.Minute

    def is_metric_slurry_rate(numerator, denominator):
        return numerator == UnitsNet.Units.VolumeUnit.CubicMeter and denominator == UnitsNet.Units.DurationUnit.Minute

    if is_proppant_concentration(physical_quantity) or is_slurry_rate(physical_quantity):
        numerator_unit, denominator_unit = ratio_units(net_quantity)
        if is_us_oilfield_proppant_concentration(numerator_unit, denominator_unit):
            return units.us_oilfield[opq.PROPPANT_CONCENTRATION]
        elif is_metric_proppant_concentration(numerator_unit, denominator_unit):
            return units.metric[opq.PROPPANT_CONCENTRATION]
        elif is_us_oilfield_slurry_rate(numerator_unit, denominator_unit):
            return units.us_oilfield[opq.SLURRY_RATE]
        elif is_metric_slurry_rate(numerator_unit, denominator_unit):
            return units.metric[opq.SLURRY_RATE]

    return _NET_UNIT_UNIT_MAP[(net_quantity.Unit, physical_quantity)]
