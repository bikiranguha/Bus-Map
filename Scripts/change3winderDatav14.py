"""
 Change three winder tf data in CAPE to match that of planning
 Functionalities:
 	If there is a generator bus present, find the equivalent 3 winder tf in planning and import impedance data
 		If there is equivalence for the 3 winder generator tf, print it out as an error
 	If no gen bus in tf:
 		If there are multiple windings mapped to the same bus in planning, print and continue to next tf
 		Try to find a 3 winder match using mapping data
 		If no 3 winder match, then try to find using midpoint data. If midpoint data found, then map while keeping bus data and phase info consistent

"""




from getMidpointDatav2 import ComedMidpointSet, MidpointDict, MidpointNeighbour, MidpointTFdata, ComedMidpointBusData
from generatetfNeighboursPlanning import tfNeighbourDict

changeLog = 'changeBusNoLog.txt' # to get the change in bus no. log
MapLog = 'AllMappedLog.txt' 
verifiedMapFile = 'PSSEGenMapVerified.txt' # mapping for gen bus
PSSErawFile = 'hls18v1dyn_new.raw'
CAPERaw = 'NewCAPERawClean.raw'
newTFFile = 'TFIter1.txt'
tf3winderchangeLog = 'tf3winderchangeLog.txt'
AllMapFileOld = 'AllMappedBusDataOld.txt' # All mapped bus data, without midpoint buses and non-shifted bus angles
AllMapFile = 'AllMappedBusDataIter1.txt' # All mapped bus data, to add three winder midpoint buses
tfIssueFile = 'noConnection3w.txt' # contains all the cases where there is no connection between the windings in planning
#newBusAngles = 'newBusAngles.txt' # file containing changed bus angle list
threetoTwoWinderDuplIssue = 'threetoTwoWinderDuplIssue.txt'
notfCases =  'notfCases.txt' # lists all the cases where a CAPE 3 winder has no tf in planning, left as is, only considering phase shifts
threetoTwoWinderAuto = 'threetoTwoWinderAuto.txt' # contains all the cases where a CAPE 3 winder can be mapped to a planning 2 winder, needs to be re-evaluated by changeThreeToTwoWinderTFMapping.py
#delete4winderDataFile = 'deleteOld4winderdata.txt' # file containing old 4 winder info
#delete4winderNoAlignMent = 'deleteOld4winderdataNoAlignment.txt' # same as delete4winderDataFile, without any spacing between commas
#new4winderDataFile = 'new4winderdata.txt' # generated from planning data for the 4 winders
deleteFictBusFile = 'deleteFictBusList.txt' # list of fict buses added by us and which need to be deleted
FinalSolFile = 'Final_sol_3w.txt' # TF substitutions which are special
stillToSolveCases = 'stillToSolveCases.txt' # Cases which are very special, requires iteration phase 2 of investigation


# files to be used by changeBusAngleTree
directory = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/'
newBusAngles = directory +  'newBusAngles.txt' # file containing changed bus angle list
angleChangeFile = directory +  'logAngleChange.txt'


oldNoDict = {} # keys: Old (original) CAPE bus numbers, values: new CAPE bus numbers
newNoDict = {} # keys: new CAPE bus numbers, values: Old (original) CAPE bus numbers
MapDict = {} # keys: Original CAPE bus numbers, values: corresponding planning numbers
ComedBusSet = set() 
planningTFDict = {} # used to superimpose planning tf impedance data on CAPE tf
TrueGenBusSet = set()
sameBusMultiTFset = set() # Used to check if multiple 3 winders exist for the same three buses in planning
newtfLines = []
toChange3winder = {} # dictionary which will contain the 3 winder changelog
newMidPointLines = []
tfIssueLines = []
planningVoltageDict = {} # key: planning bus, value: Bus voltage
CAPEVoltageDict = {} # key: CAPE bus, value: Bus voltage
UATBusSet = set() # Set of buses which belong primary and secondary of three winding UATs
UATAngleDict = {}
newBusAngleLines = [] # lines of buses where angles have been changed
threetoTwoWinderReplaceLines = [] # list of CAPE 3w tf which are PSSE 2w tf
threetoTwoWinderDuplicateIssue  = [] # cases where multiple CAPE 3w tf are being mapped to a single PSSE 2w tf
threetoTwoWinderFoundSet = set() # used to find duplicates of CAPE 3w tf being mapped to a single PSSE 2w tf
notfCaseLines = [] # lists all the cases where a CAPE 3 winder has no tf in planning, left as is, only considering phase shifts
newBusLines = [] # all the new bus info will be here, including new tf midpoints, and buses with angles shifted
FourWinderList = [] # list which keeps track of the tf data which were derived from four winder tf data
FourWinderListNoAlign = [] # same as FourWinderList, except no alignment
angleChangeLines = []
#FictBusSet = set() # set of fict buses added by us and which need to be deleted

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


