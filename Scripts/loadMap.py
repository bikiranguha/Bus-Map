# script will be different for CAPE load buses which have one tf conn or multiple conn
# handle the load mapping by getting planning tf conn and corresponding CAPE tf conn
# handle the tf mapping in the same way
# handle the bus mapping
import shutil

mapFile = 'autoTFMap0505.txt'
CAPERaw = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/Island 34 system' + '/' + 'Raw0414tmp_loadsplit.raw'
#newRaw = 'RAW0501.raw'
newRaw = 'RAW0501_v2.raw'
#mapFile = 'testMaptmp.txt'
from checkLoadSplit import BusVoltDict as planningBusVoltDict
from loadSplitCAPE import BusVoltDict as CAPEBusVoltDict, BusZoneDict as CAPEBusZoneDict
from generateLVtfData import NumLVTFDictCAPE, TFPSDict
from analyzeLoadFlowReport import flowDict # class which 
from generateLVTFDataDict import LVTFDataDict # dict of planning LV TF data dict
from LVplanningBusData import planningBusDataDict
from getPhaseShifts import AngleChangeDict
from tryAutomateLoadSplit import loadMapDict # dictionary containing info about loadBusNoChangeLog

NewLoadData = {} # key: CAPE Bus, value:  new load data, generated from planning LAMP report
LoadDataToSkip = set() # set of CAPE buses where the load data needs to be changed
NewTFData = {} # dict whose keys are the CAPE bus keys, values are the tf data, with the phase shifts included
NewBusData = {} # key: CAPE bus no, value: [NominalVolt, Voltpu, AngleStr] to be substituted into CAPE bus data
TFDataToSkip = set()
newRawLines = []
loadAdded = set() # keeps track of which load data has been modified, so that we can add load data for buses which previously had no loads
sampleLoadLine = "  4355,'1 ',1, 222,  20,     1.400,     0.600,     0.000,     0.000,     0.000,     0.000, 222,1,0"
LoadBusToSkip = ['4667','3037','4107','4783'] # missing transformers for this CAPE load bus, so do not split the load
# Functions:

def reconstructLine2(words):
	currentLine = ''
	for word in words:
		currentLine += word
		currentLine += ','
	return currentLine[:-1]

def changeBusData(planningBus, CAPEBus):
	# populate the newbusdata dict with relevant values from the planning bus data
	planningBusData = planningBusDataDict[planningBus]
	words = planningBusData.split(',')
	#words[0] = ' '*(6-len(CAPEBus)) + CAPEBus # change bus name
	NominalVolt = words[2]
	Voltpu = words[7]
	Angle = float(words[8].strip())
	if CAPEBus in AngleChangeDict.keys():
		#print CAPEBus
		change = AngleChangeDict[CAPEBus]
		Angle += change

	AngleStr = '%.4f' % Angle
	AngleStr = ' '*(9-len(AngleStr)) + AngleStr

	if CAPEBus in NewBusData.keys(): #already mapped in this script, check for inconsistencies
		OldNominalVolt = NewBusData[CAPEBus][0]
		OldVoltpu = NewBusData[CAPEBus][1]
		OldAngleStr = NewBusData[CAPEBus][2]
		if OldNominalVolt != NominalVolt:
			print 'Bus ' + CAPEBus + ' has different nominal voltages'
		if OldVoltpu != Voltpu:
			print 'Bus ' + CAPEBus + ' has different pu voltages'
		if OldAngleStr != AngleStr:
			print 'Bus ' + CAPEBus + ' has different pu voltages'

	else: # first time mapping in this script
		NewBusData[CAPEBus] = [NominalVolt, Voltpu, AngleStr]




