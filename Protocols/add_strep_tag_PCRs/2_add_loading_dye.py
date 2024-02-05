from opentrons import protocol_api
from math import ceil

#This metadata is not all required but it"s good to have
metadata = {
    "apiLevel": "2.13",
    "protocolName": "Add loading dye to PCR reactions",
    "description": """This protocol will remove 5 µl from a plate of PCR reactions and add it to a separate well.
                      We then add 2.22 µl of loading dye to the original reactions for running on a gel."""
}

#We need to define a run function which takes a protocol as argument
def run(protocol: protocol_api.ProtocolContext):

    #Load tips and labware
    p20_tips = protocol.load_labware("opentrons_96_tiprack_20ul", 1)
    reservoir = protocol.load_labware("usascientific_12_reservoir_22ml", 2)

    #Load pipettes and hardware modules
    p20 = protocol.load_instrument("p20_multi_gen2", "right", tip_racks=[p20_tips])
    temperature_module  = protocol.load_module("temperature module gen2", 3)

    #Load labware for temperature module
    pcr_plate = temperature_module.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt")

    #Define some constants and well name lists here for easy transfers later
    num_reactions = 48
    num_columns = ceil(num_reactions / 8)
    well_names = [f"A{x+1}" for x in range(num_columns)]
    new_well_names = [f"A{x+7}" for x in range(num_columns)]


    #Reserve PCR reactions
    p20.transfer(5, [pcr_plate[well] for well in well_names], [pcr_plate[well] for well in new_well_names], new_tip="always")

    #Add loading dye
    p20.transfer(2.22, reservoir["A1"], [pcr_plate[well] for well in well_names], new_tip="always")
