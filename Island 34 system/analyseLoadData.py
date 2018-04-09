# generate a set of all comed load buses
# if load bus volt > 40 kV, move on to next one
# if load bus volt within 30 and 40 kV, its a special case, need to investigate
# if load bus is only connected to transformers, check the tf windings. If any of the tf windings belong to 138 kV, we ignore any of the LV neighbours of the load bus
# if the load bus is not connected to transformers, then its a special case. We need to investigate the branches of the load bus to see which branch  connects to the HV system
# through step up
# if the tf connections of the load bus are also LV buses, then see if the neighbour is 34 kV and its connected to 138 or above. Then add the neighbour to important 34 bus list
from generateNeighbours import BranchConnDict, tfConnDict

#NewRaw = 'NewCAPERawClean.raw'
NewRaw = 'RAW0406018.raw'
LoadBusNoChangeLogOld = 'LoadBusNoChangeLogOld.txt'
#LoadBusNoChangeLogNew = 'LoadBusNoChangeLogNew.txt'
list_imp34_load = 'list_imp34_load.txt'

BusVoltDict = {}
ComedLoadSet = set()
loadBus34Set = set()
LoadMapDict = {}
LoadMapDictCAPE  = {}
ChangedLoadMapDict = {} # dictionary of changed load mappings only
#map_bus_file_old = 'mapped_buses_cleaned0313.csv'
#map_bus_file_new = 'mapped_buses_cleaned0407.csv'
with open(LoadBusNoChangeLogOld,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'CAPE' in line:
			continue

		words = line.split('->')
		if len(words)<2:
			continue
		PSSEBus = words[0].strip()
		CAPEBus = words[1].strip()
		LoadMapDict[PSSEBus] = CAPEBus
		LoadMapDictCAPE[CAPEBus] = PSSEBus




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

			for neighbour in BranchConnDict[load]:
				if neighbour in tfConnDict.keys():
					neighbourDepth2 = tfConnDict[neighbour]
					for n2 in neighbourDepth2:
						if BusVoltDict[n2] > 40.0:
							# change mapping
							PSSEBus = LoadMapDictCAPE[load] # get the PSSE load bus
							LoadMapDict[PSSEBus] = neighbour # map the PSSE load bus to this newfound bus (which connects directly to a tf)
							ChangedLoadMapDict[PSSEBus] = neighbour
							HVtfNeighbourFound = 1
							break

					if HVtfNeighbourFound == 1:
						break

			if HVtfNeighbourFound == 1:
				continue

			print load


		#print load
	


print 'Verified that all 34 kV load buses are connected to HV buses through step up transformer!'
print 'Verified that all LV buses are connected to HV buses through step up transformer in testRAW04052018_fixedload.raw and RAW0406018.raw'
#print count


"""
# log file of load bus number change
with open(LoadBusNoChangeLogNew,'w') as f:
	f.write('PSSEBus->CAPEBus\n')
	for key in LoadMapDict:
		mapStr = key + '->' + LoadMapDict[key]
		f.write(mapStr)
		f.write('\n')



# did this before, no need to do this again
# incorporate changedLoadMapDict at the end of map_bus0313.csv, and then check whether everything matches up 
mapped_bus_newLines = []

with open(map_bus_file_old,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		mapped_bus_newLines.append(line)



for key in ChangedLoadMapDict.keys():
	line = key + ',,,,=,' + ChangedLoadMapDict[key] + ',,,BG,,New load mappings from analyseLoadData.py,,,'
	mapped_bus_newLines.append(line)


with  open(map_bus_file_new,'w') as f:
	for line in mapped_bus_newLines:
		f.write(line)
		f.write('\n')
"""

# 
with open(list_imp34_load,'w') as f:
	f.write('List of imp 34 kv buses for load data')
	f.write('\n')
	for bus in list(loadBus34Set):
		f.write(bus)
		f.write('\n')