def generateNewLoadDict(planningBus1,planningBus2,CAPEBus2,NewLoadData):
	# handle all load mappings

	# handle load mapping for cases where the CAPE LV bus only has one step up tf
	if NumLVTFDictCAPE[CAPEBus2] == 1:
		#print CAPEBus2
		flowData = flowDict[planningBus2]
		if flowData.toBus.count(planningBus1) == 1: # the LV bus has only one step up tf connection to the HV bus
			busIndex = flowData.toBus.index(planningBus1)
			LoadMW =  flowData.MWList[busIndex]
			LoadMVAR =  flowData.MVARList[busIndex]

			NewLoadData[CAPEBus2] = [LoadMW, LoadMVAR]
		elif flowData.toBus.count(planningBus1) > 1: # the LV bus has multiple step up tf connection to the same HV bus, need to check ckt id to determine correct connection
			#print planningBus1
			busIndices = [i for i, b in enumerate(flowData.toBus) if b == planningBus1 ] # list of indices where planningBus1 appears

			for index in busIndices: # scan busIndices for the planningcktID
				if planningcktID == flowData.cktID[index]: # found, get load data
					LoadMW = flowData.MWList[index]
					LoadMVAR =  flowData.MVARList[index]

			NewLoadData[CAPEBus2] = [LoadMW, LoadMVAR] # the cumulate load is applied for the load data
		else: # planningBus1 has no occurence in the load flow data (should not be print anything)
			print 'Why no occurence for bus ' + planningBus1 + ' for load bus ' + planningBus2


	else: # CAPE LV bus has more than one step up tf, add loads for CAPEBus2 (the LV load bus in CAPE)
		#print CAPEBus2
		#pass
		flowData = flowDict[planningBus2]
		if flowData.toBus.count(planningBus1) == 1: # the LV bus has only one step up tf connection to the HV bus
			busIndex = flowData.toBus.index(planningBus1)
			LoadMW =  flowData.MWList[busIndex]
			LoadMVAR =  flowData.MVARList[busIndex]
			if CAPEBus2 not in NewLoadData.keys():
				NewLoadData[CAPEBus2] = [LoadMW, LoadMVAR]
			else: # CAPEBus2 already appeared before, so add the flows in this transformer to its load
				NewLoadData[CAPEBus2][0] += LoadMW
				NewLoadData[CAPEBus2][1] += LoadMVAR
			
		elif flowData.toBus.count(planningBus1) > 1: # the LV bus has multiple step up tf connection to the same HV bus, need to check ckt id to determine correct connection
			#print planningBus1
			busIndices = [i for i, b in enumerate(flowData.toBus) if b == planningBus1 ] # list of indices where planningBus1 appears

			for index in busIndices: # scan busIndices for the planningcktID
				if planningcktID == flowData.cktID[index]: # found, get load data
					LoadMW = flowData.MWList[index]
					LoadMVAR =  flowData.MVARList[index]

			if CAPEBus2 not in NewLoadData.keys():
				NewLoadData[CAPEBus2] = [LoadMW, LoadMVAR]
			else: # CAPEBus2 already appeared before, so add the flows in this transformer to its load
				NewLoadData[CAPEBus2][0] += LoadMW
				NewLoadData[CAPEBus2][1] += LoadMVAR


def generateNewTFData(planningKey,CAPEKey,CAPEData,primaryHVplanning,CAPEHVplanning,NewTFData):
	# generates the new transformer data with bus numbers changed
	# populates NewTFData dictionary with tf data and the key is the CAPE tf id
	newTFList = []

	oldTFList = LVTFDataDict[planningKey]

	# 1st line
	line1 = oldTFList[0]
	words = line1.split(',')

	if primaryHVplanning == CAPEHVplanning:
		words[0] = ' '*(6-len(CAPEData[0])) + CAPEData[0]
		words[1] = ' '*(6-len(CAPEData[1])) + CAPEData[1]
	else: # need to switch bus numbering
		words[0] = ' '*(6-len(CAPEData[1])) + CAPEData[1]
		words[1] = ' '*(6-len(CAPEData[0])) + CAPEData[0]

	ckt = "'" +   CAPEData[2] + " '" # CAPE tf ckt id
	words[3] = ckt


	line = reconstructLine2(words)
	newTFList.append(line)

	# 2nd line, just add
	newTFList.append(oldTFList[1])


	# 3rd line, import phase shift info
	line3 = oldTFList[2]
	words = line3.split(',')
	PS = TFPSDict[CAPEKey] # float

	if PS == 0.0:
		PSstr = '%0.5f' %PS # convert to string
		words[2] = ' '*(8-len(PSstr)) + PSstr
		line = reconstructLine2(words)

	else:
		if primaryHVplanning != CAPEHVplanning: # change sign, since bus order is different
			PS = -PS
		
		PSstr = '%0.5f' %PS
		words[2] = ' '*(8-len(PSstr)) + PSstr
		line = reconstructLine2(words)

	newTFList.append(line)


	# 4th line, just add
	newTFList.append(oldTFList[3])

	NewTFData[CAPEKey] = newTFList




