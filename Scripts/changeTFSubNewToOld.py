file = 'changeNewToOldTFSub.txt'
changeLogPrevious  = 'changeBusNoLogPrevious.txt' # log of all bus number changes carried out previously
changeNameDictNewToOld = {}

# look at log files which contains all the changed bus numbers in the previous iteration (first time i did this)
with open(changeLogPrevious,'r') as f:
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
		changeNameDictNewToOld[NewBus] = OldBus


with open(file,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split("\n")
	for line in fileLines:
		if '->' not in line:
			continue
		words = line.split('->')
		CAPEPart = words[0].strip()
		planningPart = words[1].strip()
		CAPEBuses = CAPEPart.split(',')
		Bus1 = CAPEBuses[0]
		Bus2 = CAPEBuses[1]
		Bus3 = CAPEBuses[2]
		cktID = CAPEBuses[3]

		if Bus1 in changeNameDictNewToOld.keys():
			Bus1 = changeNameDictNewToOld[Bus1]

		if Bus2 in changeNameDictNewToOld.keys():
			Bus2 = changeNameDictNewToOld[Bus2]

		if Bus3 in changeNameDictNewToOld.keys():
			Bus3 = changeNameDictNewToOld[Bus3]

		NewCAPEPart = Bus1.rjust(6) + ',' + Bus2.rjust(6) + ',' + Bus3.rjust(6) + ',' +  cktID
		nLine = NewCAPEPart + '->' + planningPart
		print nLine
 