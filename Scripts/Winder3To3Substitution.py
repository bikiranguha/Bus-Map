# looking at the latest tf file, applies all the 3 winder subs. Only the impedances are changed and SBASE values are changed, tap ratios are not changed.


ThreeWSubDict = {}
ThreeWinderSubSetCAPE = set()
ThreeWinderSubSetPlanning = set()
planningTFDict = {}
changeNameDictOldToNew = {}
ThreeWToThreeWSubFile = 'test3wTo3wSub.txt'
PSSErawFile = 'hls18v1dyn_new.raw'
latestTFFIle = 'TFIter1.txt'
newtfLines = []
NewTFFile = 'TF3wTo3wSub.txt'
changeLog = 'changeBusNoLog.txt'

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

			planningTFDict[key] = [CZ,R12,X12,SBASE12,R23,X23,SBASE23,R31,X31,SBASE31]
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
		newtfLines.append(line)
		i = addMultLines(i,fileLines,newtfLines,3)
		i+=1
		continue

	else: # three winder
		key = Bus1+','+Bus2+','+Bus3+','+cktID

		# Add algorithm for 3w->3w substitution
		if key in ThreeWinderSubSetCAPE:
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

			# add remaining 3 lines
			i = addMultLines(i,fileLines,newtfLines,3)
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