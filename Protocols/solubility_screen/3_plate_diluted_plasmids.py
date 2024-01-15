from opentrons import protocol_api
from math import ceil

#This metadata is not all required but it"s good to have
metadata = {
    "apiLevel": "2.13",
    "protocolName": "Dilute and plate outgrowth cultures",
    "description": """Following transformation and plating of undiluted outgrowth cultures, this protocol will dilute the cultures by half and then plate on a fresh agar plate.""",
    "author": "Naail Kashif-Khan"
}

#We need to define a run function which takes a protocol as argument
def run(protocol: protocol_api.ProtocolContext):

    #Load tips and labware
    p20_tips = protocol.load_labware("opentrons_96_tiprack_20ul", 5)
    p300_tips = [protocol.load_labware("opentrons_96_tiprack_300ul", n) for n in [4, 7]]
    reservoir = protocol.load_labware("usascientific_12_reservoir_22ml", 6)

    agar_plate = protocol.load_labware("nunc_rectangular_agar_plate", 1)

    #Load pipettes and hardware modules
    p20 = protocol.load_instrument("p20_multi_gen2", "right", tip_racks=p20_tips)
    p300 = protocol.load_instrument("p300_multi_gen2", "left", tip_racks=p300_tips)

    temperature_module  = protocol.load_module("temperature module gen2", 3)

    #Load labware for temperature and thermocycler modules
    competent_cell_plate = temperature_module.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt") 

    #Define some constants and well name lists here for easy transfers later
    num_reactions = 51
    num_columns = ceil(num_reactions / 8)
    well_names = [f"A{x+1}" for x in range(num_columns)]

    #Dilute outgrowth 2x and plate again
    p300.transfer(70, [competent_cell_plate[well] for well in well_names], reservoir["A12"], mix_before=(2, 100), new_tip="always")
    p300.transfer(70, reservoir["A1"], [competent_cell_plate[well] for well in well_names], mix_after=(2, 100), new_tip="always")

    p20.transfer(10,
                 [competent_cell_plate[well] for well in well_names],
                 [agar_plate[well].bottom(0) for well in well_names],
                 new_tip="always", blow_out=True, blowout_location="destination well") 
