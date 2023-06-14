from opentrons import protocol_api

#This metadata is not all required but it"s good to have
metadata = {
    "apiLevel": "2.13",
    "protocolName": "Sillicone Oil Pipetting Test",
    "description": """This protocol experiments with pipetting of sillicone oil, a very viscous fluid that requires optimal pipetting settings.""",
    "author": "Naail Kashif-Khan"
}

#We need to define a run function which takes a protocol as argument
def run(protocol: protocol_api.ProtocolContext):

    #Load tips and labware
    p300_tips = protocol.load_labware("opentrons_96_tiprack_300ul", 1)
    reservoir = protocol.load_labware("usascientific_12_reservoir_22ml", 2)
    golden_gate_reaction_plate = protocol.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt", 3)

    #Load pipette
    p300 = protocol.load_instrument("p300_multi_gen2", "left", tip_racks=[p300_tips])

    #Transfer loading dye to 96-well plate
    #Will dispense 20 ul to columns A6, A7, and A8 from well A2 of the 12-well reservoir
    p300.distribute(20, reservoir["A2"], [golden_gate_reaction_plate[f"A{i}"] for i in range(6, 9)], new_tip="once")

    #Set flow rates of p300 pipette to recommended values for 90% glycerol
    #This has the same viscosity as sillicone oil so it should be a good guideline
    p300.flow_rate.aspirate = 64.75
    p300.flow_rate.dispense = 64.75
    p300.flow_rate.blow_out = 4

    p300.pick_up_tip()
    for i in range(6, 9):
        #Aspirate with lower flow rate, slower withdrawal speed, and a delay of 8 seconds
        p300.move_to(reservoir["A3"].top())
        protocol.max_speeds["z"] = 1
        p300.aspirate(135, reservoir["A3"])
        protocol.delay(seconds=8)
        p300.move_to(reservoir["A3"].top())
        del protocol.max_speeds["z"]

        #Dispense with lower flow rate, slower blowout rate, and delay of 8 seconds
        p300.dispense(150, golden_gate_reaction_plate[f"A{i}"].top())
        protocol.delay(8)

        #Blow out with lower flow rate
        p300.blow_out()
    
    p300.drop_tip()

    #Reset the flow rate and speed settings
    p300.flow_rate.aspirate = 94
    p300.flow_rate.dispense = 94
    p300.flow_rate.blow_out = 94

    #Transfer loading dye from under sillicone oil to a fresh well
    p300.pick_up_tip()
    p300.aspirate(15, golden_gate_reaction_plate[f"A6"].bottom())
    p300.touch_tip()
    protocol.delay(seconds=1)
    p300.dispense(15, golden_gate_reaction_plate[f"A10"])