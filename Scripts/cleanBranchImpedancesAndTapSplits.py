# changes branch impedance data to old bus numbers
# changes tap split data to old bus numbers

branchImpedanceChangeFile = 'BranchImpedanceChanges.txt'
tapSplitFile = 'tap_splits_temp.txt'
changeLog = 'changeBusNoLog.txt' # Bus number change log

changeDict = {} # new to old

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
		changeDict[NewBus] = OldBus

# get the old branch impedance changes (with new CAPE bus numbers) and generate the new data (new CAPE bus numbers)
with open(branchImpedanceChangeFile,'r') as f: 
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if '->' not in line:
			continue
		words = line.split('->')
		planningPart = words[0].strip()
		CAPEPart = words[1].strip()

		CAPEWords = CAPEPart.split(',')
		CAPEBus1 = CAPEWords[0].strip()
		CAPEBus2 = CAPEWords[1].strip()
		cktID = CAPEWords[2].strip()

		# change to new number system
		if CAPEBus1 in changeDict.keys():
			CAPEBus1 = changeDict[CAPEBus1]

		if CAPEBus2 in changeDict.keys():
			CAPEBus2 = changeDict[CAPEBus2]


		CAPEPart = CAPEBus1.rjust(6)+','+CAPEBus2.rjust(6)+','+cktID
		#print   planningPart + '->' + CAPEPart


# do the tap split bus number changes
with open(tapSplitFile,'r') as f: 
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		words = line.split(',')
		CAPEBus1 = words[0].strip()
		CAPEBus2 = words[1].strip()
		CAPEBus3 = words[2].strip()

		if CAPEBus1 in changeDict.keys():
			CAPEBus1 = changeDict[CAPEBus1]

		if CAPEBus2 in changeDict.keys():
			CAPEBus2 = changeDict[CAPEBus2]
		if CAPEBus3 in changeDict.keys():
			CAPEBus3 = changeDict[CAPEBus3]		

		nLine = CAPEBus1.rjust(6)+','+CAPEBus2.rjust(6)+','+CAPEBus3.rjust(6)
		print nLine