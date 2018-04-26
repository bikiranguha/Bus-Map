"""
Prints any branches whose ends are not of the same voltage
"""

raw_file = 'RAW0406018.raw' # using this rawfile to avoid 2 winder midpoint sets

BusVoltDict = {}
ComedBusSet = set()


# get comed bus voltages
with open(raw_file, 'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if ('PSS' in line) or ('COMED' in line) or ('DYNAMICS' in line):
			continue
		if 'END OF BUS DATA' in line:
			break
		words = line.split(',')
		if len(words) <2:
			continue
		Bus = words[0].strip()
		BusVolt = float(words[2].strip())
		area = words[4].strip()
		if area == '222':
			ComedBusSet.add(Bus)
		BusVoltDict[Bus] = BusVolt

branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA') + 1
branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')


# add anything between end of bus data and beginning of branch data
print 'List of branches having different bus voltages at either end:'
for i in range(branchStartIndex,branchEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()

	if Bus1 in ComedBusSet or Bus2 in ComedBusSet:
		if BusVoltDict[Bus1] != BusVoltDict[Bus2]:
			print line