# get a set of planning tf (connected to loads with mult step up tf) which are still to be mapped even after the application of tryNumericTFMatching

from tryNumericTFMatching import planningTFMappedSet, tfNameDict
from checkLoadSplit import multTFLoad


planningLoadTFSet = set() # set of all tf belonging to planning Comed LV load buses
# get a set of the step up load tf in planning
for bus in list(multTFLoad):
	for tfData in tfNameDict[bus]:
		planningTFID = tfData[1]
		planningLoadTFSet.add(planningTFID)

# see which of these tf are not there in the mapped tf set
for tf in list(planningLoadTFSet):
	if tf not in planningTFMappedSet:
		print tf
