# looking at the latest tf file, applies all the 3 winder subs. The impedances, SBASE values and the tap ratios are all changed.
# Update from the first version, now we use the bus voltages in both planning and CAPE and sorted them in descending order. This 
# helps us keep the order of the NOMV and WINDV voltages consistent after substitution.
from getBusDataFn import getBusData


#ThreeWToThreeWSubFile = 'test3wTo3wSub.txt'
#ThreeWToThreeWSubFile = 'All3wTo3wSubData.txt'
#ThreeWToThreeWSubFile = 'All3wTo3wSubDataCleaned.txt'
ThreeWToThreeWSubFile = 'All3wTo3wSubDataCleaned_Mod.txt'
PSSErawFile = 'hls18v1dyn_new.raw'
latestTFFIle = 'newtfData.txt'
newtfLines = []
#NewTFFile = 'TF3wTo3wSub.txt'
NewTFFile = 'TF3wTo3wSubv2.txt'
changeLog = 'changeBusNoLog.txt'
CAPERaw = 'RAW0620.raw'

ThreeWSubDict = {}
ThreeWinderSubSetCAPE = set()
ThreeWinderSubSetPlanning = set()
planningTFDict = {}
changeNameDictOldToNew = {}
planningBusDataDict = getBusData(PSSErawFile)
CAPEBusDataDict = getBusData(CAPERaw)
class ThreeWinderData(object):
	def __init__(self):
		self.CW = ''
		self.CZ = ''
		self.R12 = ''
		self.X12 = ''
		self.SBASE12 = ''
		self.R23 = ''
		self.X23 = ''
		self.SBASE23 = ''
		self.R31 = ''
		self.X31 = ''
		self.SBASE31 = ''
		self.WINDV1 = ''
		self.NOMV1 = ''
		self.WINDV2 = ''
		self.NOMV2 = ''
		self.WINDV3 = ''
		self.NOMV3 = ''
		self.BUS1NOMV = 0.0
		self.BUS2NOMV = 0.0
		self.BUS3NOMV = 0.0



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


