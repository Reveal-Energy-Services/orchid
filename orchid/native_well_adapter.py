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

# noinspection PyUnresolvedReferences
import orchid
import orchid.dot_net_dom_access as dna
import orchid.native_stage_adapter as nsa
import orchid.native_trajectory_adapter as nta

# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics import IWell


def replace_no_uwi_with_text(uwi):
    return uwi if uwi else 'No UWI'


class NativeWellAdapter(dna.DotNetAdapter):
    """Adapts a native IWell to python."""
    def __init__(self, net_well: IWell):
        """
        Constructs an instance adapting a .NET IWell.
        :param net_well: The .NET well to be adapted.
        """
        super().__init__(net_well)

    name = dna.dom_property('name', 'The name of the adapted .NET well.')
    display_name = dna.dom_property('display_name', 'The display name of the adapted .NET well.')
    stages = dna.transformed_dom_property_iterator('stages', 'An iterator over the NativeStageAdapters.',
                                                   nsa.NativeStageAdapter)
    trajectory = dna.transformed_dom_property('trajectory', 'The trajectory of the adapted .NET well.',
                                              nta.NativeTrajectoryAdapter)
    uwi = dna.transformed_dom_property('uwi', 'The UWI of the adapted .', replace_no_uwi_with_text)
