from getMidpointData import ComedMidpointSet, MidpointDict, MidpointNeighbour

changeLog = 'changeBusNoLog.txt'
MapLog = 'AllMappedLog.txt'
verifiedMapFile = 'PSSEGenMapVerified.txt'
PSSErawFile = 'hls18v1dyn_new.raw'
CAPERaw = 'NewCAPERawClean.raw'
newTFFile = 'newTFFile.txt'

oldNoDict = {} # keys: Old (original) CAPE bus numbers, values: new CAPE bus numbers
MapDict = {} # keys: Original CAPE bus numbers, values: corresponding planning numbers
ComedBusSet = set() 
planningTFDict = {}
TrueGenBusSet = set()
sameBusMultiTFset = set()
newtfLines = []
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



def addMultLines(i,fileLines,newtfLines,numLines):
	# for adding transformer lines which do not change
	for j in range(numLines):
		i+=1
		line = fileLines[i]
		newtfLines.append(line)	
	return i


def tryMidpoints(Bus,MidpointNeighbour,MidpointDict,originalBusList,currentSet):
	skip = False
	Midpoint = MidpointNeighbour[Bus]
	MidptSet = MidpointDict[Midpoint]
	if currentSet == MidptSet:
		print 'Mapped: ' + str(originalBusList) + '->' + str(currentSet)
		skip = True
	return skip


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


i = tfStartIndex
while i < tfEndIndex:
	#print i
	line = fileLines[i]
	#print line
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	Bus3 = words[2].strip()
	currentBusList = [Bus1, Bus2, Bus3]

	if Bus3 != '0':
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
				i+=1
				continue
			except: # no corresponding three winder in planning data, just add all the 5 lines of the 3 winder
				print line
				newtfLines.append(line)
				i = addMultLines(i,fileLines,newtfLines,4)
				i+=1
				continue
		# case 2: found exact match for three winding tf in planning data
		else:
			# get mapped planning bus and if one or more mapped buses are same, add the lines and skip
			planningBus1 = getPlanningBusNo(Bus1,oldNoDict,MapDict)
			planningBus2 = getPlanningBusNo(Bus2,oldNoDict,MapDict)
			planningBus3 = getPlanningBusNo(Bus3,oldNoDict,MapDict)
			planningBusList = [planningBus1,planningBus2,planningBus3]
			if len(set(planningBusList)) <3: # all the mapping is not unique
				#print 'Issues: ' + str(originalBusList) + '->' + str(planningBusList)
				i+=5
				continue

			# if all the windings are uniquely mapped, then see if there are exact three winder matches
			notFound = True
			for key in planningTFDict.keys():
				if planningBus1 in key and planningBus2 in key and planningBus3 in key:
					notFound = False
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
				if planningBus1 in MidpointNeighbour:
					skip = tryMidpoints(planningBus1,MidpointNeighbour,MidpointDict,originalBusList,currentSet)
					if skip == True:
						i+=5 # skip to next tf
						continue

				elif planningBus2 in MidpointNeighbour:
					skip = tryMidpoints(planningBus2,MidpointNeighbour,MidpointDict,originalBusList,currentSet)
					if skip == True:
						i+=5 # skip to next tf
						continue

				elif planningBus3 in MidpointNeighbour:
					skip = tryMidpoints(planningBus3,MidpointNeighbour,MidpointDict,originalBusList,currentSet)
					if skip == True:
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
