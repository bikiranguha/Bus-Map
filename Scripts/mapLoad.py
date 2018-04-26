#newdir = 'Important data'
planningRaw = 'hls18v1dyn_1219.raw'
manualMapFile = 'mapped_buses_cleaned_for_load.csv'
#mapped_buses = 'mapped_buses_cleaned.csv'
newLoadData = 'newLoadData.txt'
changeLog = 'changeBusNoLog.txt'
AllMapFile = 'AllMappingMod.log'
#outsideComedFile = 'outsideComedBusesv3.txt'
LoadBusNoChangeLog = 'LoadBusNoChangeLog.txt'



PSSEBusSet = set()
PSSEGenBusSet = set()
mapping_done = set()
#loadMapDict = {}
loadLines = []
changeNameDict = {}
MapDict = {} #first map dict to look at
OldBusSet = set()
NewBusSet = set()
noNeedtoMapSet = set()
ComedBusSet = set()
#TieDict = {}
ManualMapDict = {} # backup map dict to look at
loadBusNoChangeDict = {}


# the new load data looks here first for possible load bus number change
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
		MapDict[PSSEBus] = CAPEBus	



# if it cannot find the load bus number change, it tries here
# open the simple map and generate a dictionary of PSSE->CAPE maps, also generate sets of PSSE and CAPE buses to be mapped
with open(manualMapFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		words = line.split(',')
		if len(words) <2:
			continue
		PSSEBus = words[0].strip()
		CAPEBus = words[5].strip()
		PSSEBusCode = words[2].strip()
		if 'M' in PSSEBusCode:
			continue
		if PSSEBus in ['NA','']:
			continue
		if CAPEBus in ['NA','']:
			continue

		ManualMapDict[PSSEBus] = CAPEBus


"""
# get a tie dictionary for each comed bus
def BusAppend(Bus,NeighbourBus,TieDict):
	if Bus not in TieDict.keys():
		TieDict[Bus] = []
	TieDict[Bus].append(NeighbourBus)
"""
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
		area = words[4].strip()
		if area == '222':
			ComedBusSet.add(Bus)
		#AreaDict[Bus] = area

"""
branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA') + 1
branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')
tieZValues = [['0.00000E+0','1.00000E-5'],['0.00000E+0','1.50000E-4'],['0.00000E+0','1.00000E-4']]
for i in range(branchStartIndex, branchEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	R = words[3].strip()
	X = words[4].strip()
	if Bus1 in ComedBusSet:
		if Bus2 in ComedBusSet:
			if [R,X] in tieZValues:
				BusAppend(Bus1,Bus2,TieDict)
				BusAppend(Bus2,Bus1,TieDict)
"""
####
		
		




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
		NewBusSet.add(NewBus)
		changeNameDict[OldBus] = NewBus





with open(planningRaw,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

loadStartIndex = fileLines.index('0 / END OF BUS DATA, BEGIN LOAD DATA') + 1
loadEndIndex = fileLines.index('0 / END OF LOAD DATA, BEGIN FIXED SHUNT DATA')


for i in range(loadStartIndex,loadEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus  = words[0].strip()

	area = words[3].strip()

	if area == '222':
		PSSEBusSet.add(Bus) # Has been verified that no load bus contains multiple entries, also that gen and load bus are mutuall exclusive
		loadLines.append(line)


# generate new load data
with open(newLoadData,'w') as f:
	for line in loadLines:
		currentline = ''
		words = line.split(',')
		Bus = words[0].strip()
		try:
			CAPEBus = MapDict[Bus]
			loadBusNoChangeDict[Bus] = CAPEBus
		except:
			try:
				CAPEBus = ManualMapDict[Bus]
				loadBusNoChangeDict[Bus] = CAPEBus
			except:
				print Bus
		if CAPEBus in OldBusSet:
			CAPEBus = changeNameDict[CAPEBus]
			loadBusNoChangeDict[Bus] = CAPEBus
		words[0] = ' '*(6-len(CAPEBus)) + CAPEBus
		ind = 1
		for word in words:
			currentline += word
			if ind != len(words):
				currentline += ','
				ind+=1


		f.write(currentline)
		f.write('\n')




# log file of load bus number change
with open(LoadBusNoChangeLog,'w') as f:
	f.write('PSSEBus->CAPEBus\n')
	for key in loadBusNoChangeDict:
		mapStr = key + '->' + loadBusNoChangeDict[key]
		f.write(mapStr)
		f.write('\n')


duplicateDict = {}
with open(LoadBusNoChangeLog,'r') as f:
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
		if CAPEBus not in duplicateDict.keys():
			duplicateDict[CAPEBus] = []
		duplicateDict[CAPEBus].append(PSSEBus)
"""
for key in duplicateDict.keys():
	if len(duplicateDict[key])>1:
		print key + ' : ' + str(duplicateDict[key]) 
"""

import loadConflictResolution # Avoid conflicts in load mapping

