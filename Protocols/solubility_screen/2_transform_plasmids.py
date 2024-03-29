from opentrons import protocol_api
from math import ceil

#This metadata is not all required but it"s good to have
metadata = {
    "apiLevel": "2.13",
    "protocolName": "Transformation of Purified Plasmid DNA",
    "description": """This protocol will tranform pure plasmid DNA into E. coli T7-Express (or BL21, or any protein expression strian you prefer). The protocol will mix plasmid with cells and pause to incubate at 4 degrees, wait for you to heat shock
                      the cells in a water bath, add SOC medium, then pause for you to carry out the out growth in a thermomixer/shaker, then resume again to plate cells onto an agar plate
                      NOTE: Because we've run out of slots on the OT-2 deck, this protocol will only plate the undiluted outgrowth mixtures.
                      Use the next protocol in the series to dilute and plate the cultures again after.""",
    "author": "Naail Kashif-Khan"
}

#We need to define a run function which takes a protocol as argument
def run(protocol: protocol_api.ProtocolContext):

    #Load tips and labware
    p20_tips = [protocol.load_labware("opentrons_96_tiprack_20ul", n) for n in [5, 8]]
    p300_tips = [protocol.load_labware("opentrons_96_tiprack_300ul", n) for n in [4, 7]]
    reservoir = protocol.load_labware("usascientific_12_reservoir_22ml", 6)

    agar_plate = protocol.load_labware("nunc_rectangular_agar_plate", 1)
    plasmid_plate = protocol.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt", 2)

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

    #Transfer golden gate reaction mixture to competent cell plates
    temperature_module.set_temperature(celsius=4)
    protocol.pause("Add competent cells in PCR strips to temperature module now - don't forget to fill aluminium block with water!")

    p20.transfer(10, [plasmid_plate[well] for well in well_names],
                     [competent_cell_plate[well] for well in well_names], mix_after=(1, 10), new_tip="always")

    #Incubate on ice and then wait for heat shock
    protocol.delay(minutes=30)
    protocol.pause("Heat shock cells and then return to temperature module now")

    #Add SOC medium and then wait for outgrowth
    p300.transfer(125, reservoir["A1"], [competent_cell_plate[well] for well in well_names], mix_after=(2, 100), new_tip="always")
    protocol.pause("Remove cells and incubate in thermomixer for outgrowth now")

    #Plate undiluted outgrowth mixture
    p20.transfer(10,
                 [competent_cell_plate[well] for well in well_names],
                 [agar_plate[well].bottom(0) for well in well_names],
                 new_tip="always", blow_out=True, blowout_location="destination well")
