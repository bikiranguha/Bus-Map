from branchAutomation import ComedCAPESet345, noMismatch345Set
Map345CheckFile = 'Map345CheckFile.txt'
TrueMappingDict = {}
for bus in ComedCAPESet345:
	TrueMappingDict[bus] = ''

with open(Map345CheckFile,'w') as f:
	f.write('Status of 345 Map Check:')
	f.write('\n')
	for bus in TrueMappingDict.keys():
		string = bus + '->' + TrueMappingDict[bus]
		f.write(string)
		f.write('\n')
