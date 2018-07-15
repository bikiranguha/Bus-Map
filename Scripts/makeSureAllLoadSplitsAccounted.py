import sys

sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/')
from getTFDataFn import getTFData
from generateBranchNeighboursFn import getBranchNeighbours

autoTFMapFile = 'autoTFMap0505.txt'
planningRaw = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/' +  'hls18v1dyn_1219.raw'
ComedLVBusSet = set()
ComedLVLoadSet = set()
BusVoltDict = {}
BusLine = {}
planningTFKeySet = set()
TFDataDict = getTFData(planningRaw)
BranchNeighbourDict = getBranchNeighbours(planningRaw)


with open(autoTFMapFile, 'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if '->' not in line:
			continue
		words = line.split('->')
		planningTFKey = words[0].strip()
		planningTFKeySet.add(planningTFKey)




# get the relevant comed bus sets
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
			BusLine[Bus] = line
			#ComedBusSet.add(Bus)
			if BusVolt < 40.0:
				ComedLVBusSet.add(Bus)


loadStartIndex = fileLines.index('0 / END OF BUS DATA, BEGIN LOAD DATA') + 1
loadEndIndex = fileLines.index('0 / END OF LOAD DATA, BEGIN FIXED SHUNT DATA')

# scan load data to populate load sets and dictionaries
for i in range(loadStartIndex,loadEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus  = words[0].strip()
	Load = float(words[5].strip())
	if Bus in ComedLVBusSet and Load > 0.0:
		ComedLVLoadSet.add(Bus)


for Bus in list(ComedLVLoadSet):
	found = 0
	if Bus in TFDataDict.keys() and Bus not in BranchNeighbourDict.keys():
		toBuses = TFDataDict[Bus].toBus
		for i in range(len(toBuses)):
			to = toBuses[i]
			ID = TFDataDict[Bus].cktID[i]
			tfKey = Bus + ',' + to + ',' + ID
			tfKeyReverse = to + ',' + Bus + ',' + ID
			if tfKey in planningTFKeySet:
				found = 1
				break
			elif tfKeyReverse in planningTFKeySet:
				found = 1
				break

		if found == 0:
			print 'Investigate why tf not present: ' + tfKey + ' or ' + tfKeyReverse