def reconstructLine(words,newtfLines):
	currentLine  = ''
	for word in words:
		currentLine += word
		currentLine += ','
	newtfLines.append(currentLine[:-1])

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


def tryMidpoints(Bus,originalBusList,currentSet,PSList):
	# see if the CAPE transformer matches to a midpoint set in planning
	skip = False
	Midpoint = MidpointNeighbour[Bus]
	MidptSet = MidpointDict[Midpoint]
	newtfData = []
	if currentSet == MidptSet:
		newtfData = reconstructMidPointData(originalBusList,PSList,Midpoint)
		skip = True
	return skip, newtfData



def reconstructMidPointData(originalBusList,PSList,Midpoint):
	# if CAPE tf can be mapped to a three winder set in PSSE, do it here
	tfData = MidpointTFdata[Midpoint] # contains 3 lists, each lists has multiple lines consisting of tf data
	newtfData = [] # new tf list, to be returned

	#if Midpoint == '275174':
	#	print MidpointTFdata[Midpoint]
	for tf in tfData: # tf: list of tf data
		newtf = list(tf)
		BusLineWords = newtf[0].split(',') # get words for Bus Line
		Bus1 = BusLineWords[0].strip()
		Bus2 = BusLineWords[1].strip()
		#print Bus1
		#print Bus2
		#PSindex = 0

		# find the phase shift index (PSIndex) and the CAPE bus number (newBus)
		if Bus1 == Midpoint:
			for b in originalBusList:
				if MapDict[b] == Bus2:
					bNew = b
					if b in newNoDict.keys():
						bNew = newNoDict[b] 
					BusLineWords[1] = ' '*(6-len(bNew)) +  bNew
					PSindex = originalBusList.index(b)
					MidPtPosition = 0 # if 0, then the PSValue is inverted (+ve-> -ve or -ve -> +ve)
					break
		elif Bus2 == Midpoint:
			for b in originalBusList:
				if MapDict[b] == Bus1:
					bNew = b
					if b in newNoDict.keys():
						bNew = newNoDict[b]
					BusLineWords[0] = ' '*(6-len(bNew)) +  bNew
					PSindex = originalBusList.index(b)
					MidPtPosition = 1 # if 1, then PSValue remains unchanged
					break

		#print originalBusList.index(b)
		#print b
		#print originalBusList
		#print Bus2
		#print Bus1
		#print tf[0]
		# reconstruct first line of tf data and insert it into the list
		newBusLine = reconstructLine2(BusLineWords)
		newtf[0] = newBusLine

		# insert the PS value
		#print PSindex
		PSValue = PSList[PSindex]
		if MidPtPosition == 0: # Midpoint is Bus1, change PSValue sign
			PSValueFloat = float(PSValue)
			if PSValueFloat != 0.0: # if 0, no need to change sign
				PSValueFloat = -PSValueFloat
			PSValue = str(PSValueFloat)

		PSLineWords = newtf[2].split(',')
		PSLineWords[2] = PSValue
		# reconstruct PSLine
		newPSLine = reconstructLine2(PSLineWords)
		newtf[2] = newPSLine

		# populate new tf data
		newtfData.append(newtf)

	return newtfData



