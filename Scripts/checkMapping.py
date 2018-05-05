# check to see all the tf mappings in testMapOld and ManualMapCSPriority1 appear in autoTFMap once and only once
# also checks if the mappings in testMapOld and ManualMapCSPriority1 and that of autoTFMap are the same

testMapOld = 'testMapOld.txt'
ManualMapCSPriority1 = 'Mapping_CSPriority1.txt'
autoTFMap  = 'autoTFMap0505.txt'

alreadyMappedTFSet = set() # manual maps done before any automation
needToBeThereLines = [] # mapping lines in testMapOld and ManualMapCSPriority1 which need to be there in autoTFMap
NumAppearance = {} # num of appearance of the manual maps in autoTFMap, should be one for every key
checkLines = {} # check to see if all manual maps are present in autoTFMap


# get all the planning tf keys in testMapOld
with open(testMapOld,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if '->' not in line:
			continue
		words = line.split('->')
		pTFID = words[0].strip() # planning TF ID in this file
		alreadyMappedTFSet.add(pTFID)
		needToBeThereLines.append(line.strip()) # add line for checking




# look at the manual maps done by the CS guys, version 2 (ie, the corrected mapping list)
with open(ManualMapCSPriority1,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:		
		if line == '':
			continue

		words = line.split('->')
		planningSide = words[0].strip()
		# check to see if this mapping already done in testMapOld or loadAlreadySplit file

		if planningSide in alreadyMappedTFSet:
			continue
		else:
			alreadyMappedTFSet.add(planningSide) # add tf id for checking

		CAPESide = words[1].strip()
		if CAPESide == '': # mapping not provided
			continue

		CAPESideWords = CAPESide.split(',')
		CAPESideShort = ''
		# eliminate any comments
		for i in range(3):
			CAPESideShort += CAPESideWords[i].strip()
			CAPESideShort += ','
		CAPESideShort = CAPESideShort[:-1]


		nLine = planningSide + '->' + CAPESideShort
		needToBeThereLines.append(nLine) # add line for checking


#construct the relevant dictionaries for checking
for planningTF in list(alreadyMappedTFSet):
	NumAppearance[planningTF] = 0

for line in needToBeThereLines:
	checkLines[line] = False
#######


# open the autoTFMap file and populate the relevant dictionaries to facilitate the checking
with open(autoTFMap,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if '->' not in line:
			continue
		if line == '':
			continue
		words = line.split('->')
		pTFID = words[0].strip() # planning TF ID in this file

		if pTFID in NumAppearance.keys():
			NumAppearance[pTFID] +=1

		if line.strip() in needToBeThereLines:
			checkLines[line.strip()] = True

# perform the checks
for tf in NumAppearance.keys():
	if NumAppearance[tf] != 1:
		print tf

for line in checkLines.keys():
	if checkLines[line] != True:
		print line