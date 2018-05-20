# starting from a bus whose mapping is definite, map neighbours comparing branch impedance values
# if branch impedance values are small, map those buses to the same planning bus
# if branch impedance values are not small and they have no comparable mapping, flag those CAPE buses


from generateBranchNeighboursFn import generateNeighbours # function which generates in-service branch neighbour dictionary given raw file
from getBranchGroupFn import makeBranchGroups # this function will help map any ties to buses which are already mapped
CAPERaw = 'Raw0501.raw'
planningRaw = 'hls18v1dyn_new.raw'
ManualMapFile = 'test_automation.txt'
changeLog = 'changeBusNoLog.txt'
sortedMismatchData345 = 'sortedMismatchData345.txt'
mapping_priority1 = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/' + 'mapping_priority1.txt'
AllMapFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/' + 'AllMappedLog.txt'
ManualMappingDict = {} # dict constructed from the entries given in the manual map file
autoMapDict = {} # dictionary which generates mapping
autoMappedSet =set()
changeDictNewToOld ={}
changeDictOldToNew = {}
mismatchBusSet345 = set()
noMismatch345Set = set() # set of 345 buses (not including fict midpoints) which show no mismatch
ComedCAPESet345 = set()
MapDict = {} # dict containing all CAPE bus maps (the bus numbers all include the latest numbers, ie, include 75xxxxx and 27xxxxx)
#matchLines = [] # set of 345 bus data which show no mismatch (with the exception of tf midpoints)


BranchDictCAPE, BranchDataDictCAPE = generateNeighbours(CAPERaw)
BranchDictPlanning, BranchDataDictPlanning = generateNeighbours(planningRaw)


# get a set of 345 buses showing no mismatch
with open(changeLog,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split('\n')
    for line in fileLines:
        if 'CAPE' in line:
            continue
        words = line.split('->')
        if len(words) < 2:
            continue
        OldBus = words[0].strip()
        NewBus = words[1].strip()
        changeDictNewToOld[NewBus] = OldBus
        changeDictOldToNew[OldBus] = NewBus


with open(sortedMismatchData345,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'Bus' in line:
			continue
		if line == '':
			continue
		words = line.split(',')
		Bus = words[0].strip()
		mismatchBusSet345.add(Bus)


with open(CAPERaw,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if ('PSS' in line) or ('COMED' in line) or ('DYNAMICS' in line):
			continue
		if 'END OF BUS DATA' in line:
			break
		words = line.split(',')
		if len(words) <2:
			continue
		Bus = words[0].strip()
		area = words[4].strip()

		if area == '222':
			#BusAngleDict[Bus] = angle
			#ComedBusSet.add(Bus)
			BusVolt = float(words[2].strip())
			#BusVoltDict[Bus] =BusVolt
			name = words[1].strip("'").strip()
			if BusVolt >= 345.0 and not name.startswith('T3W'):
				ComedCAPESet345.add(Bus)
				if Bus not in mismatchBusSet345:
					noMismatch345Set.add(Bus)
					#matchLines.append(line)

##############################

#for line in matchLines:
#	print line





# testing mapping of branch neighbours using comparison of branch impedances 
# ManualMapFile contains the mappings which have been verified
with open(ManualMapFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		# skip conditions
		#if 'Bus' in line:
		#	continue
		if line == '':
			continue
		##
		words = line.split('->')
		planningBus = words[0].strip()
		CAPEBus = words[1].strip()
		ManualMappingDict[CAPEBus] = planningBus

for CAPEBus in ManualMappingDict.keys():
	CAPEBranchList = BranchDataDictCAPE[CAPEBus].toBus
	CAPEBranchZ  = BranchDataDictCAPE[CAPEBus].Z

	planningBus = ManualMappingDict[CAPEBus]

	PlanningBranchList = BranchDataDictPlanning[planningBus].toBus
	PlanningBranchZ  = BranchDataDictPlanning[planningBus].Z


	for i in range(len(CAPEBranchList)):
		neighbour = CAPEBranchList[i]
		neighbourZ = CAPEBranchZ[i]

		for j in range(len(PlanningBranchList)):
			planningNeighbour = PlanningBranchList[j]
			planningNeighbourZ = PlanningBranchZ[j]

			error = abs((planningNeighbourZ - neighbourZ)/planningNeighbourZ)*100

			if error < 2.0:
				autoMapDict[neighbour] = planningNeighbour
				autoMappedSet.add(neighbour)
				break



# get all the ties to buses which have no mismatch
BranchGroupDict = makeBranchGroups(CAPERaw)
#for bus in list(noMismatch345Set):
	#if bus in BranchGroupDict.keys():
		#print bus

# get the highest priority maps first 
with open(mapping_priority1,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if '->' not in line:
			continue

		words = line.split('->')
		if len(words) < 2:
		    continue
		PSSEBus = words[0].strip()
		CAPEBus = words[1].strip()
		MapDict[CAPEBus] = PSSEBus 

# get all the remaining maps
# get all the previous mapped data 
with open(AllMapFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'CAPE' in line:
			continue

		words = line.split('->')
		if len(words) < 2:
		    continue
		PSSEBus = words[0].strip()
		CAPEBus = words[1].strip()
		if CAPEBus in changeDictOldToNew.keys():
			CAPEBus = changeDictOldToNew[CAPEBus]
		if CAPEBus in MapDict.keys():
			print CAPEBus
			continue
		MapDict[CAPEBus] = PSSEBus 



# map all the 345 buses with no mismatch and their ties