def getPhaseShifts(i, fileLines, Bus3):
	#get original tf phase shifts, to be added in to new 2 winders
	PSList = [] # ordered as primary, secondary and tertiary
	
	if Bus3 != '0': # three winder
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
	else: # two winder
		i+=2 #skip this line and the next line
		line = fileLines[i]
		words = line.split(',')
		PS = words[2].strip()
		PSList.append(PS)


	return PSList
	


def generateIssueString(currentBusList,planningBusList):

	string = ''

	for bus in currentBusList:
		string += bus
		#string += '[' + CAPEVoltageDict[bus] + ']'
		string += ','

	string = string[:-1]

	string += '->'

	for bus in planningBusList:
		string += bus
		#string += '[' + planningVoltageDict[bus] + ']'
		string += ','

	string = string[:-1]

	return string



# get the new 4 winder data, to be added in as a string at the end of the new tf file

#with open(new4winderDataFile,'r') as f:
#	new4winderdata = f.read()

"""
# get a set of fict buses added by us and do not need to be included in the new bus data
with open(deleteFictBusFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		words = line.split(',')
		if len(words) <2:
			continue
		FictBusSet.add(words[0].strip())
"""

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
		newNoDict[OldBus] = NewBus

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

"""
# get a set of all the tf which were originally 4 winders and which have been replaced with 2 winder data
with open(delete4winderDataFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		FourWinderList.append(line.strip())

with open(delete4winderNoAlignMent,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		FourWinderListNoAlign.append(line.strip())
"""






