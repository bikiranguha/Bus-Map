"""
For the CAPE comed LV load buses:
	Checks if the bus name ends with a two digit number (which may represent tf name). If yes, tries to match this number with tf connected to its mapped load bus in planning
	Also scan the depth 2 neighbours of the CAPE LV load bus for the same thing, ie, whether their bus name can be matched to tf names in the same planning bus
	This works in cases where the CAPE LV load bus is connected to one a single step up tf

	In cases where a CAPE LV Load bus is connected to multiple step up tf, we compare CAPE bus tf name to planning bus tf name.
	Same thing is done for all of its depth 2 neighbours. 
"""


# get a set of all LV load buses which have 2 digit names at the end, it represents the transformer digits
# look at the mapping of these load buses with special names and see if you can find transformer names with the same 2 digits

from tryAutomateLoadSplit import loadMapDictCAPE
from loadSplitCAPE import ComedLVLoadSet, BusNameDict, NumLoadTFDictCAPE, BusTypeDict
from generateLVTFDataDict import tfNameDict # dict which has LV planning bus as key, and values: [transformer name, tf key (bus1, bus2, ckt id)]
#from getLVTFDictCAPE import tfKeyDict
from depth2BranchConnLVLoadCAPE import Depth2Dict
from checkLoadSplit import multTFLoad
from generateLVTFNameCAPE import tfNameDictCAPE # dict which has LV CAPE bus as key, and values: [transformer name, tf key (bus1, bus2, ckt id)]
loadAlreadySplit = 'loadAlreadySplitList.txt'
tfMapFile = 'tfMapFile.txt'
tfMapLog = 'tfMapLog.txt'
logLinesNametoTF = [] # log of the tf connections which will be mapped using CAPE bus name to planning tf name
logLinesTFtoTF = [] # log of the tf connections which will be mapped using CAPE tf name to planning tf name
alreadySplitSet = set() # set of CAPE LV load buses which have been properly split in Raw_loadsplit.raw
mapLines = [] # lines of new tf mappings
planningTFMappedSet = set() # keeps track of which planning tf has already been mapped in this script
foundSplitSet = set() # set of CAPE for which we found splits in this script



def getNametoTFNameMatch(CAPEBus,planningBus,BusName, last2Digits,CAPETFID):
	# given a CAPEBus and its BusName and a planningbus:
		# tries to get a match between the last 2 digits of the CAPE Bus name and the planning bus tf name
	for tfData in tfNameDict[planningBus]:
		tfName = tfData[0]
		try:
			tfNameLast2Digits = int(tfName[-2:])
		except: # tf name does not contain number as last two digits
			continue
		if tfNameLast2Digits == last2Digits and tfData[1] not in planningTFMappedSet:
			"""
			if NumLoadTFDictCAPE[CAPEBus] > 1:
			 	print 'This is odd. Bus ' + CAPEBus + ' has tf name in its bus name but still has multiple transformers'
			"""
			# generate map log and the key map (to be used by loadMap.py)
			logString = CAPEBus + ',' + BusName + ',' + planningBus + ',' + tfName + ',' + tfData[1]
			logLinesNametoTF.append(logString)
			planningTFMappedSet.add(tfData[1]) # add to set which keeps track of which planning tf has already been mapped in this script

			planningTFID = tfData[1]
			#CAPETFID = tfNameCAPE
			mapStr = planningTFID + '->' + CAPETFID
			mapLines.append(mapStr)
			foundSplitSet.add(CAPEBus)

def getCAPEToPSSETFNameMatch(CAPEBus,planningBus,tfNameCAPE, BusName,last2Digits,CAPETFID):
	# given a CAPEBus and its tfName and a planningbus:
		# tries to get a match between the last 2 digits of the CAPE tf name and the planning bus tf name
	for tfData in tfNameDict[planningBus]:
		tfName = tfData[0]
		try:
			tfNameLast2Digits = int(tfName[-2:])
		except: # tf name does not contain number as last two digits
			continue
		if tfNameLast2Digits == last2Digits and tfData[1] not in planningTFMappedSet:
			"""
			if NumLoadTFDictCAPE[CAPEBus] > 1:
			 	print 'This is odd. Bus ' + CAPEBus + ' has tf name in its bus name but still has multiple transformers'
			"""
			# generate map log and the key map (to be used by loadMap.py)
			logString = CAPEBus + ',' + BusName + ',' + tfNameCAPE + ',' + planningBus + ',' + tfName + ',' + tfData[1]
			#print logString
			logLinesTFtoTF.append(logString)
			planningTFMappedSet.add(tfData[1]) # add to set which keeps track of which planning tf has already been mapped in this script

			planningTFID = tfData[1]
			#CAPETFID = tfKeyDict[CAPEBus]
			mapStr = planningTFID + '->' + CAPETFID
			mapLines.append(mapStr)
			foundSplitSet.add(CAPEBus)




