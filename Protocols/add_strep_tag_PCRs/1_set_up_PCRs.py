from opentrons import protocol_api
from math import ceil

#This metadata is not all required but it"s good to have
metadata = {
    "apiLevel": "2.13",
    "protocolName": "Set up PCR reactions for adding Strep-Tag II",
    "description": """This protocol will dilute 48 200 µM primers by a factor of 40x to a final concentration of 2.5 µM.
                      We then add 5µl of pre-diluted, purified plasmid and 5 µl of the diluted 2.5 µM reverse primer to a plate 
                      containing 15 µl of PCR master mix (including Fw primer)"""
}

#We need to define a run function which takes a protocol as argument
def run(protocol: protocol_api.ProtocolContext):

    #Load tips and labware
    p20_tips = [protocol.load_labware("opentrons_96_tiprack_20ul", n) for n in [4, 7]]
    p300_tips = protocol.load_labware("opentrons_96_tiprack_300ul", 5)
    
    primer_plate = protocol.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt", 1)
    diluted_primer_plate = protocol.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt", 2)
    plasmid_plate = protocol.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt", 6)
    reservoir = protocol.load_labware("usascientific_12_reservoir_22ml", 8)

    #Load pipettes and hardware modules
    p20 = protocol.load_instrument("p20_multi_gen2", "right", tip_racks=p20_tips)
    p300 = protocol.load_instrument("p300_multi_gen2", "left", tip_racks=[p300_tips])
    temperature_module  = protocol.load_module("temperature module gen2", 3)

    #Load labware for temperature module
    pcr_plate = temperature_module.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt")

    #Define some constants and well name lists here for easy transfers later
    num_reactions = 48
    num_columns = ceil(num_reactions / 8)
    well_names = [f"A{x+1}" for x in range(num_columns)]


    #Dilute primers
    p20.transfer(4, [primer_plate[well] for well in well_names], [diluted_primer_plate[well] for well in well_names])
    p300.transfer(156, reservoir["A1"], [diluted_primer_plate[well] for well in well_names])

    #Add template
    p20.transfer(5, [plasmid_plate[well] for well in well_names], [pcr_plate[well] for well in well_names])

    #Add Rv Primer
    p20.transfer(5, [diluted_primer_plate[well] for well in well_names], [pcr_plate[well] for well in well_names], mix_after=(2, 10))