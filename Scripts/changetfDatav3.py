"""
	Changes the tf data by updating the bus numbers and also skipping any transformer data which includes buses outside of comed
"""


#CAPERaw = 'CAPE_RAW1116v33.raw'
#newdir = 'Important data'
changeLog = 'changeBusNoLog.txt'
CAPERaw = 'CAPE_RAW0225v33.raw'
outsideComedFile = 'outsideComedBusesv4.txt'

newtfData = 'newtfData.txt'
outsideComedFile = 'outsideComedBusesv4.txt'

OldBusSet = set()
NewBusSet = set()
#MapDict = {}
#GenDict = {}
MapDict = {} # map of old bus numbers to new bus numbers
noNeedtoMapSet = set()

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
		#elif word == words[-1]:
		#	newLine += word
		else:
			newLine += word
			newLine += ','
	#print newLine
	return newLine[:-1]


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


tfLines = []
with open(CAPERaw, 'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
	tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')
	i = tfStartIndex
	while i < tfEndIndex:
		skip = 0
		line = fileLines[i]
		words = line.split(',')
		Bus1 = words[0].strip()
		Bus2 = words[1].strip()
		Bus3 = words[2].strip()

		if Bus3 == '0': # two winder
			if Bus1 in noNeedtoMapSet:
				i+=4
				continue
			elif Bus2 in noNeedtoMapSet:
				i+=4
				continue


			if Bus1 in OldBusSet:
				#print line
				line = changeBus(Bus1,words,MapDict)
				words = line.split(',')
				#print newLine
				#tfLines.append(newLine)
				#i+=1
				#line = fileLines[i]
			if Bus2 in OldBusSet:
				#print line
				line = changeBus(Bus2,words,MapDict)
				words = line.split(',')
				#print newLine
				#tfLines.append(newLine)
				#i+=1
				#line = fileLines[i]
			#else: # no bus in CAPESet
			tfLines.append(line)
			i+=1
			line = fileLines[i]

			for j in range(3): # get the next 3 lines of the transformer data
				tfLines.append(line)
				i+=1
				line = fileLines[i]

		else: # three winder
			if Bus1 in noNeedtoMapSet:
				i+=5
				continue
			elif Bus2 in noNeedtoMapSet:
				i+=5
				continue
			elif Bus3 in noNeedtoMapSet:
				i+=5
				continue

			if Bus1 in OldBusSet:
				#print line
				line = changeBus(Bus1,words,MapDict)
				words = line.split(',')
				#print newLine
				#tfLines.append(newLine)
				#i+=1
				#line = fileLines[i]
			if Bus2 in OldBusSet:
				#print line
				line = changeBus(Bus2,words,MapDict)
				words = line.split(',')
				#print newLine
				#tfLines.append(newLine)
				#i+=1
				#line = fileLines[i]
			if Bus3 in OldBusSet:
				#print line
				line = changeBus(Bus3,words,MapDict)
				words = line.split(',')
				#print newLine
				#tfLines.append(newLine)
				#i+=1
				#line = fileLines[i]
			#else: # no bus in CAPESet
			tfLines.append(line)
			i+=1
			line = fileLines[i]

			for j in range(4): # get the next 4 lines of the transformer data
				tfLines.append(line)
				i+=1
				line = fileLines[i]

with open(newtfData, 'w') as f:
	for line in tfLines:
		f.write(line)
		f.write('\n')