# get a set of buses which have been split already
with open(loadAlreadySplit,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'List' in line:
			continue
		if line == '':
			continue
		alreadySplitSet.add(line.strip())


# search for matches with the CAPE bus name and the planning tf name
for Bus in ComedLVLoadSet:

	if Bus in alreadySplitSet: # no need to care, since load has already been split manually
		continue
	BusName = BusNameDict[Bus]

	try:
		last2Digits = int(BusName[-2:]) # convert to float to ensure that the last 2 digits are numeric
	except:
		continue

	# look at the corresponding (mapped) planning load bus and examine its transformer name (tfNameDict[0]), remember that the dict can have multiple entries
	# if there is a match, then we can go ahead and try to map the CAPE LV load bus's transformer 
	planningBus = loadMapDictCAPE[Bus]
	if len(tfNameDictCAPE[Bus]) > 1: # for now, ignore any CAPE buses which has mult tf, we will come back to them later
		continue
	CAPETFID = tfNameDictCAPE[Bus][0][1]

	if planningBus not in multTFLoad: # the planning load bus does not have multiple step up tf
		continue
	getNametoTFNameMatch(Bus,planningBus,BusName,last2Digits,CAPETFID)

	# look at all neighbours within depth 2 and try to find a name to tf name match
		# search within a depth 2 of bus, for buses which are not disconnected
		# if bus name ends with two digit integer, try to get a match with the tf of the same planning bus
	
	if Bus not in Depth2Dict.keys(): # Bus has no branches
		continue

	depth2neighbourList = Depth2Dict[Bus]

	for d2Bus in depth2neighbourList:
		if BusTypeDict[d2Bus] == '4':
			continue

		if d2Bus in alreadySplitSet:
			continue

		BusName = BusNameDict[d2Bus]
		
		try:
			last2Digits = int(BusName[-2:])
		except:
			continue

		if len(tfNameDictCAPE[d2Bus]) > 1: # for now, ignore any CAPE buses which has mult tf, we will come back to them later
			continue
		CAPETFID = tfNameDictCAPE[d2Bus][0][1]
		getNametoTFNameMatch(d2Bus,planningBus,BusName,last2Digits,CAPETFID)



# also look at the case where you are trying to match the transfomer numbers in both cases (may work when there are mult TF connected to one LV load bus in CAPE)
for Bus in ComedLVLoadSet:
	if Bus in foundSplitSet:
		continue

	CAPEBusName = BusNameDict[Bus]
	

	for tfData in tfNameDictCAPE[Bus]:
		tfName = tfData[0]
		if tfName == '':
			continue

		try:
			last2Digits = int(tfName[-2:]) # convert to float to ensure that the last 2 digits are numeric
		except:
			continue

		planningBus = loadMapDictCAPE[Bus]

		if planningBus not in multTFLoad: # the planning load bus does not have multiple step up tf
			continue
		CAPETFID = tfData[1]
		getCAPEToPSSETFNameMatch(Bus,planningBus,tfName,CAPEBusName,last2Digits,CAPETFID)


	# search depth 2 neighbours for the same thing
	
	if Bus not in Depth2Dict.keys(): # Bus has no branches
		continue

	# Bus has branches and its branches may be connected to step up tf which might be of interest
	depth2neighbourList = Depth2Dict[Bus]
	for d2Bus in depth2neighbourList:
		if BusTypeDict[d2Bus] == '4':
			continue
		if d2Bus in foundSplitSet or d2Bus in alreadySplitSet:
			continue

		CAPEBusName = BusNameDict[d2Bus]

		for tfData in tfNameDictCAPE[d2Bus]:
			tfName = tfData[0]
			if tfName == '':
				continue
		
			try:
				last2Digits = int(tfName[-2:])
			except:
				continue
			CAPETFID = tfData[1]
			#getNametoTFNameMatch(d2Bus,planningBus,BusName,last2Digits)
			getCAPEToPSSETFNameMatch(d2Bus,planningBus,tfName,CAPEBusName,last2Digits,CAPETFID)

	


if __name__ == "__main__":
	# list of tf maps
	with open(tfMapFile,'w') as f:
		f.write('List of tf mappings to be added to loadMap.py input:')
		f.write('\n')
		for line in mapLines:
			f.write(line)
			f.write('\n')

	# log list
	with open(tfMapLog,'w') as f:
		f.write('CAPEBus,BusName,planningBus,planning TF name, planning tf key:')
		f.write('\n')
		for line in logLinesNametoTF:
			f.write(line)
			f.write('\n')
		f.write('CAPEBus,BusName,CAPE TF Name,planningBus,planning TF name, planning tf key:')
		f.write('\n')
		for line in logLinesTFtoTF:
			f.write(line)
			f.write('\n')