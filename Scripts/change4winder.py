deleteFictBusFile = 'deleteFictBusList.txt'
delete4winderDataFile = 'deleteOld4winderdata.txt'
AllMapFile = 'AllMappedBusData.txt'
AllMapFileNew = 'AllMappedBusDataNew.txt'

FictBusSet = set()
FourWinderSet = set()
newBusLines = []

with open(deleteFictBusFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		words = line.split(',')
		if len(words) <2:
			continue
		FictBusSet.add(words[0].strip())

with open(delete4winderDataFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		FourWinderSet.add(line.strip())


with open(AllMapFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		words = line.split(',')
		if len(words) <2:
			continue

		Bus = words[0].strip()
		if Bus not in FictBusSet:
			newBusLines.append(line)

with open(AllMapFileNew,'w') as f:
	for line in newBusLines:
		f.write(line)
		f.write('\n')


