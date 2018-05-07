# starting from a bus whose mapping is definite, map neighbours comparing branch impedance values
# if branch impedance values are small, map those buses to the same planning bus
# if branch impedance values are not small and they have no comparable mapping, flag those CAPE buses


from generateBranchNeighboursFn import generateNeighbours # function which generates in-service branch neighbour dictionary given raw file

CAPERaw = 'Raw0501.raw'
planningRaw = 'hls18v1dyn_new.raw'
ManualMapFile = 'test_automation.txt'
changeLog = 'changeBusNoLog.txt'
sortedMismatchData345 = 'sortedMismatchData345.txt'

ManualMappingDict = {} # dict constructed from the entries given in the manual map file
autoMapDict = {} # dictionary which generates mapping
autoMappedSet =set()
changeDictNewToOld ={}
changeDictOldToNew = {}
mismatchBusSet345 = set()
noMismatch345Set = set()
ComedCAPESet345 = set()
matchLines = []


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
			if BusVolt >= 345.0:
				ComedCAPESet345.add(Bus)
				if Bus not in mismatchBusSet345 and not name.startswith('T3W'):
					noMismatch345Set.add(Bus)
					matchLines.append(line)

##############################

for line in matchLines:
	print line






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


# get a list of all 345 buses which do not show any mismatch
# then look at a depth of 1 and try to map stuff

# generate a script which can map tf data
# use it to do the following in Raw_loadsplit.raw:
# 274753,369,1->274753,400011,1
# 274754,369,1->274754,400011,1
# 274750,369,1->750083,400011,1
