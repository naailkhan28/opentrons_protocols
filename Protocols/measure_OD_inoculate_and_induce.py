from opentrons import protocol_api
from math import ceil

#This metadata is not all required but it"s good to have
metadata = {
    "apiLevel": "2.13",
    "protocolName": "Inoculation and Induction of Protein Expression Cultures",
    "description": """This protocol will setup a 96-well plate to measure OD of overnight cultures in LB medium, and then inoculate expression cultures in TB medium.
                      After a pause of 3 hours, the protocol will add 10 mM IPTG (to a final concentration of 1 mM)""",
    "author": "Naail Kashif-Khan"
}

#We need to define a run function which takes a protocol as argument
def run(protocol: protocol_api.ProtocolContext):

    #Load tips and labware  
    culture_plate = protocol.load_labware("abgene_96_wellplate_2200ul", 1)
    od_plate = protocol.load_labware("sarstedt96wellfbottom_96_wellplate_360ul", 2)
    reservoir = protocol.load_labware("usascientific_12_reservoir_22ml", 3)
    p300_tips = protocol.load_labware("opentrons_96_tiprack_300ul", 4)
    p20_tips = protocol.load_labware("opentrons_96_tiprack_20ul", 5)

    #Load pipettes and hardware modules
    p20 = protocol.load_instrument("p20_multi_gen2", "right", tip_racks=[p20_tips])
    p300 = protocol.load_instrument("p300_multi_gen2", "left", tip_racks=[p300_tips])

    #Define some constants and well name lists here for easy transfers later
    num_cultures = 24
    num_columns = ceil(num_cultures / 8) 
    well_names = [f"A{x+1}" for x in range(num_columns)]


    #Add LB medium to OD plate
    p300.pick_up_tip()
    p300.transfer(190, reservoir["A1"], [od_plate[name] for name in well_names], new_tip="never")
    p300.transfer(200, reservoir["A1"], od_plate[f"A{len(well_names) + 1}"], new_tip="never")
    p300.drop_tip()

    #Add overnight cultures
    p20.flow_rate.dispense = 300 #Increase flow rate to fully mix

    p20.transfer(10, [culture_plate[well] for well in well_names],
                 [od_plate[well] for well in well_names], mix_after=(15, 20), new_tip="always")
    
    p20.flow_rate.dispense = 94 #Reset flow rate
    
    protocol.pause("Measure OD of 96-well plate now")

    #Add TB medium to culture plate
    p300.pick_up_tip()
    p300.transfer(225, reservoir["A2"], [culture_plate[f"A{i + num_columns + 1}"] for i in range(num_columns)],
                  new_tip="never")
    p300.drop_tip()
    
    #Inoculate wells with overnight culture
    p300.transfer(25, [culture_plate[well] for well in well_names],
                  [culture_plate[f"A{i + num_columns + 1}"] for i in range(num_columns)], new_tip="always", mix_after=(200, 3))
    
    protocol.pause("Grow cells at 37 degrees with 1800 rpm shaking for 3 hours now")

    #Induce with 1 mM IPTG
    p300.transfer(27.7, reservoir["A3"],
                  [culture_plate[f"A{i + num_columns + 1}"] for i in range(num_columns)], new_tip="always", mix_after=(200, 3))