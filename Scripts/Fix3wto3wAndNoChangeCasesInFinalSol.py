"""
	Sub all the tf in Final_sol_3w which are not 3w -> 2w (3w -> 3w and no sub)

"""

import shutil


latestTFFIle = 'TFIter2.txt' # file which contains subs in change3winderData and NewMidpointTFFix
#currentAllMapFile = 'AllMappedBusDataIter2.txt'
FinalSolFile = 'Final_sol_3w.txt' # TF substitutions which are special
#AllMapFileNew = 'AllMappedBusDataIter3.txt'
NewTFFile = 'TFIter3.txt' # New output
PSSErawFile = 'hls18v1dyn_new.raw'

NoChangeTFSet = set() # Set of CAPE tf which have no sub, include any phase shift
tfLinesIter3  =[] # output lines
#UATAngleDict = {} # key: CAPE Bus which may need angle shifting, value: angle shift
#UATBusSet = set() # All CAPE buses which need angles shifted
#newBusLines = [] # All buses in AllMapNew
#newBusAngleLines = [] # saves all the bus lines which got their angles shifted
ThreeWSubDict = {} # key: CAPE tf id, value: planning tf id
ImpPlanningTFSet = set() # planning tf which are relevant for this script
planningTFDict = {} # key: planning tf id, value: all the relevant impedance values
ImpCAPESet = set() # set of CAPE 3 winders which has 3 winder substitution in planning


def getPhaseShifts(i, fileLines):
	#get original tf phase shifts, to be added in to new 2 winders
	PSList = [] # ordered as primary, secondary and tertiary
	
	i+=2 #skip this line and the next line

	line = fileLines[i]
	words = line.split(',')
	PS = words[2].strip()
	PSList.append(PS)

	i+=1
	line = fileLines[i]
	words = line.split(',')
	PS = words[2].strip()
	PSList.append(PS)

	i+=1
	line = fileLines[i]
	words = line.split(',')
	PS = words[2].strip()
	PSList.append(PS)

	return PSList

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



# get relevant data (no change and 3w->3w cases) from this file
with open(FinalSolFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'txt' in line:
			continue
		if 'case' in line:
			continue
		words = line.split('->')
		CAPEPart = words[0].strip()
		planningPart = words[1].strip()

		if planningPart == '0': # tf which should be left as is, only phase shifts to be included
			NoChangeTFSet.add(CAPEPart)

		# Add if-else for 3w-3w cases
		planningWords = planningPart.split(',')
		if len(planningWords) > 3 and planningWords[2].strip() != '0': # 3w - 3w sub
			ThreeWSubDict[CAPEPart] = planningPart

			ImpCAPESet.add(CAPEPart)

			if planningPart not in ImpPlanningTFSet:
				ImpPlanningTFSet.add(planningPart)
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
		if key in ImpPlanningTFSet:
			CZ = words[5]
			i+=1
			line = fileLines[i]
			words = line.split(',')
			R12 = words[0]
			X12 = words[1]
			SBASE12 = words[2]
			R23 = words[3]
			X23 = words[4]
			SBASE23 = words[5]
			R31 = words[6]
			X31 = words[7]
			SBASE31 = words[8]
			if key not in planningTFDict.keys():
				planningTFDict[key] = [CZ,R12,X12,SBASE12,R23,X23,SBASE23,R31,X31,SBASE31]
			else:
				print 'Multiple CAPE 3 winder mapped to single PSSE 3 winder: ', key
				sameBusMultiTFset.add(key)
			i+=4 # continue to next TF
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
		tfLinesIter3.append(line)
		i = addMultLines(i,fileLines,tfLinesIter3,3)
		i+=1
		continue

	else: # three winder
		key = Bus1+','+Bus2+','+Bus3+','+cktID

		if key in NoChangeTFSet: # leave as is, get the phase shifts
			PSList = getPhaseShifts(i, fileLines)
			"""
			UATAngleDict[Bus2] = float(PSList[1])
			UATAngleDict[Bus3] = float(PSList[2])

			#get which phase shifts are actually being changed
			if float(PSList[1]) != 0.0:
				#print fileLines[i]
				UATBusSet.add(Bus2)

			elif float(PSList[2]) != 0.0:
				#print fileLines[i]
				UATBusSet.add(Bus3)
			"""

			# add tf lines and continue
			tfLinesIter3.append(line)
			i = addMultLines(i,fileLines,tfLinesIter3,4)
			i+=1
			continue

		# Add algorithm for 3w->3w substitution
		if key in ImpCAPESet:
			planningKey = ThreeWSubDict[key]
			data =planningTFDict[planningKey]

			# reconstruct 1st line and add
			CZ = data[0]
			R12 = data[1]
			X12 = data[2]
			SBASE12 = data[3]
			R23 = data[4]
			X23 = data[5]
			SBASE23 = data[6]
			R31 = data[7]
			X31 = data[8]
			SBASE31 = data[9]

			words[5]  = CZ
			line = reconstructLine2(words)
			tfLinesIter3.append(line)

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
			tfLinesIter3.append(line)

			# add remaining 3 lines
			i = addMultLines(i,fileLines,tfLinesIter3,3)
			# continue to next tf
			i+=1
			continue


		else: # three winder of no interest, add lines
			tfLinesIter3.append(line)
			i = addMultLines(i,fileLines,tfLinesIter3,4)
			i+=1
			continue



"""
# updates bus angles in the bus data
with open(currentAllMapFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		words = line.split(',')
		if len(words) <2:
			continue

		Bus = words[0].strip()
		
		#if Bus in FictBusSet: # dont include fictitious buses added by us
		#	continue
		
		if Bus in UATBusSet: # bus needs to have angle changed
			Angle = words[8].strip()
			newAngle = float(Angle) + UATAngleDict[Bus]
			words[8] = ' '*(9- len(str(newAngle))) + str(newAngle)
			nLine = reconstructLine2(words)
			newBusLines.append(nLine) # append the bus line which has angles changed
			newBusAngleLines.append(nLine) # used as a log of all the buses which have phase shifted
		else: # bus does not need to have angle changed
			newBusLines.append(line)
"""


# Outputs
# generate new tf lines
with open(NewTFFile,'w') as f:
	for line in tfLinesIter3:
		f.write(line)
		f.write('\n')

"""
# change bus angles
with open(AllMapFileNew,'w') as f:
	for line in newBusLines:
		f.write(line)
		f.write('\n')
"""

# make a copy in Donut Hole v2
# 
#destBusData = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/AllMappedBusData.txt'
#shutil.copyfile(AllMapFileNew,destBusData)

destTFData = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/TFIter3.txt'
shutil.copyfile(NewTFFile,destTFData)
