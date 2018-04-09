# script to check if the changes made in analyseLoadData.py worked


from generateNeighbours import BranchConnDict, tfConnDict

#NewRaw = 'NewCAPERawClean.raw'
NewRaw = 'RAW0406018.raw'
LoadBusNoChangeLogOld = 'LoadBusNoChangeLog.txt'
#LoadBusNoChangeLogNew = 'LoadBusNoChangeLogNew.txt'
BusVoltDict = {}
ComedLoadSet = set()
loadBus34Set = set()
LoadMapDict = {}
LoadMapDictCAPE  = {}
ChangedLoadMapDict = {} # dictionary of changed load mappings only






# generate NeighbourDict for branches
with open(NewRaw, 'r') as f:
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
		BusVolt = float(words[2].strip())
		#angle = float(words[8].strip())
		area = words[4].strip()
		#AreaDict[Bus] = area

		if area == '222':
			#BusAngleDict[Bus] = angle
			BusVoltDict[Bus] = BusVolt
			#ComedBusSet.add(Bus)

# get a set of all comed load buses
loadStartIndex = fileLines.index('0 / END OF BUS DATA, BEGIN LOAD DATA') + 1
loadEndIndex = fileLines.index('0 / END OF LOAD DATA, BEGIN FIXED SHUNT DATA')


for i in range(loadStartIndex,loadEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus  = words[0].strip()

	area = words[3].strip()

	if area == '222':
		ComedLoadSet.add(Bus) # Has been verified that no load bus contains multiple entries, also that gen and load bus are mutuall exclusive



# analyze each load
count = 0
for load in list(ComedLoadSet):
	if BusVoltDict[load] > 40.0: # skip if the load volt > 40.0
		count +=1
		continue
		#print load
		

	# investigate 34 kv buses
	if BusVoltDict[load] <40.0 and BusVoltDict[load] > 30.0:
		count +=1
		loadBus34Set.add(load)
		HVtfNeighbourFound = 0
		#print load
		if load in tfConnDict.keys():
			for neighbour in tfConnDict[load]:
				if BusVoltDict[neighbour] > 40.0:
					HVtfNeighbourFound = 1
					break

		if HVtfNeighbourFound == 1: # 34 kV load bus has HV connection, no need to look at its other LV neighbours (if any)
			continue

	else: # LV buses
		HVtfNeighbourFound = 0

		if load in tfConnDict.keys():
			for neighbour in tfConnDict[load]:
				if BusVoltDict[neighbour] > 40.0:
					HVtfNeighbourFound = 1
					break
			if HVtfNeighbourFound == 1: # LV load bus has HV connection, no need to look at its other LV neighbours (if any)
				continue
			
			#else: # connected to tf but not step up (no such cases)
			#	print load

		else: # load bus has no direct tf connections, need to map the load bus to a neighbour which has direct HV tf connections


			print load
		