# get a set of comed buses
with open(PSSErawFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split("\n")
	for line in fileLines:
		if ('PSS' in line) or ('COMED' in line) or ('DYNAMICS' in line):
		    continue
		if 'END OF BUS DATA' in line:
		    break
		words = line.split(',')
		if len(words)<2: # continue to next iteration of loop if its a blank line
		    continue

		Bus = words[0].strip()
		BusCode = words[3].strip()
		Busvoltage = words[2].strip()
		area = words[4].strip()
		if area == '222':
		    ComedBusSet.add(Bus)
		    planningVoltageDict[Bus] = Busvoltage # populate the planning voltage dict


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
	if Bus3 == '0':
		if Bus1 in ComedBusSet:
			CZ = words[5]
			i+=1
			line = fileLines[i]
			words = line.split(',')
			R12 = words[0]
			X12 = words[1]
			SBASE12 = words[2]
			#R23 = words[3]
			#X23 = words[4]
			#SBASE23 = words[5]
			#R31 = words[6]
			#X31 = words[7]
			#SBASE31 = words[8]
			if key not in planningTFDict.keys():
				planningTFDict[key] = [CZ,R12,X12,SBASE12]
			else:
				print 'Duplicate TF data: ', key
				sameBusMultiTFset.add(key)
			i+=3 # continue to next TF
		else:
			i+=4

	else:
		if Bus1 in ComedBusSet:
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
				print 'Duplicate TF data: ', key
				sameBusMultiTFset.add(key)
			i+=4 # continue to next TF
		else:
			i+=5








# open up CAPE tf data
with open(CAPERaw,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split("\n")

	# generate a cape dict of bus voltages
	for line in fileLines:
		if ('PSS' in line) or ('COMED' in line):
			continue
		if 'END OF BUS DATA' in line:
			break
		words = line.split(',')
		if len(words) <2:
			continue
		Bus = words[0].strip()
		Busvoltage = words[2].strip()
		CAPEVoltageDict[Bus] = Busvoltage



	tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
	tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')



# generate a dictionary of three winding transformers to be mapped
i = tfStartIndex
while i < tfEndIndex:
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	Bus3 = words[2].strip()
	cktID = words[3].strip()
	key = Bus1+','+Bus2+','+Bus3+','+cktID
	if Bus3 != '0':
		toChange3winder[key] = ''
		i+=5
	else: # two winder, dont care
		i+=4



# start the actual changes
i = tfStartIndex
while i < tfEndIndex:
	#print i
	line = fileLines[i]

	"""
	# deal with tf data which were originally 4 winders and have been substituted by planning tf data
	fourWindertfFound = 0 # flag which indicates if a 4 winder has been found or not
	for tf in FourWinderList:
		if tf in line:
			#print line
			fourWindertfFound = 1
			break

	if fourWindertfFound == 1:
		tfWords = tf.split(',')
		Bus3 = tfWords[2].strip()
		if Bus3 == '0':
			i+=4
			continue
		else:
			i+=5
			continue
	#####################
	"""


	#print line
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	Bus3 = words[2].strip()
	cktID = words[3].strip()
	#key = Bus1 + ',' + Bus2 + ',' + Bus3 + ','  + cktID
	
	currentBusList = [Bus1, Bus2, Bus3, cktID]

	PSList = getPhaseShifts(i, fileLines, Bus3)


	if Bus3 != '0':

		# record any phase shifts
		if float(PSList[1]) != 0.0:
			if Bus2 not in UATBusSet:
				UATAngleDict[Bus2] = float(PSList[1])
				UATBusSet.add(Bus2)
		if float(PSList[2]) != 0.0:
			if Bus3 not in UATBusSet:
				UATAngleDict[Bus3] = float(PSList[2])
				UATBusSet.add(Bus3)



		############

		key3winderMapLog = Bus1+','+Bus2+','+Bus3+','+cktID # used to get the relevant key in toChange3winder
		# get mapped planning bus and if one or more mapped buses are same, add the lines and skip
		planningBus1 = getPlanningBusNo(Bus1,oldNoDict,MapDict)
		planningBus2 = getPlanningBusNo(Bus2,oldNoDict,MapDict)
		planningBus3 = getPlanningBusNo(Bus3,oldNoDict,MapDict)
		planningBusList = [planningBus1,planningBus2,planningBus3]
		

		if Bus1 in oldNoDict.keys():
			originalBus1 = oldNoDict[Bus1]
		else:
			originalBus1 = Bus1

		if Bus2 in oldNoDict.keys():
			originalBus2 = oldNoDict[Bus2]
		else:
			originalBus2 = Bus2

		if Bus3 in oldNoDict.keys():
			originalBus3 = oldNoDict[Bus3]
		else:
			originalBus3 = Bus3

		originalBusList = [originalBus1,originalBus2,originalBus3]
		GenBusPresent = False
		
		#if (Bus1 in TrueGenBusSet) or (Bus2 in TrueGenBusSet) or (Bus3 in TrueGenBusSet):
		for Bus in currentBusList:
			if Bus in TrueGenBusSet:
				GenBus = Bus
				GenBusPresent = True
				break
		#case 1: any one of the bus is a planning gen
		if GenBusPresent == True:
			try:
				for key in planningTFDict.keys():
					if GenBus in key:
						#print key
						data = planningTFDict[key]
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
						reconstructLine(words,newtfLines)

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
						reconstructLine(words,newtfLines)
						break
				i = addMultLines(i,fileLines,newtfLines,3)
				toChange3winder[key3winderMapLog] = str(planningBusList) # add to log dict
				i+=1
				continue
			except: # no corresponding three winder in planning data, just add all the 5 lines of the 3 winder
				#print line
				newtfLines.append(line)
				i = addMultLines(i,fileLines,newtfLines,4)
				i+=1
				continue
		

		else: # none of the buses in the CAPE 3 winder is a true gen bus
			if len(set(planningBusList)) <3: # all the mapping is not unique


				if len(set(planningBusList)) == 1: # all three buses mapped to the same planning bus, leave them as is, just change the angles if necessary
					Bus2 = currentBusList[1]
					Bus3 = currentBusList[2]
					Bus2V = float(CAPEVoltageDict[Bus2])
					Bus3V = float(CAPEVoltageDict[Bus3])
					noPlanningBusList = ['0,0,0']
					out = generateIssueString(currentBusList,noPlanningBusList) # the '0,0,0' map means leave as is
					toChange3winder[key3winderMapLog] = str(noPlanningBusList)
					notfCaseLines.append(out)
					#UATAngleDict[Bus2] = float(PSList[1])
					#UATAngleDict[Bus3] = float(PSList[2])

					"""
					#get which phase shifts are actually being changed
					if float(PSList[1]) != 0.0:
						#print fileLines[i]
						UATBusSet.add(Bus2)

					elif float(PSList[2]) != 0.0:
						#print fileLines[i]
						UATBusSet.add(Bus3)
					"""
					
					# no corresponding three winder in planning data, just add all the 5 lines of the 3 winder and continue
					newtfLines.append(line)
					i = addMultLines(i,fileLines,newtfLines,4)
					i+=1
					continue


				else: # only two of the three mapped tf buses are unique
					if planningBus1 in tfNeighbourDict.keys():
						if planningBus2 not in tfNeighbourDict[planningBus1]:	# CAPE three winder cannot be mapped to a two winder	
							string = generateIssueString(currentBusList,planningBusList)
							tfIssueLines.append(string)
							#  add all the 5 lines of the 3 winder and continue
							newtfLines.append(line)
							i = addMultLines(i,fileLines,newtfLines,4)
							i+=1
							continue

						else: # CAPE three winder can be mapped to a two winder	
							if str(planningBusList[:-1]) not in threetoTwoWinderFoundSet: # dont include tertiary winding
								threetoTwoWinderFoundSet.add(str(planningBusList[:-1]))
								string = generateIssueString(currentBusList,planningBusList)
								threetoTwoWinderReplaceLines.append(string)
								#  add all the 5 lines of the 3 winder and continue
								newtfLines.append(line)
								i = addMultLines(i,fileLines,newtfLines,4)
								i+=1
								continue

							else: # multiple CAPE 3 winders are being mapped to a single planning 2 winder
								string = generateIssueString(currentBusList,planningBusList)
								threetoTwoWinderReplaceLines.append(string)
								threetoTwoWinderDuplicateIssue.append(string)
								#  add all the 5 lines of the 3 winder and continue
								newtfLines.append(line)
								i = addMultLines(i,fileLines,newtfLines,4)
								i+=1
								continue

								
								
					else: # CAPE three winder cannot be mapped to a two winder
						string = generateIssueString(currentBusList,planningBusList)
						tfIssueLines.append(string)
						#  add all the 5 lines of the 3 winder and continue
						newtfLines.append(line)
						i = addMultLines(i,fileLines,newtfLines,4)
						i+=1
						continue

	

				#i+=5
				#continue

			# if all the windings are uniquely mapped, then see if there are exact three winder matches
			notFound = True
			for key in planningTFDict.keys():
				if planningBus1 in key and planningBus2 in key and planningBus3 in key:
					notFound = False
					toChange3winder[key3winderMapLog] = str(planningBusList) # add to log dict
					#print 'Mapped: '+ str(originalBusList) + '->' + str(planningBusList)
					data = planningTFDict[key]
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
					reconstructLine(words,newtfLines)

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
					reconstructLine(words,newtfLines)
					break

			if notFound == True: # three winder equivalent tf not found, append 2 lines
				#print 'Ok'
				currentSet = set([planningBus1,planningBus2,planningBus3])
				if planningBus1 in MidpointNeighbour.keys():
					#PSList = getPhaseShifts(i, fileLines)
					skip, newtfData = tryMidpoints(planningBus1,originalBusList,currentSet,PSList)
					if skip == True:
						# Add to log file
						toChange3winder[key3winderMapLog] = str(currentSet)

						#### Add new tf lines here (remember it is a nested list)
						for tf in newtfData:
							for line in tf:
								newtfLines.append(line)
						
						# Add midpoint buses in bus data
						midpoint = MidpointNeighbour[planningBus1]
						newMidPointLines.append(ComedMidpointBusData[midpoint])
						i+=5 # skip to next tf
						continue

				elif planningBus2 in MidpointNeighbour.keys():
					#PSList = getPhaseShifts(i, fileLines)
					skip, newtfData = tryMidpoints(planningBus2,originalBusList,currentSet,PSList)
					if skip == True:
						# Add to log file
						toChange3winder[key3winderMapLog] = str(currentSet)

						#### Add new tf lines here (remember it is a nested list)
						for tf in newtfData:
							for line in tf:
								newtfLines.append(line)

						# Add midpoint buses in bus data
						midpoint = MidpointNeighbour[planningBus2]
						newMidPointLines.append(ComedMidpointBusData[midpoint])
						i+=5 # skip to next tf
						continue

				elif planningBus3 in MidpointNeighbour.keys():
					#PSList = getPhaseShifts(i, fileLines)
					skip, newtfData = tryMidpoints(planningBus3,originalBusList,currentSet,PSList)
					if skip == True:
						# Add to log file
						toChange3winder[key3winderMapLog] = str(currentSet)

						#### Add new tf lines here (remember it is a nested list)
						for tf in newtfData:
							for line in tf:
								newtfLines.append(line)

						# Add midpoint buses in bus data
						midpoint = MidpointNeighbour[planningBus3]
						newMidPointLines.append(ComedMidpointBusData[midpoint])
						i+=5 # skip to next tf
						continue



				#print 'Ok'
				# execute if tf not found in midpoint set
				newtfLines.append(line)
				i+=1
				line = fileLines[i]
				newtfLines.append(line)

			# append the next three lines and then increase the index and continue
			#print 'Ok'
			i = addMultLines(i,fileLines,newtfLines,3)
			i+=1
			continue


			
	else: # two winder
		# record any phase shifts
		#UATAngleDict[Bus2] = float(PSList[0])
		#get which phase shifts are actually being changed
		if float(PSList[0]) != 0.0:
			#print fileLines[i]
			if float(CAPEVoltageDict[Bus1]) >= 69.0: # step down transformer and phase shift occurs on the high side

				if Bus2 not in UATBusSet:
					UATBusSet.add(Bus2) #  add the LV bus to bus whose angle need to be changed
					UATAngleDict[Bus2] = -float(PSList[0]) # negate the value of the phase shift

			else: # normal case, just add the bus set and the angle shift
				if Bus1 not in UATBusSet:
					UATBusSet.add(Bus1)
					UATAngleDict[Bus1] = float(PSList[0])

		############

		newtfLines.append(line)
		i = addMultLines(i,fileLines,newtfLines,3)

		i+=1 # continue





# Create new files

# add cases of FinalSolFile in the log file
with open(FinalSolFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		if 'txt' in line:
			continue
		words = line.split('->')
		CAPEPart = words[0].strip()
		planningPart = words[1].strip()
		#print CAPEPart
		if CAPEPart in toChange3winder.keys():
			toChange3winder[CAPEPart] = planningPart
		else:
			print line




#print getPlanningBusNo('750333',oldNoDict,MapDict)
with open(newTFFile,'w') as f:
	for line in newtfLines:
		f.write(line)
		f.write('\n')
	#f.write(new4winderdata)


# print a log data
stillToSolveLines = [] # three winder tf which still are issues
with open(tf3winderchangeLog,'w') as f:
	for key in toChange3winder.keys():
		line = key + '->' + toChange3winder[key]
		
		if key in FourWinderListNoAlign:
			continue
		
		if toChange3winder[key] == '':
			CAPEBuses = key.split(',')
			Bus1 = CAPEBuses[0].strip()
			Bus2 = CAPEBuses[1].strip()
			Bus3 = CAPEBuses[2].strip()
			planningBus1 = getPlanningBusNo(Bus1,oldNoDict,MapDict)
			planningBus2 = getPlanningBusNo(Bus2,oldNoDict,MapDict)
			planningBus3 = getPlanningBusNo(Bus3,oldNoDict,MapDict)

			planningBuses = planningBus1 + ',' + planningBus2 + ',' + planningBus3
			line2 = key + '->' + planningBuses
			stillToSolveLines.append(line2)


		f.write(line)
		f.write('\n')




###########


###### generate new bus angles according to phase shift

with open(AllMapFileOld,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		words = line.split(',')
		if len(words) <2:
			continue

		Bus = words[0].strip()
		"""
		if Bus in FictBusSet: # dont include fictitious buses added by us
			continue
		"""
		if Bus in UATBusSet: # bus needs to have angle changed
			Angle = words[8].strip()
			newAngle = float(Angle) + UATAngleDict[Bus]
			words[8] = ' '*(9- len(str(newAngle))) + str(newAngle)
			nLine = reconstructLine2(words)
			newBusLines.append(nLine) # append the bus line which has angles changed
			newBusAngleLines.append(nLine) # used as a log of all the buses which have phase shifted
		else: # bus does not need to have angle changed
			newBusLines.append(line)

# keep a log of all bus angles changed, to incorporate tf phase shift
with open(newBusAngles,'w') as f:
	f.write('Log of all buses where angles have been changed to incorporate tf phase shift:')
	f.write('\n')
	for line in newBusAngleLines:
		f.write(line)
		f.write('\n')



# these two lines are needed for the 4 winder tf data
#newMidPointLines.append("275152,'RIDGELAND;1M',  69.0000,1, 222,   8, 222,0.99952, -66.6867,1.10000,0.90000,1.10000,0.90000")
#newMidPointLines.append("275153,'RIDGELAND;2M',  69.0000,1, 222,   8, 222,1.02012, -68.4367,1.10000,0.90000,1.10000,0.90000")
# change bus angles in the bus data
with open(AllMapFile,'w') as f:
	for line in newBusLines:
		f.write(line)
		f.write('\n')
	# add midpoint buses
	for line in newMidPointLines:
		f.write(line)
		f.write('\n')	
#############

# issue file which lists all cases where the primary and secondary of a CAPE three winder
# cannot be even mapped to a planning 2 winder
with open(tfIssueFile,'w') as f:
	f.write('Cases where the primary and secondary of a CAPE three winder cannot be even mapped to a planning 2 winder:')
	f.write('\n')
	for line in tfIssueLines:
		f.write(line)
		f.write('\n')

# lists cases where multiple CAPE 3 winders are being mapped to a single planning 2 winder
with open(threetoTwoWinderDuplIssue,'w') as f:
	f.write('Cases where multiple CAPE 3 winders are being mapped to a single planning 2 winder by original map:')
	f.write('\n')
	for line in threetoTwoWinderDuplicateIssue:
		f.write(line)
		f.write('\n')

# lists cases where the script says multiple 3 winders can be mapped to a single 2 winder
# This file also includes cases included in threetoTwoWinderDuplIssue
# This file needs to be analyzed by changeThreeToTwoWinderTFMapping.py
with open(threetoTwoWinderAuto,'w') as f:
	f.write('Cases where CAPE 3 winders may be mapped to planning 2 winders, but need to be re-evaluated:')
	f.write('\n')
	for line in threetoTwoWinderReplaceLines:
		f.write(line)
		f.write('\n')

# cases where a CAPE 3 winder has no tf in planning, left as is, only considering phase shifts
with open(notfCases,'w') as f:
	f.write('Cases where a CAPE 3 winder has no tf in planning, left as is, only considering phase shifts:')
	f.write('\n')
	for line in notfCaseLines:
		f.write(line)
		f.write('\n')

# generate the cases which still need to be solved
with open(stillToSolveCases,'w') as f:
	f.write('Cases which are yet to be solved even after incorporating FinalSolFile.txt')
	f.write('\n')
	for line in stillToSolveLines:
		f.write(line)
		f.write('\n')


# generate bus angle change data, will be used in changeBusAngleTree to determine angle
# change in connected buses

with open(angleChangeFile,'w') as f:
	line = 'Bus->Angle Change'
	f.write(line)
	f.write('\n')
	for key in UATAngleDict.keys():
		line = key + '->' + str(UATAngleDict[key])
		f.write(line)
		f.write('\n')



# execute other scripts which fix more tf

import NewMidpointTFFix # converts all the 3w to sets of 2w detailed in AdvancedMidpointCases.txt
import Fix3wto3wAndNoChangeCasesInFinalSol # handles cases in Final Sol where there is no equivalent tf, or a 3w->3w substitution
import AppendAndCheckLog # to check what tf still remain to be substituted
#import changeBusAngleTree # BFS tree to change all remaining bus angles (for neighbours of buses which were changed originally)