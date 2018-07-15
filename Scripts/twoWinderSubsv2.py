# looking at the latest tf file, applies all the normal 2 winder subs. The impedances, SBASE values and the tap ratios are all changed.
# Update from the first version, now we use the bus voltages in both planning and CAPE and sorted them in descending order. This 
# helps us keep the order of the NOMV and WINDV voltages consistent after substitution.
from getBusDataFn import getBusData



#ThreeWToThreeWSubFile = 'All3wTo3wSubDataCleaned_Mod.txt'
PSSErawFile = 'hls18v1dyn_1219.raw'
latestTFFIle = 'TFSubManualDone.txt'
newtfLines = []
NewTFFile = 'TFTwoWinderSubDone.txt'
#NewTFFile = 'TF3wTo3wSub.txt'
#NewTFFile = 'TF3wTo3wSubv2.txt'
changeLog = 'changeBusNoLog.txt'
CAPERaw = 'RAW0620.raw'

TwoWSubDict = {}
TwoWinderSubSetCAPE = set()
TwoWinderSubSetPlanning = set()
planningTFDict = {}
changeNameDictOldToNew = {}
planningBusDataDict = getBusData(PSSErawFile)
CAPEBusDataDict = getBusData(CAPERaw)
tfSubLines = []

# get the lines to sub
TwoWinderSubFile = 'tf2tfmaps_2winder_cleaned.txt'
"""
with open(input_file,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

# get the relevant inputs
startIndex = fileLines.index('Normal two winder substitutions from mapping_confirmed_0606:') + 1
for i in range(startIndex,len(fileLines)):
	line = fileLines[i]
	tfSubLines.append(line)
"""

class TwoWinderData(object):
	def __init__(self):
		self.CW = ''
		self.CZ = ''
		self.R = ''
		self.X = ''
		self.SBASE = ''
		self.WINDV1 = ''
		self.NOMV1 = ''
		self.WINDV2 = ''
		self.NOMV2 = ''
		self.BUS1NOMV = 0.0
		self.BUS2NOMV = 0.0



def reconstructLine2(words):
	currentLine = ''
	for word in words:
		currentLine += word
		currentLine += ','
	return currentLine[:-1]

def addMultLines(i,fileLines,newtfLines,numLines):
	# for adding transformer lines which do not change
	for j in range(numLines):
		i+=1
		line = fileLines[i]
		newtfLines.append(line)	
	return i


