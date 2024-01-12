from opentrons import protocol_api

#This metadata is not all required but it"s good to have
metadata = {
    "apiLevel": "2.13",
    "protocolName": "Set up overnight plates",
    "description": """This protocol will add 250 µl of LB medium from a reservoir to each well of 2x 96-well deep well plates""",
    "author": "Naail Kashif-Khan"
}

#We need to define a run function which takes a protocol as argument
def run(protocol: protocol_api.ProtocolContext):

    #Load tips and labware
    p300_tips = protocol.load_labware("opentrons_96_tiprack_300ul", 4)
    reservoir = protocol.load_labware("usascientific_12_reservoir_22ml", 3)

    culture_plates = [protocol.load_labware("abgene_96_wellplate_2200ul", n) for n in [1, 2]]

    #Load pipettes and hardware modules
    p300 = protocol.load_instrument("p300_multi_gen2", "left", tip_racks=p300_tips)

    #Make a list of all wells we're using in this protocol
    locations = []
    limits = [13, 10]
    for i, plate in enumerate(culture_plates):
        locations.extend([plate[f"A{x}"] for x in range(1, limits[i])])

    #Distribute LB medium
    #Need to do this in three steps because one reservoir well only holds enough for 8 destination wells
    p300.pick_up_tip()
    p300.transfer(250, reservoir["A1"], locations[:8], new_tip="never")
    p300.transfer(250, reservoir["A2"], locations[8:16], new_tip="never")
    p300.transfer(250, reservoir["A3"], locations[16:], new_tip="never")
    p300.drop_tip()