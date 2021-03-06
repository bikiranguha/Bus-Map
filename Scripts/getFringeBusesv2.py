# get the path from the three 138 kV substations where the SVCs are at, to nearest 345
# get all the buses connected to 345 directly (or through midpoints)
# get all the COMED boundary buses
import sys
sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2')
sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/Automate 345 kV mapping')
from getBusDataFn import getBusData
from getCAPESubstationDict import SubStationDictNew # key: substation name, value: list of all buses (new bus numbers) belonging to the substation
from findPathTo345Fn import generate345PathList
from getTFDataFn import getTFData
from writeFileFn import writeToFile
from generateNeighboursFn import getNeighbours
from getBranchGroupFn import makeBranchGroups 

CAPERaw = 'RAW0602.raw'
changeLog = 'changeBusNoLog.txt'
Imp138PathFile = 'Imp138PathFile.txt'
directTFConnFile = 'directTFConnFile.txt'
AllToBeMappedFile = 'AllToBeMappedFile.txt'
ArtificialLoadBusFile = 'ArtificialLoadBusFile.txt'
Imp138PathSet = set()
Imp138Depth1Set = set()
CAPEBusDataDict = getBusData(CAPERaw)
CAPENeighboursDict = getNeighbours(CAPERaw)
ArtificialLoadBusSet = set()
necessaryMidpointSet = set() # set of tf midpoints which need to be there
ParentDict = {}
AllToBeMappedSet = set() # All the non-345 comed buses to be mapped
toGetPathSet = set() # set of 138 kV belonging to the 3 SVC substations, from which we need to get paths to 345
OldToNewBusDict = {} # key: new CAPE bus number, old: old CAPE bus number
# get the path from the three 138 kV substations where the SVCs are at, to nearest 345
impSubStationList = ['TSS 135 ELMHURST', 'TSS 117 PROSPECT HEIGHTS', 'STA 13 CRAWFORD']
AllToBeMappedLines = []
OldBusSet = set()
directTFConnLines = []
BoundaryBusSet = set()
CAPEBranchGroupDict = makeBranchGroups(CAPERaw)
ArtificialLoadLines = []



def populatePathDict(FromBus,toBus):
	# info needed for getting artificial load bus flows
	if toBus not in ParentDict.keys():
		ParentDict[toBus] = FromBus
	else:
		try:
			ParentBusGroup = CAPEBranchGroupDict[ParentDict[toBus]]
			if FromBus in ParentBusGroup:
				return
			ParentDict[toBus] += ',' +  FromBus
		except:
			ParentDict[toBus] += ',' +  FromBus




# look at log files which contains all the changed bus number
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
        OldBusSet.add(OldBus)
        OldToNewBusDict[OldBus] = NewBus


# get all the important 138 starting buses
for substation in impSubStationList:
	BusList = SubStationDictNew[substation]
	for Bus in BusList:
		if Bus in OldBusSet:
			Bus = OldToNewBusDict[Bus]
		try:
			BusVolt = float(CAPEBusDataDict[Bus].NominalVolt)
		except:
			continue
			#print Bus + ' is a special case. Please investigate.'
		if BusVolt == 138.0:
			toGetPathSet.add(Bus)


# get paths to 345 
Imp138PathDict = generate345PathList(CAPERaw,list(toGetPathSet)) # key: Important 138 bus, value: path, starting from the 138, ending in a 345
# generate a set of buses which belong to this path:


Imp138FileLines = []
for key in Imp138PathDict.keys():
	Imp138FileLines.append(Imp138PathDict[key])
	path = Imp138PathDict[key]
	words = path.split('->')
	for bus in words:
		if float(CAPEBusDataDict[bus].NominalVolt) < 345.0:
			Imp138PathSet.add(bus.strip())

writeToFile(Imp138PathFile,Imp138FileLines,'Path from Important 138 to nearest 345 (depthwise):')
#print Imp138PathSet




# get all the buses connected to 345 directly (or through midpoints)
directTFConnSet = set()
TFDataDict = getTFData(CAPERaw) # keys are the buses having transformers
for Bus in CAPEBusDataDict.keys():
	Area = CAPEBusDataDict[Bus].area 
	Volt = float(CAPEBusDataDict[Bus].NominalVolt)
	if Area == '222' and Volt >= 345.0 and Bus in TFDataDict.keys():
		toBusList = TFDataDict[Bus].toBus

		for tfNeighbour in toBusList:
			
			# deal with midpoints, get its neighbours which are not the bus itself
			NeighbourName = CAPEBusDataDict[tfNeighbour].name
			if NeighbourName.startswith('T3W') or NeighbourName.endswith('M'):
				necessaryMidpointSet.add(tfNeighbour)
				Depth2Neighbours = TFDataDict[tfNeighbour].toBus
				for d2Neighbour in Depth2Neighbours:
					if d2Neighbour != Bus and float(CAPEBusDataDict[d2Neighbour].NominalVolt) < 345.0:
						populatePathDict(tfNeighbour,d2Neighbour)
						directTFConnSet.add(d2Neighbour)
			else:
				# ignore step up transformers or windings which are at the same voltage level
				if float(CAPEBusDataDict[tfNeighbour].NominalVolt) >=345.0:
					continue

				# info needed for getting artificial load bus flows
				if tfNeighbour not in ParentDict.keys():
					populatePathDict(Bus,tfNeighbour)
				directTFConnSet.add(tfNeighbour)

