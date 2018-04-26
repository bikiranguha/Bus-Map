from getMidpointDatav2 import ComedMidpointSet, MidpointDict, MidpointNeighbour, MidpointTFdata, ComedMidpointBusData
#print MidpointTFdata['275174']
changeLog = 'changeBusNoLog.txt'
MapLog = 'AllMappedLog.txt'
verifiedMapFile = 'PSSEGenMapVerified.txt'
PSSErawFile = 'hls18v1dyn_new.raw'
CAPERaw = 'NewCAPERawClean.raw'
newTFFile = 'newTFFile.txt'
tf3winderchangeLog = 'tf3winderchangeLog.txt'
AllMapFile = 'AllMappedBusData.txt'

oldNoDict = {} # keys: Old (original) CAPE bus numbers, values: new CAPE bus numbers
MapDict = {} # keys: Original CAPE bus numbers, values: corresponding planning numbers
ComedBusSet = set() 
planningTFDict = {}
TrueGenBusSet = set()
sameBusMultiTFset = set()
newtfLines = []
toChange3winder = {} # dictionary which will contain the 3 winder changelog
newMidPointLines = []
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


def tryMidpoints(Bus,originalBusList,currentSet,PSList,MidpointTFdata):
	# see if the CAPE transformer matches to a midpoint set in planning
	skip = False
	Midpoint = MidpointNeighbour[Bus]
	MidptSet = MidpointDict[Midpoint]
	newtfData = []
	if currentSet == MidptSet:
		newtfData = reconstructMidPointData(originalBusList,PSList,Midpoint,MidpointTFdata)
		skip = True
	return skip, newtfData



def reconstructMidPointData(originalBusList,PSList,Midpoint,MidpointTFdata):
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
					BusLineWords[1] = ' '*(6-len(b)) +  b
					PSindex = originalBusList.index(b)
					break
		elif Bus2 == Midpoint:
			for b in originalBusList:
				if MapDict[b] == Bus1:
					BusLineWords[0] = ' '*(6-len(b)) +  b
					PSindex = originalBusList.index(b)
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
		PSLineWords = newtf[2].split(',')
		PSLineWords[2] = PSValue
		# reconstruct PSLine
		newPSLine = reconstructLine2(PSLineWords)
		newtf[2] = newPSLine

		# populate new tf data
		newtfData.append(newtf)

	return newtfData












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
        BusCode = words[3].strip()
        area = words[4].strip()
        if area == '222':
            ComedBusSet.add(words[0].strip()) 


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
# if any of the bus in the tf data is a true gen, write a function to get the corresponding data
with open(CAPERaw,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split("\n")	

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
	#print line
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	Bus3 = words[2].strip()
	cktID = words[3].strip()
	
	currentBusList = [Bus1, Bus2, Bus3]



	if Bus3 != '0':
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
		# case 2: found exact match for three winding tf in planning data
		else:
			if len(set(planningBusList)) <3: # all the mapping is not unique
				#print 'Issues: ' + str(originalBusList) + '->' + str(planningBusList)
				i+=5
				continue

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
					PSList = getPhaseShifts(i, fileLines)
					skip, newtfData = tryMidpoints(planningBus1,originalBusList,currentSet,PSList,MidpointTFdata)
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
					PSList = getPhaseShifts(i, fileLines)
					skip, newtfData = tryMidpoints(planningBus2,originalBusList,currentSet,PSList,MidpointTFdata)
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
					PSList = getPhaseShifts(i, fileLines)
					skip, newtfData = tryMidpoints(planningBus3,originalBusList,currentSet,PSList,MidpointTFdata)
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


			
	else:
		newtfLines.append(line)
		i = addMultLines(i,fileLines,newtfLines,3)

		i+=1 # continue




#print getPlanningBusNo('750333',oldNoDict,MapDict)
with open(newTFFile,'w') as f:
	for line in newtfLines:
		f.write(line)
		f.write('\n')

# print a log data
with open(tf3winderchangeLog,'w') as f:
	for key in toChange3winder.keys():
		line = key + '->' + toChange3winder[key]
		f.write(line)
		f.write('\n')


with open(AllMapFile,'a') as f:
	for line in newMidPointLines:
		f.write(line)
		f.write('\n')

