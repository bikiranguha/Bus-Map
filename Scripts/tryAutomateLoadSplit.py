"""
Incomplete script: Reads the auto map and manual map files to get combined mapping info.
Original intention was to automate the mapping, but too hard at that time
"""

from checkLoadSplit import NumLoadTFDict, multTFLoad


# list of files
loadBusNoChangeLog = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/' +  'LoadBusNoChangeLog.txt'
mapFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/' + 'mapped_buses_cleaned0407.csv'
rawFileOld = 'Raw0414tmp_loadsplit.raw'

loadMapDict = {}
ManualMapDict = {} # dict where the maps of the mult load buses are 
combinedMapDict = {} # key: loads which have mult tf conn, values: maps in loadBusNoChangelog and mapFile
loadMapDictCAPE = {}

# get map info
with open(loadBusNoChangeLog,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')


	for line in fileLines:
		if 'CAPE' in line:
			continue
		if line == '':
			continue
		words = line.split('->')
		planningBus = words[0].strip()
		CAPEBus = words[1].strip()
		if planningBus not in loadMapDict.keys():
			loadMapDict[planningBus] = CAPEBus
			loadMapDictCAPE[CAPEBus] = planningBus
		else:
			print CAPEBus

# get maps of multTFLoad
with open(mapFile,'r') as f:
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

		if PSSEBus in multTFLoad:
			if PSSEBus not in ManualMapDict.keys():
				ManualMapDict[PSSEBus] = set()
				ManualMapDict[PSSEBus].add(CAPEBus)
			else:
				ManualMapDict[PSSEBus].add(CAPEBus)

# combine the two maps

combinedMapDict = dict(ManualMapDict)
for bus in ManualMapDict.keys():
	if bus in loadMapDict.keys():
		combinedMapDict[bus].add(loadMapDict[bus])
