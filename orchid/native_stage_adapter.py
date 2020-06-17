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

from orchid.measurement import Measurement
from orchid.net_quantity import as_datetime, as_measurement, convert_net_quantity_to_different_unit


class NativeStageAdapter:
    """Adapts a .NET IStage to be more Pythonic."""

    def __init__(self, adaptee):
        """
        Construct an instance adapting a .NET IStage.
        :param adaptee: The IStage instance to adapt.
        """
        self._adaptee = adaptee

    def display_stage_number(self):
        """
        Determine the stage number for display purposes.
        :return: The display stage number for the adapted .NET IStage.
        """
        return self._adaptee.DisplayStageNumber

    def md_top(self, length_unit_abbreviation: str) -> Measurement:
        """
        Return the measured depth of the top of this stage (closest to the well head / farthest from the toe)
        in the specified unit.
        :param length_unit_abbreviation: An abbreviation of the unit of length for the returned Measurement.
        :return: The measured depth of the stage top in the specified unit.
        """
        original = self._adaptee.MdTop
        md_top_quantity = convert_net_quantity_to_different_unit(original, length_unit_abbreviation)
        result = as_measurement(md_top_quantity)
        return result

    def md_bottom(self, length_unit_abbreviation):
        """
        Return the measured depth of the bottom of this stage (farthest from the well head / closest to the toe)
        in the specified unit.
        :param length_unit_abbreviation: An abbreviation of the unit of length for the returned Measurement.
        :return: The measured depth of the stage bottom in the specified unit.
        """
        original = self._adaptee.MdBottom
        md_top_quantity = convert_net_quantity_to_different_unit(original, length_unit_abbreviation)
        result = as_measurement(md_top_quantity)
        return result

    def start_time(self):
        """
        Calculate the start time of the treatment for this stage.
        :return: The start time of the stage treatment.
        """
        return as_datetime(self._adaptee.StartTime)

    def stop_time(self):
        """
        Calculate the stop time of the treatment for this stage.
        :return: The stop time of the stage treatment.
        """
        return as_datetime(self._adaptee.StopTime)
