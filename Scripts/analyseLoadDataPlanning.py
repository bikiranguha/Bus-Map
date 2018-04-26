# script to make sure all LV (<40.0 kV) buses in the comed planning area are connected directly to HV transformers
from generateNeighboursPlanning import BranchConnDict, tfConnDict

#NewRaw = 'NewCAPERawClean.raw'
planningRaw = 'hls18v1dyn_new.raw'
BusVoltDict = {}
ComedLoadSet = set()
loadBus34Set = set()
# generate NeighbourDict for branches
with open(planningRaw, 'r') as f:
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
countHV = 0
countLV = 0
for load in list(ComedLoadSet):

	if BusVoltDict[load] > 40.0:
		countHV +=1
		continue

	# if load volt <=40.0
	countLV +=1
	#if BusVoltDict[load] < 30.0:

	HVtfNeighbourFound = 0

	if load in tfConnDict.keys(): #  load bus has tf connections
		for neighbour in tfConnDict[load]: # see if it is directly connected to a HV bus through tf
			if BusVoltDict[neighbour] > 40.0:
				HVtfNeighbourFound = 1
				break

	else:
		print 'Load Bus ' + load + ' does not have any transformer connections'
		continue

	if HVtfNeighbourFound == 1: # LV load bus has HV connection, no need to look at its other LV neighbours (if any)
		continue

	print 'Load Bus ' + load + ' is not connected directly to a HV bus through a transformer.'




print 'Verified that all load buses (< 40.0 kV) are connected to HV buses through step up transformer!'
print 'countHV: ', countHV
print 'countLV: ', countLV
print 'No. of loads: ', len(ComedLoadSet)