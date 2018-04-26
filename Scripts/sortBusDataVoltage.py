Busdata = 'AllMappedBusDataOld.txt'
BusdataSorted = 'AllMappedBusDataSorted.txt'

VoltSet = set()

with open(Busdata,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')


# get a set of all bus voltage levels
for line in fileLines:
	words = line.split(',')
	if len(words) <2:
		continue

	Busvoltage = words[2].strip()
	VoltSet.add(Busvoltage)

VoltDescending = sorted(list(VoltSet))
print VoltDescendingl