from opentrons import protocol_api

#This metadata is not all required but it"s good to have
metadata = {
    "apiLevel": "2.13",
    "protocolName": "Set up plates for OD measurement",
    "description": """This protocol will add 20 µl of cell culture from 2x 96-well deep well plates, to standard 96-well plates for plate reader measurement.
                      We'll also add 180 µl of medium to each well, and the final column of each destination plate will contain 200 µl of blank medium""",
    "author": "Naail Kashif-Khan"
}

#We need to define a run function which takes a protocol as argument
def run(protocol: protocol_api.ProtocolContext):

    #Load tips and labware
    culture_plates = [protocol.load_labware("abgene_96_wellplate_2200ul", n) for n in [1, 4]]
    od_plates = [protocol.load_labware("sarstedt96wellfbottom_96_wellplate_360ul", n) for n in [2, 5]]
    p300_tips = [protocol.load_labware("opentrons_96_tiprack_300ul", n) for n in [3, 6]]
    reservoir = protocol.load_labware("usascientific_12_reservoir_22ml", 7)


    #Load pipettes and hardware modules
    p300 = protocol.load_instrument("p300_multi_gen2", "left", tip_racks=p300_tips)

    #Make a list of all wells we're using in this protocol
    culture_plate_wells = []
    od_plate_wells = []
    limits = [13, 10]

    for i, plate in enumerate(culture_plates):
        culture_plate_wells.extend([plate[f"A{x}"] for x in range(1, limits[i])])

    limits = [12, 11]
    for i, plate in enumerate(od_plates):
        od_plate_wells.extend([plate[f"A{x}"] for x in range(1, limits[i])])

    #Distribute medium
    #Need to do this in three steps because one reservoir well only holds enough for 8 destination columns
    p300.pick_up_tip()
    p300.transfer(180, reservoir["A1"], od_plate_wells[:8], new_tip="never")
    p300.transfer(180, reservoir["A2"], od_plate_wells[8:16], new_tip="never")
    p300.transfer(180, reservoir["A3"], od_plate_wells[16:], new_tip="never")
    p300.transfer(200, reservoir["A3"], [plate["A12"] for plate in od_plates], new_tip="never")
    p300.drop_tip()

    #Inoculate expression wells with overnight cultures
    p300.transfer(20, culture_plate_wells, od_plate_wells, mix_after=(2, 80), new_tip="always")