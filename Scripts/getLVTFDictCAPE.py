"""
"""
from loadSplitCAPE import ComedLVBusSet # all LV buses in comed in the CAPE raw file

#planningRaw = 'hls18v1dyn_1219.raw'
CAPERaw = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/Island 34 system/' +  'Raw0414tmp_loadsplit.raw'
#listMultTFfile = 'listMultTFfileCAPE.txt'


tfKeyDict = {} # key: LV CAPE bus, values: whole tf id of tf connection to it (Bus1, Bus2, ckt id) 



# get the relevant comed bus sets
with open(CAPERaw, 'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')



tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')
i = tfStartIndex
# search tf data to populate LVTFDataDict
while i < tfEndIndex:
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	cktID = words[3].strip("'").strip()
	status = words[11].strip()
	#tfname = words[10].strip("'").strip()

	if Bus1 in ComedLVBusSet or Bus2 in ComedLVBusSet:
		if status == '1':
			key = Bus1 + ',' + Bus2 + ',' + cktID

			# generate tfNameDict
			if Bus1 in ComedLVBusSet:
				keyBus = Bus1 # keyBus is the LV bus
			else:
				keyBus = Bus2

			if keyBus not in tfKeyDict.keys():
				tfKeyDict[keyBus] = [key]
			else:
				tfKeyDict[keyBus].append(key)

		i+=4 # continue to next tf

	else:
		i+=4