# get relevant data (no change and 3w->3w cases) from this file
with open(ThreeWToThreeWSubFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if '->' not in line:
			continue
		words = line.split('->')
		CAPEPart = words[0].strip()
		CAPEBus1 = CAPEPart.split(',')[0].strip()
		CAPEBus2 = CAPEPart.split(',')[1].strip()
		CAPEBus3 = CAPEPart.split(',')[2].strip()
		cktID  = CAPEPart.split(',')[3].strip()

		# change to new bus numbers
		if CAPEBus1 in changeNameDictOldToNew.keys():
			CAPEBus1 = changeNameDictOldToNew[CAPEBus1]

		if CAPEBus2 in changeNameDictOldToNew.keys():
			CAPEBus2 = changeNameDictOldToNew[CAPEBus2]

		if CAPEBus3 in changeNameDictOldToNew.keys():
			CAPEBus3 = changeNameDictOldToNew[CAPEBus3]

		CAPEPart =  CAPEBus1 + ',' + CAPEBus2 + ',' + CAPEBus3 + ',' + cktID
		#print CAPEPart
		planningPart = words[1].strip()

		# Add if-else for 3w-3w cases
		planningWords = planningPart.split(',')
		if len(planningWords) > 3 and planningWords[2].strip() != '0': # 3w - 3w sub
			ThreeWSubDict[CAPEPart] = planningPart

			ThreeWinderSubSetCAPE.add(CAPEPart)

			if planningPart not in ThreeWinderSubSetPlanning:
				ThreeWinderSubSetPlanning.add(planningPart)
			else:
				print 'Duplicate: ', planningPart
		else: # This line is not 3w -> 3w substitution data
			print 'Check line, not 3w->3w sub data: ' + line


# read planning raw file and get tf data to be substituted
with open(PSSErawFile,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split("\n")


# build a dictionary of comed transformer (relevant) data to be substituted into CAPE data
tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')



# generate a dictionary from the planning data, values are relevant tf info
i = tfStartIndex
while i < tfEndIndex:
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	Bus3 = words[2].strip()
	cktID = words[3].strip()
	key = Bus1+','+Bus2+','+Bus3+','+cktID
	if Bus3 == '0': # dont care about 2 winders
		i+=4
		continue


	else: # three winder
		if key in ThreeWinderSubSetPlanning:
			planningTFDict[key]  = ThreeWinderData()

			planningTFDict[key].CW = words[4]
			planningTFDict[key].CZ = words[5]
			i+=1
			line = fileLines[i]
			words = line.split(',')
			planningTFDict[key].R12 = words[0]
			planningTFDict[key].X12 = words[1]
			planningTFDict[key].SBASE12 = words[2]
			planningTFDict[key].R23 = words[3]
			planningTFDict[key].X23 = words[4]
			planningTFDict[key].SBASE23 = words[5]
			planningTFDict[key].R31 = words[6]
			planningTFDict[key].X31 = words[7]
			planningTFDict[key].SBASE31 = words[8]
			planningTFDict[key].BUS1NOMV = float(planningBusDataDict[Bus1].NominalVolt)
			planningTFDict[key].BUS2NOMV = float(planningBusDataDict[Bus2].NominalVolt)
			planningTFDict[key].BUS3NOMV = float(planningBusDataDict[Bus3].NominalVolt)



			i+=1
			line = fileLines[i]
			words = line.split(',')
			planningTFDict[key].WINDV1 = words[0]
			planningTFDict[key].NOMV1 = words[1]

			i+=1
			line = fileLines[i]
			words = line.split(',')
			planningTFDict[key].WINDV2 = words[0]
			planningTFDict[key].NOMV2 = words[1]

			i+=1
			line = fileLines[i]
			words = line.split(',')
			planningTFDict[key].WINDV3 = words[0]
			planningTFDict[key].NOMV3 = words[1]

			#planningTFDict[key] = [CW,CZ,R12,X12,SBASE12,R23,X23,SBASE23,R31,X31,SBASE31,WINDV1,NOMV1,WINDV2,NOMV2,WINDV3,NOMV3]

			i+=1 # continue to next TF
		else: # 3 winder of no interest
			i+=5



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
		newtfLines.append(line)
		i = addMultLines(i,fileLines,newtfLines,3)
		i+=1
		continue

	else: # three winder
		key = Bus1+','+Bus2+','+Bus3+','+cktID

		# Add algorithm for 3w->3w substitution
		if key in ThreeWinderSubSetCAPE:
			planningKey = ThreeWSubDict[key]
			planningVoltIndexDict = {}
			#data =planningTFDict[planningKey]

			# reconstruct 1st line and add
			CW = planningTFDict[planningKey].CW
			CZ = planningTFDict[planningKey].CZ
			R12 = planningTFDict[planningKey].R12
			X12 = planningTFDict[planningKey].X12
			SBASE12 = planningTFDict[planningKey].SBASE12
			R23 = planningTFDict[planningKey].R23
			X23 = planningTFDict[planningKey].X23
			SBASE23 = planningTFDict[planningKey].SBASE23
			R31 = planningTFDict[planningKey].R31
			X31 = planningTFDict[planningKey].X31
			SBASE31 = planningTFDict[planningKey].SBASE31

			# match the bus nominal voltages by sorting each side in descending order
			PlanningBus1NOMV = planningTFDict[planningKey].BUS1NOMV
			PlanningBus2NOMV = planningTFDict[planningKey].BUS2NOMV
			PlanningBus3NOMV = planningTFDict[planningKey].BUS3NOMV
			WINDV1 = planningTFDict[planningKey].WINDV1
			NOMV1 = planningTFDict[planningKey].NOMV1
			WINDV2 = planningTFDict[planningKey].WINDV2
			NOMV2 = planningTFDict[planningKey].NOMV2
			WINDV3 = planningTFDict[planningKey].WINDV3
			NOMV3 = planningTFDict[planningKey].NOMV3
			PlanningVoltSortedList = sorted([PlanningBus1NOMV,PlanningBus2NOMV,PlanningBus3NOMV],reverse = True)
			planningVoltIndexDict[PlanningBus1NOMV] = [WINDV1,NOMV1]
			planningVoltIndexDict[PlanningBus2NOMV] = [WINDV2,NOMV2]
			planningVoltIndexDict[PlanningBus3NOMV] = [WINDV3,NOMV3]

			CAPEBus1NOMV = float(CAPEBusDataDict[Bus1].NominalVolt)
			CAPEBus2NOMV = float(CAPEBusDataDict[Bus2].NominalVolt)
			CAPEBus3NOMV = float(CAPEBusDataDict[Bus3].NominalVolt)
			CAPEVoltSortedList = sorted([CAPEBus1NOMV,CAPEBus2NOMV,CAPEBus3NOMV],reverse = True)

			# Now both lists are sorted in same order (descending). So, the corresponding indices are the corresponding windings in CAPE and planning
			# Using this idea, get the index of CAPE Buses from the sorted CAPE list
			VoltIndexCAPEBus1 = CAPEVoltSortedList.index(CAPEBus1NOMV)
			VoltIndexCAPEBus2 = CAPEVoltSortedList.index(CAPEBus2NOMV)
			VoltIndexCAPEBus3 = CAPEVoltSortedList.index(CAPEBus3NOMV)

			# Using these indices, get the corresponding planning nom volt, and then using planningVoltIndexDict, get the corresponding WINDV1 and NOMV1
			CAPEWINDV1 = planningVoltIndexDict[PlanningVoltSortedList[VoltIndexCAPEBus1]][0]
			CAPEWINDV2 = planningVoltIndexDict[PlanningVoltSortedList[VoltIndexCAPEBus2]][0]
			CAPEWINDV3 = planningVoltIndexDict[PlanningVoltSortedList[VoltIndexCAPEBus3]][0]

			CAPENOMV1 = planningVoltIndexDict[PlanningVoltSortedList[VoltIndexCAPEBus1]][1]
			CAPENOMV2 = planningVoltIndexDict[PlanningVoltSortedList[VoltIndexCAPEBus2]][1]
			CAPENOMV3 = planningVoltIndexDict[PlanningVoltSortedList[VoltIndexCAPEBus3]][1]





			words[4] = CW
			words[5]  = CZ
			line = reconstructLine2(words)
			newtfLines.append(line)

			# reconstruct 2nd line and add
			i +=1
			line = fileLines[i]
			words = line.split(',')
			words[0] = R12
			words[1] = X12
			words[2] = SBASE12
			words[3] = R23
			words[4] = X23
			words[5] = SBASE23
			words[6] = R31
			words[7] = X31
			words[8] = SBASE31
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
			# reconstruct 5th line
			i +=1
			line = fileLines[i]
			words = line.split(',')
			words[0] = CAPEWINDV3
			words[1] = CAPENOMV3
			line = reconstructLine2(words)
			newtfLines.append(line)

			# continue to next tf
			i+=1
			continue


		else: # three winder of no interest, add lines
			newtfLines.append(line)
			i = addMultLines(i,fileLines,newtfLines,4)
			i+=1
			continue


# generate new tf lines
with open(NewTFFile,'w') as f:
	for line in newtfLines:
		f.write(line)
		f.write('\n')