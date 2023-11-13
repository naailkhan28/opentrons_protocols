from opentrons import protocol_api
from math import ceil

#This metadata is not all required but it"s good to have
metadata = {
    "apiLevel": "2.13",
    "protocolName": "Golden Gate Reaction Setup",
    "description": """This protocol sets up a 96-well plate of Golden Gate DNA assembly reactions, from a master mix and a 96-well plate of DNA fragments
                      Setup: Empty 96-well PCR plate for the reactions
                             96-well PCR plate with gBlocks (4 ul per reaction, minimum 10 ul)
                             12-well reservoir with golden gate master mix in the first well (16 ul per reaction)""",
    "author": "Naail Kashif-Khan"
}

#We need to define a run function which takes a protocol as argument
def run(protocol: protocol_api.ProtocolContext):

    #Load tips and labware
    p20_tips = protocol.load_labware("opentrons_96_tiprack_20ul", 4)
    p300_tips = protocol.load_labware("opentrons_96_tiprack_300ul", 5)

    target_golden_gate_reaction_plate = protocol.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt", 1)
    gblock_plate = protocol.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt", 2)
    reservoir = protocol.load_labware("usascientific_12_reservoir_22ml", 3)

    #Load pipettes and hardware modules
    p20 = protocol.load_instrument("p20_multi_gen2", "right", tip_racks=[p20_tips])
    p300 = protocol.load_instrument("p300_multi_gen2", "left", tip_racks=[p300_tips])
    
    #Define some constants and well name lists here for easy transfers later
    num_reactions = 48
    num_columns = ceil(num_reactions / 8)
    well_names = [f"A{x+1}" for x in range(num_columns)]

    #Add master mix to reaction plate
    p20.distribute(16,
                 reservoir["A1"],
                 [target_golden_gate_reaction_plate[well] for well in well_names])
    
    #Add gBlocks to each well
    p20.transfer(4,
                 [gblock_plate[well] for well in well_names],
                 [target_golden_gate_reaction_plate[well] for well in well_names], mix_after=(4, 10), new_tip="always")