##################################

with open(mapFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		if '->' not in line: # skip header
			continue
		words = line.split('->')
		planningData = words[0].split(',')
		CAPEData  = words[1].split(',')

		planningKey = words[0].strip() # key for LVTFDataDict
		CAPEKey = words[1].strip()

		primaryHVplanning = 1 # 1 means Bus1 is HV, 0 means Bus2 is HV
		# arrange the planning buses according to voltage level (HV always primary)
		if planningBusVoltDict[planningData[0].strip()] > 40.0:
			planningBus1 = planningData[0].strip()
			planningBus2 = planningData[1].strip()
		else:
			planningBus1 = planningData[1].strip()
			planningBus2 = planningData[0].strip()
			primaryHVplanning = 0

		# get ckt id if any
		if len(planningData) > 2:
			planningcktID  = planningData[2].strip("'")
			

		# arrange the CAPE buses according to voltage level (HV always primary)
		CAPEHVplanning = 1 # 1 means Bus1 is HV, 0 means Bus2 is HV
		if CAPEBusVoltDict[CAPEData[0].strip()] > 40.0:
			CAPEBus1 = CAPEData[0].strip()
			CAPEBus2 = CAPEData[1].strip()
		else:
			CAPEBus1 = CAPEData[1].strip()
			CAPEBus2 = CAPEData[0].strip()	
			CAPEHVplanning = 0

		if CAPEBus2 in LoadBusToSkip: # these load buses have already been taken care of in Raw_loadsplit.raw, so move on to next line
			continue

		# get ckt id if any
		if len(CAPEData) > 2:
			CAPEcktID  = CAPEData[2].strip("'")	

		generateNewLoadDict(planningBus1,planningBus2,CAPEBus2,NewLoadData)


		if CAPEBus2 != loadMapDict[planningBus2]: # CAPE load bus was wrongly mapped, print warning and add the previously mapped bus to a set of load lines which will be skipped
			#print 'Load map of ' + planningBus2 + ' should be ' + CAPEBus2 + ', not ' +  loadMapDict[planningBus2]
			LoadDataToSkip.add(loadMapDict[planningBus2]) # add the previous CAPE load map to the skip set, this bus will be skipped if encountered in load data

		#LoadDataToSkip.add(CAPEBus2) # skip when adding load lines in new raw file

		generateNewTFData(planningKey,CAPEKey,CAPEData,primaryHVplanning,CAPEHVplanning,NewTFData)
		TFDataToSkip.add(CAPEKey) # skip when adding tf lines in new raw file

		# extract the relevant info from planning bus data into NewBusData dict, these info will be substituted in the new raw file bus data
		changeBusData(planningBus1, CAPEBus1)
		changeBusData(planningBus2, CAPEBus2)

# search for buses which were originally mapped for loads, but then 
# it was determined that the mapping was wrong and the load was shifted
for Bus in list(LoadDataToSkip):
	if Bus not in NewLoadData.keys():
		print'Load removed from Bus ' + Bus + ' due to wrong mapping earlier.'
 
# generate new raw file with the new bus data, new load data and new tf data
with open(CAPERaw,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if ('PSS' in line) or ('COMED' in line) or ('DYNAMICS' in line):
		    continue
		if 'END OF BUS DATA' in line:
		    break
		words = line.split(',')
		if len(words)<2: # continue to next iteration of loop if its a blank line
		    continue

		Bus = words[0].strip()
		# change bus nominal volt, pu volt and angle if the it appears in the keys of NewBusData
		if Bus in NewBusData.keys():
			ImpData = NewBusData[Bus] 

			NominalVolt = ImpData[0]
			Voltpu = ImpData[1]
			AngleStr = ImpData[2]

			words[2] = NominalVolt
			words[7] = Voltpu
			words[8] = AngleStr
			line = reconstructLine2(words)
			
		newRawLines.append(line)

# add these two bus lines, for some reason they were missing
newRawLines.append("243083,'05CAMPSS    ', 138.0000,1, 205,1251,   1,1.01145, -55.0773")
newRawLines.append("658082,'MPSSE  7    ', 115.0000,1, 652,1624, 658,1.02055, -45.2697")

newRawLines.append("0 / END OF BUS DATA, BEGIN LOAD DATA")

# change load data
loadStartIndex = fileLines.index('0 / END OF BUS DATA, BEGIN LOAD DATA') + 1
loadEndIndex = fileLines.index('0 / END OF LOAD DATA, BEGIN FIXED SHUNT DATA')
tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')
for i in range(loadStartIndex,loadEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus  = words[0].strip()

	# change load MW and load MVAR if the load bus appears in the keys of NewLoadData
	if Bus in NewLoadData.keys() and Bus not in loadAdded:
		loadAdded.add(Bus)
		LoadMW = '%.3f' %NewLoadData[Bus][0]
		LoadMVAR = '%.3f' %NewLoadData[Bus][1]
		words[5] = ' '*(10-len(LoadMW)) + LoadMW
		words[6] = ' '*(10-len(LoadMVAR)) + LoadMVAR
		line = reconstructLine2(words)
	elif Bus in LoadDataToSkip: # Load wrongly put at this bus, skip
		continue

	newRawLines.append(line)

for Bus in NewLoadData.keys():
	if Bus not in loadAdded: # the load at this bus needs to be added
		sampleWords = sampleLoadLine.split(',')
		sampleWords[0] = ' '*(6-len(Bus)) + Bus
		Zone = CAPEBusZoneDict[Bus]
		LoadMW = '%.3f' %NewLoadData[Bus][0]
		LoadMVAR = '%.3f' %NewLoadData[Bus][1]
		sampleWords[4] = ' '*(4-len(Zone)) + Zone
		sampleWords[5] = ' '*(10-len(LoadMW)) + LoadMW
		sampleWords[6] = ' '*(10-len(LoadMVAR)) + LoadMVAR
		line = reconstructLine2(sampleWords)

		newRawLines.append(line)

# append all data between load end and tf beginning
for i in range(loadEndIndex,tfStartIndex):
	line = fileLines[i]
	newRawLines.append(line)


# change tf data


i = tfStartIndex
while i < tfEndIndex:
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	Bus3 = words[2].strip()
	cktID = words[3].strip("'").strip()
	key = Bus1+','+Bus2+','+cktID

	if key in NewTFData.keys():
		newTFList = NewTFData[key] # list containing tf data
		for ele in newTFList:
			newRawLines.append(ele)
		i+=4 # continue to next tf
	
	else: # tf need not be changed, add lines
		line = fileLines[i]
		newRawLines.append(line)
		for j in range(3):
			i+=1
			line = fileLines[i]
			newRawLines.append(line)

		i+=1 # continue to next tf

# append all data from the end of tf data
for i in range(tfEndIndex,len(fileLines)):
	line = fileLines[i]
	newRawLines.append(line)


# generate new raw file
with open(newRaw,'w') as f:
	f.write('0,   100.00, 33, 1, 1, 60.00     / PSS(R)E-33.3    TUE, DEC 13 2016  22:08')
	f.write('\n')
	f.write('COMED 2018,  HLS18V1, N18S OUTSIDE AND 18 INTCHNG')
	f.write('\n')
	f.write('DYNAMICS REVSION 01')
	f.write('\n')
	for line in newRawLines:
		f.write(line)
		f.write('\n')



# copy to the given location
destTFData = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders\Automate 345 kV mapping/'
shutil.copy(newRaw,destTFData)