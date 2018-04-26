changeLog = 'changeBusNoLog.txt'
MapLog = 'AllMappedLog.txt'
verifiedMapFile = 'PSSEGenMapVerified.txt'

oldNoDict = {} # keys: Old (original) CAPE bus numbers, values: new CAPE bus numbers
MapDict = {} # keys: Original CAPE bus numbers, values: corresponding planning numbers

def getPlanningBusNo(CAPEBus,oldNoDict,MapDict):
	"""
	function to get planning bus number, given original or changed CAPE number
	"""
	if CAPEBus in oldNoDict.keys():
		OriginalCAPENo = oldNoDict[CAPEBus]
	else:
		OriginalCAPENo = CAPEBus

	planningBusNo = MapDict[OriginalCAPENo]

	return planningBusNo




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
		#OldBusSet.add(OldBus)
		#NewBusSet.add(NewBus)
		oldNoDict[NewBus] = OldBus

with open(MapLog,'r') as f:
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
		MapDict[CAPEBus] = PSSEBus	



# open up the verified gen map file and extract the info into a set and a dictionary
with open(verifiedMapFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'Manual' in line:
			continue
		words = line.split(',')
		if len(words) < 2:
			continue
		PSSEBus = words[0].strip()
		#CAPEBus = words[5].strip()
		TrueGenBusSet.add(PSSEBus)
		#CAPEBusSet.add(CAPEBus)
		#MapDict[CAPEBus] = PSSEBus


# open up CAPE tf data
# if any of the bus in the tf data is a true gen, write a function to get the corresponding data
# build a dictionary which has transformer bus info as key, and a list which has all the needed data (CW, CZ, Impedance info)



#print getPlanningBusNo('750333',oldNoDict,MapDict)

