from opentrons import protocol_api
from math import ceil

#This metadata is not all required but it"s good to have
metadata = {
    "apiLevel": "2.13",
    "protocolName": "96-well Streptactin Magnetic Bead Purification",
    "description": """This protocol will perform batch purification of Strep-tagged proteins in a 96-well plate using magnetic Streptactin beads. It will equilibrate beads, add sample, then
                        perform washing and elution steps.""",
    "author": "Naail Kashif-Khan"
}

#We need to define a run function which takes a protocol as argument
def run(protocol: protocol_api.ProtocolContext):

    #Load tips and labware
    p300_tips = [protocol.load_labware("opentrons_96_tiprack_300ul", n) for n in [4, 5, 6, 7]]
    reservoir = protocol.load_labware("usascientific_12_reservoir_22ml", 2)
    target_plate = protocol.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt", 8)

    #Load pipettes and hardware modules
    p300 = protocol.load_instrument("p300_multi_gen2", "left", tip_racks=p300_tips)

    temperature_module  = protocol.load_module("temperature module gen2", 3)
    magnetic_module = protocol.load_module("magnetic module gen2", 1)

    #Load labware for magnetic and temperature modules
    beads_plate = magnetic_module.load_labware("abgene_96_wellplate_2200ul")
    lysate_plate = temperature_module.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt")   

    #Define some constants and well name lists here for easy transfers later
    num_reactions = 32
    num_columns = ceil(num_reactions / 8)
    well_names = [f"A{x+1}" for x in range(num_columns)]

    #Initialize temperature module
    temperature_module.set_temperature(celsius=4)

    #Equilibrate beads in Buffer W
    p300.flow_rate.dispense = 300 #Increase flow rate to fully resuspend beads
    p300.pick_up_tip()
    
    for _ in range(2):
        #Add buffer and resuspend beads
        magnetic_module.disengage()
        p300.transfer(300, reservoir["A1"], [beads_plate[well] for well in well_names], mix_after=(3, 200), new_tip="never")

        #Separate beads
        magnetic_module.engage(height=6.8)
        protocol.delay(minutes=3) #Allow time for magnetic beads to settle

        #Remove supernatant
        p300.flow_rate.aspirate = 15 #Decrease flow rate to avoid disturbing beads
        p300.transfer(300, [beads_plate[well].bottom(2.5) for well in well_names], reservoir["A12"], new_tip="never") #Aspirate from 2.5mm above the bottom of the well
        p300.flow_rate.aspirate = 94 #Reset flow rate to speed up protocol
    
    #Remove the final bit of liquid from the beads
    p300.flow_rate.aspirate = 15 #Decrease flow rate to avoid disturbing beads
    p300.transfer(50, [beads_plate[well].bottom(2.5) for well in well_names], reservoir["A12"], new_tip="never") #Aspirate from 2.5mm above the bottom of the well
    p300.flow_rate.aspirate = 94 #Reset flow rate to speed up protocol
    p300.flow_rate.dispense = 94 #Reset flow rate
    magnetic_module.disengage()

    #Load sample, dilute with Buffer W, and incubate
    p300.transfer(180, reservoir["A2"], [beads_plate[well] for well in well_names], new_tip="never")
    p300.drop_tip()
    p300.transfer(20, [lysate_plate[well] for well in well_names], [beads_plate[well] for well in well_names], new_tip="always")
    protocol.pause("Incubate beads at room temperature with 700 rpm shaking for 60 minutes")

    #Separate beads and remove supernatant
    magnetic_module.engage(height=6.8)
    protocol.delay(minutes=3) #Allow time for magnetic beads to settle

    p300.flow_rate.aspirate = 15 #Decrease flow rate to avoid disturbing beads
    p300.transfer(200, [beads_plate[well].bottom(2.5) for well in well_names], reservoir["A4"], new_tip="always") #Aspirate from 2.5mm above the bottom of the well
    p300.flow_rate.aspirate = 94 #Reset flow rate to speed up protocol

    #Wash beads in Buffer W
    p300.flow_rate.dispense = 300 #Increase flow rate to fully resuspend beads
    
    for _ in range(2):
        #Add buffer and resuspend beads
        magnetic_module.disengage()
        p300.transfer(100, reservoir["A2"], [beads_plate[well] for well in well_names], mix_after=(3, 200), new_tip="always")

        #Separate beads
        magnetic_module.engage(height=6.8)
        protocol.delay(minutes=3) #Allow time for magnetic beads to settle

        #Remove supernatant
        p300.flow_rate.aspirate = 15 #Decrease flow rate to avoid disturbing beads
        p300.transfer(100, [beads_plate[well].bottom(2.5) for well in well_names], reservoir["A5"], new_tip="always") #Aspirate from 2.5mm above the bottom of the well
        p300.flow_rate.aspirate = 94 #Reset flow rate to speed up protocol
    magnetic_module.disengage()

    #Elute protein
    p300.flow_rate.dispense = 300 #Increase flow rate to fully resuspend beads
    
    for _ in range(2):
        #Add buffer and resuspend beads
        magnetic_module.disengage()
        p300.transfer(100, reservoir["A3"], [beads_plate[well] for well in well_names], mix_after=(3, 200), new_tip="always")

        protocol.pause("Incubate beads at room temperature with 400 rpm shaking for 10 minutes")

        #Separate beads
        magnetic_module.engage(height=6.8)
        protocol.delay(minutes=3) #Allow time for magnetic beads to settle

        #Remove eluate
        p300.flow_rate.aspirate = 15 #Decrease flow rate to avoid disturbing beads
        p300.transfer(100, [beads_plate[well].bottom(2.5) for well in well_names], [target_plate[well] for well in well_names], new_tip="always") #Aspirate from 2.5mm above the bottom of the well
        p300.flow_rate.aspirate = 94 #Reset flow rate to speed up protocol

    magnetic_module.disengage()