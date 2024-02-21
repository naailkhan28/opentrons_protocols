from opentrons import protocol_api

#This metadata is not all required but it"s good to have
metadata = {
    "apiLevel": "2.13",
    "protocolName": "Set up expression plates",
    "description": """This protocol will add 225 µl of TB medium from a reservoir to each well of 2x 96-well deep well plates.
                      We'll then add 25 µl from each well of the two overnight plates to the expression plates""",
    "author": "Naail Kashif-Khan"
}

#We need to define a run function which takes a protocol as argument
def run(protocol: protocol_api.ProtocolContext):

    #Load tips and labware
    overnight_plates = [protocol.load_labware("abgene_96_wellplate_2200ul", n) for n in [1, 4]]
    expression_plates = [protocol.load_labware("abgene_96_wellplate_2200ul", n) for n in [2, 5]]
    p300_tips = [protocol.load_labware("opentrons_96_tiprack_300ul", n) for n in [3, 6]]
    reservoir = protocol.load_labware("usascientific_12_reservoir_22ml", 7)


    #Load pipettes and hardware modules
    p300 = protocol.load_instrument("p300_multi_gen2", "left", tip_racks=p300_tips)

    #Make a list of all wells we're using in this protocol
    overnight_wells = []
    expression_wells = []
    limits = [13, 10]

    for i, plate in enumerate(overnight_plates):
        overnight_wells.extend([plate[f"A{x}"] for x in range(1, limits[i])])

    for i, plate in enumerate(expression_plates):
        expression_wells.extend([plate[f"A{x}"] for x in range(1, limits[i])])

    #Distribute TB medium
    #Need to do this in three steps because one reservoir well only holds enough for 8 destination wells
    p300.pick_up_tip()
    p300.transfer(225, reservoir["A4"], expression_wells[:8], new_tip="never")
    p300.transfer(225, reservoir["A5"], expression_wells[8:16], new_tip="never")
    p300.transfer(225, reservoir["A6"], expression_wells[16:], new_tip="never")
    p300.drop_tip()

    #Inoculate expression wells with overnight cultures
    p300.transfer(25, overnight_wells, expression_wells, mix_after=(2, 125), new_tip="always")