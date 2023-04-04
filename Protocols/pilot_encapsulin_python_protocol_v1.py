from opentrons import protocol_api


#This metadata is not all required but it's good to have
metadata = {
    'apiLevel': '2.13',
    'protocolName': 'Serial Dilution Tutorial',
    'description': '''This protocol is the outcome of following the
                   Python Protocol API Tutorial located at
                   https://docs.opentrons.com/v2/tutorial.html. It takes a
                   solution and progressively dilutes it by transferring it
                   stepwise across a plate.''',
    'author': 'Naail Kashif-Khan'
}

#We need to define a run function which takes a protocol as argument
def run(protocol: protocol_api.ProtocolContext):
    #First, we load our tips and labware
    tips = protocol.load_labware("opentrons_96_tiprack_300ul", 1)
    reservoir = protocol.load_labware('nest_12_reservoir_15ml', 2)
    plate = protocol.load_labware('nest_96_wellplate_200ul_flat', 3)

    #Then, we load pipettes and any other modules
    p300 = protocol.load_instrument('p300_multi_gen2', 'left', tip_racks=[tips])

    #We can then transfer our stock solution to the destination plate
    p300.transfer(100, reservoir['A1'], plate.rows()[0])

    row = plate.rows()[0]
    #Transfer 100 ul sequentially from well i to well i+1 in each row
    #Note that we have a multichannel pipette so we only need to target row A
    #Since there are 8 pipette tips the other 7 rows will be pipetted as usual
    p300.transfer(100, reservoir['A2'], row[0], mix_after=(3, 50))
    p300.transfer(100, row[:11], row[1:], mix_after=(3, 50))