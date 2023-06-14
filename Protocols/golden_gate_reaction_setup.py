from opentrons import protocol_api
from math import ceil

#This metadata is not all required but it"s good to have
metadata = {
    "apiLevel": "2.13",
    "protocolName": "Golden Gate Reaction Setup",
    "description": """This protocol sets up a 96-well plate of Golden Gate DNA assembly reactions, from a master mix, a 96-well plate of DNA fragments,
                      and a reagent reservoir filled with sillicone oil.
                      Setup: Empty 96-well PCR plate for the reactions
                             96-well PCR plate with golden gate master mix in Row 1 (17.9 ul per reaction) and gBlocks in Row 2 onwards (3.1 ul per reaction, minimum 10 ul)
                             12-well reservoir with sillicone oil in the first well""",
    "author": "Naail Kashif-Khan"
}

#We need to define a run function which takes a protocol as argument
def run(protocol: protocol_api.ProtocolContext):

    #Load tips and labware
    p20_tips = protocol.load_labware("opentrons_96_tiprack_20ul", 4)
    p300_tips = protocol.load_labware("opentrons_96_tiprack_300ul", 5)
    reservoir = protocol.load_labware("usascientific_12_reservoir_22ml", 6)

    target_golden_gate_reaction_plate = protocol.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt", 1)
    gblocks_master_mix_plate = protocol.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt", 2)

    #Load pipettes and hardware modules
    p20 = protocol.load_instrument("p20_multi_gen2", "right", tip_racks=[p20_tips])
    p300 = protocol.load_instrument("p300_multi_gen2", "left", tip_racks=[p300_tips])
    
    #Define some constants and well name lists here for easy transfers later
    num_reactions = 12
    num_columns = ceil(num_reactions / 8)
    gblock_well_names = [f"A{x+2}" for x in range(num_columns)]
    gg_well_names = [f"A{x+1}" for x in range(num_columns)]

    #Add master mix to reaction plate
    p20.distribute(16.9,
                 gblocks_master_mix_plate["A1"],
                 [target_golden_gate_reaction_plate[well] for well in gg_well_names])
    
    #Add gBlocks to each well
    p20.transfer(3.1,
                 [gblocks_master_mix_plate[well] for well in gblock_well_names],
                 [target_golden_gate_reaction_plate[well] for well in gg_well_names], mix_after=(4, 10), new_tip="always")

    #Now we can add sillicone oil to each reaction
    #Set flow rates of p300 pipette to recommended values for 90% glycerol
    #This has the same viscosity as sillicone oil so it should be a good guideline
    p300.flow_rate.aspirate = 64.75
    p300.flow_rate.dispense = 64.75
    p300.flow_rate.blow_out = 4

    p300.pick_up_tip()
    for well in gg_well_names:
        #Aspirate with lower flow rate, slower withdrawal speed, and a delay of 8 seconds
        p300.move_to(reservoir["A1"].top())
        protocol.max_speeds["z"] = 1
        p300.aspirate(135, reservoir["A1"])
        protocol.delay(seconds=8)
        p300.move_to(reservoir["A1"].top())
        del protocol.max_speeds["z"]

        #Dispense with lower flow rate, slower blowout rate, and delay of 8 seconds
        p300.dispense(150, target_golden_gate_reaction_plate[well].top())
        protocol.delay(8)

        #Blow out with lower flow rate
        p300.blow_out()
    
    p300.drop_tip()

    #Reset the flow rate and speed settings
    p300.flow_rate.aspirate = 94
    p300.flow_rate.dispense = 94
    p300.flow_rate.blow_out = 94