"""
# not needed, since all the bus numbers in the inputs are renumbered to new numbers
# look at log files which contains all the changed bus numbers in the previous iteration (first time i did this)
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
		changeNameDictOldToNew[OldBus] = NewBus
"""
# get relevant data (no change and 3w->3w cases) from this file
with open(TwoWinderSubFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	#for line in fileLines:
	startIndex = fileLines.index('Normal two winder substitutions from mapping_confirmed_0606:') + 1
	for i in range(startIndex,len(fileLines)):
		line = fileLines[i]
		if line == '':
			continue
		words = line.split('->')

		planningPart = words[0].strip()
		planningWords = planningPart.split(',')
		planningBus1 = planningWords[0].strip()
		planningBus2 = planningWords[1].strip()
		planningcktID = planningWords[2].strip()
		# put quotes properly around planning ckt id
		if len(planningcktID)  == 1:
			planningcktID = "'" +  planningcktID  + " '"
		else:
			planningcktID = "'" +  planningcktID  + "'"
		#######
		planningPart =  planningBus1.rjust(6) + ',' + planningBus2.rjust(6) + ',' + '     0' + ',' + planningcktID
		#print planningPart
		CAPEPart = words[1].strip()
		CAPEBus1 = CAPEPart.split(',')[0].strip()
		CAPEBus2 = CAPEPart.split(',')[1].strip()
		#CAPEBus3 = CAPEPart.split(',')[2].strip()
		cktID  = CAPEPart.split(',')[2].strip()
		
		# no need to change bus numbers, already renumbered
		"""
		# change to new bus numbers
		if CAPEBus1 in changeNameDictOldToNew.keys():
			CAPEBus1 = changeNameDictOldToNew[CAPEBus1]

		if CAPEBus2 in changeNameDictOldToNew.keys():
			CAPEBus2 = changeNameDictOldToNew[CAPEBus2]

		if CAPEBus3 in changeNameDictOldToNew.keys():
			CAPEBus3 = changeNameDictOldToNew[CAPEBus3]
		"""

		CAPEPart =  CAPEBus1.rjust(6) + ',' + CAPEBus2.rjust(6) + ',' + '     0' + ',' + "'" +  cktID  + " '"
		# some of the CAPE side inputs are flipped in order, need to fix these
		CAPEPartReverse = CAPEBus2.rjust(6) + ',' + CAPEBus1.rjust(6) + ',' + '     0' + ',' + "'" +  cktID  + " '"
		#print CAPEPart
		TwoWinderSubSetCAPE.add(CAPEPart)
		TwoWinderSubSetCAPE.add(CAPEPartReverse)

	
		TwoWSubDict[CAPEPart] = planningPart
		TwoWSubDict[CAPEPartReverse] = planningPart

		if planningPart not in TwoWinderSubSetPlanning:
			TwoWinderSubSetPlanning.add(planningPart)
		else:
			print 'Duplicate: ', planningPart

			


# read planning raw file and get tf data to be substituted
with open(PSSErawFile,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split("\n")


# build a dictionary of comed transformer (relevant) data to be substituted into CAPE data
tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')



# generate a dictionary from the planning data, values are relevant tf info
#foundPlanningTFSet = set() # set to keep track of which planning tf has been found, and which has not been found
i = tfStartIndex
while i < tfEndIndex:
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	Bus3 = words[2].strip()
	cktID = words[3]
	key = Bus1.rjust(6)+','+Bus2.rjust(6)+','+Bus3.rjust(6)+','+cktID
	if Bus3 == '0': # 2 winders
		if key in TwoWinderSubSetPlanning:
			#foundPlanningTFSet.add(key)
			#print key
			planningTFDict[key]  = TwoWinderData()
			# Line 1
			planningTFDict[key].CW = words[4]
			planningTFDict[key].CZ = words[5]
			planningTFDict[key].BUS1NOMV = float(planningBusDataDict[Bus1].NominalVolt)
			planningTFDict[key].BUS2NOMV = float(planningBusDataDict[Bus2].NominalVolt)
			#Line 2
			i+=1
			line = fileLines[i]
			words = line.split(',')
			planningTFDict[key].R = words[0]
			planningTFDict[key].X = words[1]
			planningTFDict[key].SBASE = words[2]

			# Line 3
			i+=1
			line = fileLines[i]
			words = line.split(',')
			planningTFDict[key].WINDV1 = words[0]
			planningTFDict[key].NOMV1 = words[1]
			# Line 4
			i+=1
			line = fileLines[i]
			words = line.split(',')
			planningTFDict[key].WINDV2 = words[0]
			planningTFDict[key].NOMV2 = words[1]



			#planningTFDict[key] = [CW,CZ,R,X,SBASE,R23,X23,SBASE23,R31,X31,SBASE31,WINDV1,NOMV1,WINDV2,NOMV2,WINDV3,NOMV3]

			i+=1 # continue to next TF
		else: # 2 winder of no interest
			i+=4


	else: # three winder,dont care
		i+=5
		continue

"""
# figure out which planning tf still need to be found
for tf in list(TwoWinderSubSetPlanning):
	if tf not in foundPlanningTFSet:
		print tf
"""
#foundCAPETFSet = set()
# read current TFFile and reconstruct the 3 winders which can be mapped into 2 winder set using AdvancedMidpointCases.txt
with open(latestTFFIle,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')


# generate new tf lines 
i = 0
while i < len(fileLines):
	line = fileLines[i]
	if line == '':
		i+=1
		continue
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	Bus3 = words[2].strip()
	cktID = words[3].strip()
	if Bus3 == '0': # two winder, add lines and continue
		key = Bus1.rjust(6)+','+Bus2.rjust(6)+','+Bus3.rjust(6)+','+cktID

		# Add algorithm for 3w->3w substitution
		if key in TwoWinderSubSetCAPE:
			#foundCAPETFSet.add(key)
			#print key
			planningKey = TwoWSubDict[key]
			planningVoltIndexDict = {}
			#data =planningTFDict[planningKey]

			# reconstruct 1st line and add
			CW = planningTFDict[planningKey].CW
			CZ = planningTFDict[planningKey].CZ
			R = planningTFDict[planningKey].R
			X = planningTFDict[planningKey].X
			SBASE = planningTFDict[planningKey].SBASE


			# match the bus nominal voltages by sorting each side in descending order
			PlanningBus1NOMV = planningTFDict[planningKey].BUS1NOMV
			PlanningBus2NOMV = planningTFDict[planningKey].BUS2NOMV
			WINDV1 = planningTFDict[planningKey].WINDV1
			NOMV1 = planningTFDict[planningKey].NOMV1
			WINDV2 = planningTFDict[planningKey].WINDV2
			NOMV2 = planningTFDict[planningKey].NOMV2
			PlanningVoltSortedList = sorted([PlanningBus1NOMV,PlanningBus2NOMV],reverse = True)
			planningVoltIndexDict[PlanningBus1NOMV] = [WINDV1,NOMV1]
			planningVoltIndexDict[PlanningBus2NOMV] = [WINDV2,NOMV2]


			CAPEBus1NOMV = float(CAPEBusDataDict[Bus1].NominalVolt)
			CAPEBus2NOMV = float(CAPEBusDataDict[Bus2].NominalVolt)
			CAPEVoltSortedList = sorted([CAPEBus1NOMV,CAPEBus2NOMV],reverse = True)

			# Now both lists are sorted in same order (descending). So, the corresponding indices are the corresponding windings in CAPE and planning
			# Using this idea, get the index of CAPE Buses from the sorted CAPE list
			VoltIndexCAPEBus1 = CAPEVoltSortedList.index(CAPEBus1NOMV)
			VoltIndexCAPEBus2 = CAPEVoltSortedList.index(CAPEBus2NOMV)

			# Using these indices, get the corresponding planning nom volt, and then using planningVoltIndexDict, get the corresponding WINDV1 and NOMV1
			CAPEWINDV1 = planningVoltIndexDict[PlanningVoltSortedList[VoltIndexCAPEBus1]][0]
			CAPEWINDV2 = planningVoltIndexDict[PlanningVoltSortedList[VoltIndexCAPEBus2]][0]

			CAPENOMV1 = planningVoltIndexDict[PlanningVoltSortedList[VoltIndexCAPEBus1]][1]
			CAPENOMV2 = planningVoltIndexDict[PlanningVoltSortedList[VoltIndexCAPEBus2]][1]



			words[4] = CW
			words[5]  = CZ
			line = reconstructLine2(words)
			newtfLines.append(line)

			# reconstruct 2nd line and add
			i +=1
			line = fileLines[i]
			words = line.split(',')
			words[0] = R
			words[1] = X
			words[2] = SBASE
			line = reconstructLine2(words)
			newtfLines.append(line)

			# reconstruct 3rd line
			i +=1
			line = fileLines[i]
			words = line.split(',')
			words[0] = CAPEWINDV1
			words[1] = CAPENOMV1
			line = reconstructLine2(words)
			newtfLines.append(line)
			# reconstruct 4th line
			i +=1
			line = fileLines[i]
			words = line.split(',')
			words[0] = CAPEWINDV2
			words[1] = CAPENOMV2
			line = reconstructLine2(words)
			newtfLines.append(line)


			# continue to next tf
			i+=1
			continue


		else: # two winder of no interest, add lines
			newtfLines.append(line)
			i = addMultLines(i,fileLines,newtfLines,3)
			i+=1
			continue

	else: # three winder, just add
		newtfLines.append(line)
		i = addMultLines(i,fileLines,newtfLines,4)
		i+=1
		continue

"""
# figure out which planning tf still need to be found
for tf in list(TwoWinderSubSetCAPE):
	if tf not in foundCAPETFSet:
		print tf
"""
# generate new tf lines
with open(NewTFFile,'w') as f:
	for line in newtfLines:
		f.write(line)
		f.write('\n')