# output the list of buses
for Bus in list(directTFConnSet):
	BusName = CAPEBusDataDict[Bus].name
	BusVolt = CAPEBusDataDict[Bus].NominalVolt
	string = Bus + ',' + BusName + ',' + BusVolt
	directTFConnLines.append(string)
writeToFile(directTFConnFile,directTFConnLines,'List of buses which are directly connected to Comed 345:')

# get the boundary bus set

for Bus in CAPEBusDataDict.keys():
	if CAPEBusDataDict[Bus].area == '222' and float(CAPEBusDataDict[Bus].NominalVolt) < 345.0:
		neighboursList = list(CAPENeighboursDict[Bus])
		for neighbour in neighboursList:
			if CAPEBusDataDict[neighbour].area != '222' :
				populatePathDict(neighbour,Bus)
				BoundaryBusSet.add(Bus)
				break

#print BoundaryBusSet
# generate a super set, which comprises all the non-345 Comed set which need to be included and mapped properly. 
for Bus in directTFConnSet:
	if float(CAPEBusDataDict[Bus].NominalVolt) >= 345.0:
		print 'In direct TF connections, there is 345 bus present, please fix:'
		print Bus
	AllToBeMappedSet.add(Bus)

for Bus in Imp138PathSet:
	if float(CAPEBusDataDict[Bus].NominalVolt) >= 345.0:
		print 'In Imp 138,  there is 345 bus present, please fix:'
		print Bus
	AllToBeMappedSet.add(Bus)

for Bus in BoundaryBusSet:
	if float(CAPEBusDataDict[Bus].NominalVolt) >= 345.0:
		print 'In Boundary,  there is 345 bus present, please fix:'
		print Bus
	AllToBeMappedSet.add(Bus)
# Generate an artificial load bus set, whose elements are those in directTFConnSet and BoundaryBusSet which are not in Imp138PathSet. Also includes depth 1 of Imp138PathSet.
for Bus in list(Imp138PathSet):
	if Bus not in CAPEBranchGroupDict.keys(): # Bus has no ties
		neighbourList = list(CAPENeighboursDict[Bus])
		for neighbour in neighbourList:
			if neighbour not in Imp138PathSet and neighbour not in directTFConnSet and neighbour not in BoundaryBusSet:
				if float(CAPEBusDataDict[neighbour].NominalVolt) < 345.0:
					Imp138Depth1Set.add(neighbour)
					populatePathDict(Bus,neighbour)


					ArtificialLoadBusSet.add(neighbour)  # belong to artificial loads
	else: # Bus has ties, add ties to Imp138Path and scan for actual neighbours (connected through branches) to add to Imp138depth1Set
		print Bus
		BusGroup = list(CAPEBranchGroupDict[Bus]) # any ties to the bus are got here
		for tie in BusGroup:
			Imp138PathSet.add(tie)
			tieNeighbourList = list(CAPENeighboursDict[tie])
			for tieNeighbour in tieNeighbourList:
				if tieNeighbour not in BusGroup and tieNeighbour not in Imp138PathSet:
					if float(CAPEBusDataDict[tieNeighbour].NominalVolt) < 345.0:
						Imp138Depth1Set.add(tieNeighbour)
						populatePathDict(tie,tieNeighbour)
						ArtificialLoadBusSet.add(tieNeighbour)  # belong to artificial loads




# need to be mapped as well
for Bus in Imp138Depth1Set:
	if float(CAPEBusDataDict[Bus].NominalVolt) >= 345.0:
		print 'In Imp 138 Depth 1:'
		print Bus
	AllToBeMappedSet.add(Bus)


for Bus in necessaryMidpointSet:
	AllToBeMappedSet.add(Bus)

for Bus in list(AllToBeMappedSet):
	BusName = CAPEBusDataDict[Bus].name
	BusVolt = CAPEBusDataDict[Bus].NominalVolt
	string = Bus + ',' + BusName + ',' + BusVolt
	if float(BusVolt) > 138.0:
		print string
	AllToBeMappedLines.append(string)
writeToFile(AllToBeMappedFile,AllToBeMappedLines,'List of buses which need to be mapped:')

# add remaining cases to artificial load bus set
for Bus in directTFConnSet:
	if Bus not in Imp138PathSet and CAPEBusDataDict[Bus].type != '2':
		ArtificialLoadBusSet.add(Bus)

for Bus in BoundaryBusSet:
	if Bus not in Imp138PathSet and CAPEBusDataDict[Bus].type != '2':
		ArtificialLoadBusSet.add(Bus)

for Bus in list(ArtificialLoadBusSet):
	BusName = CAPEBusDataDict[Bus].name
	BusVolt = CAPEBusDataDict[Bus].NominalVolt
	string = Bus + ',' + BusName + ',' + BusVolt + ',' + ParentDict[Bus]
	if float(BusVolt) > 138.0:
		print string
	ArtificialLoadLines.append(string)	
writeToFile(ArtificialLoadBusFile,ArtificialLoadLines,'List of buses which will be converted to artificial loads. Format: Bus, Name, Volt, List of neighbours which will be present')


import scanArtificialLoadData

