from opentrons import protocol_api
from math import ceil

#This metadata is not all required but it"s good to have
metadata = {
    "apiLevel": "2.13",
    "protocolName": "Troubleshooting Transformations",
    "description": """This protocol will tranform pre-run Golden Gate reactions into E. coli DH5alpha. We will perform heat shock, add SOC medium, and then outgrowth
                        before plating 10 ul of the outgrowth mixture. We'll also plate 10 ul of a 2x dilution of this outgrowth mixture.
                        --------------------------TIP REQUIREMENTS--------------------------
                        12x 300 µl tips, 10x 20µl tips (both arranged in columns of two tips)""",
    "author": "Naail Kashif-Khan"
}

#We need to define a run function which takes a protocol as argument
def run(protocol: protocol_api.ProtocolContext):

    #Load tips and labware
    p20_tips = protocol.load_labware("opentrons_96_tiprack_20ul", 4)
    p300_tips = protocol.load_labware("opentrons_96_tiprack_300ul", 5)
    reservoir = protocol.load_labware("usascientific_12_reservoir_22ml", 1)
    agar_plate = protocol.load_labware("nunc_rectangular_agar_plate", 2)
    golden_gate_reaction_plate = protocol.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt", 6)

    #Load pipettes and hardware modules
    p20 = protocol.load_instrument("p20_multi_gen2", "right", tip_racks=[p20_tips])
    p300 = protocol.load_instrument("p300_multi_gen2", "left", tip_racks=[p300_tips])

    temperature_module  = protocol.load_module("temperature module gen2", 3)

    #Load labware for temperature and thermocycler modules
    competent_cell_plate = temperature_module.load_labware("opentrons_96_aluminumblock_generic_pcr_strip_200ul")

    #Define some constants and well name lists here for easy transfers later
    num_reactions = 16
    num_columns = ceil(num_reactions / 8)
    well_names = [f"A{x+1}" for x in range(num_columns)]

    #Transfer golden gate reaction mixture to competent cell plates
    temperature_module.set_temperature(celsius=4)
    protocol.pause("Add competent cells in PCR strips to temperature module now - don't forget to fill aluminium block with water!")

    p20.transfer(15, golden_gate_reaction_plate["A2"], competent_cell_plate["A2"], mix_after=(2, 10), new_tip="always")

    #Incubate on ice, heat shock, and recovery
    protocol.delay(minutes=30)
    temperature_module.set_temperature(celsius=42)
    protocol.delay(seconds=60)
    temperature_module.set_temperature(celsius=4)
    protocol.delay(minutes=5)

    #Add SOC medium and outgrowth
    p300.transfer(175, reservoir["A1"], [competent_cell_plate[well] for well in well_names], mix_after=(2, 100), new_tip="always")
    
    temperature_module.set_temperature(celsius=37)
    protocol.delay(minutes=60)

    #Plate undiluted outgrowth mixture
    p20.transfer(10,
                 [competent_cell_plate[well] for well in well_names],
                 [agar_plate[well].bottom(0) for well in well_names],
                 new_tip="always", blow_out=True, blowout_location="destination well")

    #Dilute outgrowth 2x and plate again
    p300.transfer(95, [competent_cell_plate[well] for well in well_names], reservoir["A12"], mix_before=(2, 100), new_tip="always")
    p300.transfer(95, reservoir["A1"], [competent_cell_plate[well] for well in well_names], mix_after=(2, 100), new_tip="always")

    new_well_names = [f"A{x + num_columns + 1}" for x in range(num_columns)]
    p20.transfer(10,
                 [competent_cell_plate[well] for well in well_names],
                 [agar_plate[well].bottom(0) for well in new_well_names],
                 new_tip="always", blow_out=True, blowout_location="destination well") 