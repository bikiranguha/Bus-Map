"""
	Script to generate new branch data with any bus number changes incorporated
	Any branch which contains buses which are outside comed are skipped while building new branch data
	Note: Verified that no gen bus has any branch connections
"""

#newdir = 'Important data'

changeLog = 'changeBusNoLog.txt'
CAPERaw = 'CAPE_RAW0228v33.raw'
outsideComedFile = 'outsideComedBusesv4.txt'
newbranchData =  'newbranchData.txt' # output of this file

OldBusSet = set()
NewBusSet = set()
#MapDict = {}
#GenDict = {}
MapDict = {} # key: Old bus number, value: new bus number
noNeedtoMapSet = set()

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
		OldBusSet.add(OldBus)
		NewBusSet.add(NewBus)
		MapDict[OldBus] = NewBus


# get a set of buses which dont need to be included in the branch data
with open(outsideComedFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'Manually' in line:
			continue
		if line.strip() != '':
			noNeedtoMapSet.add(line.strip())
			#CAPEMappedSet.add(line.strip())



def changeBus(Bus,words,MapDict):
	#print Bus
	newLine = ''
	newBus = MapDict[Bus]
	lennewBus = len(newBus)
	newBus = ' '*(6 - lennewBus) + newBus
	for word in words:
		if word.strip() == Bus:
			word = newBus
			newLine += word
			newLine += ','
		elif word == words[-1]:
			newLine += word
		else:
			newLine += word
			newLine += ','
	#print newLine
	return newLine






# generate the new branch lines
branchLines = []
with open(CAPERaw, 'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA') + 1
	branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')

	for i in range(branchStartIndex, branchEndIndex):
		line = fileLines[i]
		words = line.split(',')
		Bus1 = words[0].strip()
		Bus2 = words[1].strip()
		noNeedtoMapSet.add('998884') # temporary manual addition
		if Bus1 in noNeedtoMapSet:
			continue
		if Bus2 in noNeedtoMapSet:
			continue

		if Bus1 in OldBusSet:
			#print line
			line = changeBus(Bus1,words,MapDict)
			words = line.split(',')
			#print line
			#branchLines.append(line)
		if Bus2 in OldBusSet:
			#print line
			line = changeBus(Bus2,words,MapDict)
			#print line
			#branchLines.append(line)
		
		branchLines.append(line)



# output branch data
with open(newbranchData, 'w') as f:
	for line in branchLines:
		f.write(line)
		f.write('\n')





