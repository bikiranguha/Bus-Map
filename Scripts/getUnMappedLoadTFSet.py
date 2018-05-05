# get a set of planning tf (connected to loads with mult step up tf) which are still to be mapped even after the application of tryNumericTFMatching

from tryNumericTFMatchingEvenSingle import planningTFMappedSet, tfNameDict
from checkLoadSplit import multTFLoad, singleTFSet
listUnmappedTF = 'listUnmappedTF.txt'
listUnmappedTFSingle = 'listUnmappedTFSingle.txt'
unmappedTFLines = []
unmappedTFLinesSingle = []

planningLoadTFSet = set() # set of all tf belonging to planning Comed LV load buses which are connected to multiple step up tf
planningLoadTFSetSingle = set() # set of all tf belonging to planning Comed LV load buses which are connected to single step up tf only
# get a set of the step up load tf in planning
for bus in list(multTFLoad):
	for tfData in tfNameDict[bus]:
		planningTFID = tfData[1]
		planningLoadTFSet.add(planningTFID)

# single step up tf case
for bus in list(singleTFSet):
	for tfData in tfNameDict[bus]:
		planningTFID = tfData[1]
		planningLoadTFSetSingle.add(planningTFID)



# see which of these tf are not there in the mapped tf set
for tf in list(planningLoadTFSet):
	if tf not in planningTFMappedSet:
		#print tf
		unmappedTFLines.append(tf)

# single step up tf case
for tf in list(planningLoadTFSetSingle):
	if tf not in planningTFMappedSet:
		#print tf
		unmappedTFLinesSingle.append(tf)

#print unmappedTFLinesSingle
with open(listUnmappedTF,'w') as f:
	f.write('List of mult tf step up still need to be mapped:')
	f.write('\n')
	for line in unmappedTFLines:
		f.write(line)
		f.write('\n')

with open(listUnmappedTFSingle,'w') as f:
	f.write('List of single tf step up still need to be mapped:')
	f.write('\n')
	for line in unmappedTFLinesSingle:
		f.write(line)
		f.write('\n')