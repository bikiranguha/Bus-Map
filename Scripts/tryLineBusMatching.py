"""
Look at the output of the 345 auto mapping using branch impedance
For all cases where branch impedance did match, but substation info did not match, see if all the branches can be mapped
	If yes, then its the correct match
"""
from generateBranchNeighboursFn import generateNeighbours
mapping345Output = 'output345.txt'
ImpedanceMatchNotSubMatchSet = set()
CAPERaw = 'Raw0509.raw'
planningRaw = 'hls18v1dyn_new.raw'
autoMapped345File = 'Automated345MapFile.txt'

_, BranchDataDictPlanning = generateNeighbours(planningRaw)
_, BranchDataDictCAPE = generateNeighbours(CAPERaw)
newMatchDict = {}
foundMatchSetPlanning = set()
foundMatchSetCAPE = set()
mappedCAPEBusSet = set()

# get the set of planning, CAPE match pairs
with open(mapping345Output,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'is an impedance match but not substation match to' not in line:
			continue
		splitList = line.split('is an impedance match but not substation match to')
		PlanningBus = splitList[0].strip()
		CAPESide = splitList[1].strip()
		CAPESideWords = CAPESide.split(',')
		CAPEBus = CAPESideWords[0].strip()
		pair = PlanningBus + ',' + CAPEBus
		ImpedanceMatchNotSubMatchSet.add(pair)

# get the set of mapped CAPE buses
with open(autoMapped345File,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue

		if 'CAPE' in line:
			continue

		words = line.split('->')
		CAPEBus = words[0].strip()
		mappedCAPEBusSet.add(CAPEBus)




# If all line connections match, say its a map and move to the next thing on the list

for busPair in list(ImpedanceMatchNotSubMatchSet):
	busPairWords = busPair.split(',')
	planningBus = busPairWords[0].strip()
	CAPEBus = busPairWords[1].strip()

	if planningBus in foundMatchSetPlanning:
		continue

	if CAPEBus in foundMatchSetCAPE or CAPEBus in mappedCAPEBusSet:
		continue


	# see if both sides have branches
	try:
		PlanningBranchList = BranchDataDictPlanning[planningBus].toBus
	except: # planning bus has no branches
		continue

	try:
		CAPEBranchList = BranchDataDictCAPE[CAPEBus].toBus
	except: # CAPE bus has no branches
		continue


	unMappedPlanningBranchList = list(PlanningBranchList)
	for planningNeighbour in PlanningBranchList:
		PlanningBranchInd = PlanningBranchList.index(planningNeighbour)
		PlanningBranchZ = BranchDataDictPlanning[planningBus].Z[PlanningBranchInd]
		for CAPENeighbour in CAPEBranchList:
			CAPEBranchInd = CAPEBranchList.index(CAPENeighbour)
			CAPEBranchZ = BranchDataDictCAPE[CAPEBus].Z[CAPEBranchInd]

			error = abs((PlanningBranchZ - CAPEBranchZ)/PlanningBranchZ)*100

			if error < 5.0:
				#newMatchDict[planningBus] = CAPEBus
				#foundMatchSetCAPE.add(CAPEBus)
				#foundMatchSetPlanning.add(planningBus)
				unMappedPlanningBranchList.remove(planningNeighbour)
				break

	if len(unMappedPlanningBranchList) == 0:
		newMatchDict[planningBus] = CAPEBus
		foundMatchSetCAPE.add(CAPEBus)
		foundMatchSetPlanning.add(planningBus)		






