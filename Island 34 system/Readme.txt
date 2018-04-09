Raw files:
testRAW04052018.raw: Raw file generated from FinalRAW03312018MM2.raw by following the changes made in change_map.txt
testRAW04052018_fixedload.raw: Changed mappings of all LV loads (< 30 kV) so that they are now directly connected to transformers
tmp.raw: generated from disconnectLV.py after disconnecting all unimportant LV buses
tmp_islanded.raw: Generated from tmp.raw after islanding with the help of PSS/E
tmp_island_branch_fixed.raw: Generated from tmp_island.raw after disconnecting all the branches and transformers connected to bus type 4 (done with the help of disconnectBranchesForType4.py)
RAW0406018.raw: Raw file which is automatically generated using the main script (3 winders are not converted to 2 winders and none of the scripts in 'Raw with only 2 winders' folders are applied)

Scripts:
