"""
	Changes the tf data by updating the bus numbers and also skipping any transformer data which includes buses outside of comed
	Also sets  winding voltage to nominal voltage if difference greater than 20%
"""


#CAPERaw = 'CAPE_RAW1116v33.raw'
#newdir = 'Important data'
changeLog = 'changeBusNoLog.txt'
CAPERaw = 'CAPE_RAW0228v33.raw'


newtfData = 'newtfData.txt' # outputs the new tf data
outsideComedFile = 'outsideComedBusesv4.txt' # list of buses in CAPE case which are outside comed
BusData = 'AllMappedBusData.txt'

OldBusSet = set() # old bus numbers
NewBusSet = set() # new bus numbers
#MapDict = {}
#GenDict = {}
MapDict = {} # map of old bus numbers to new bus numbers
noNeedtoMapSet = set() # set of buses which do not need to be mapped in CAPE
BusVoltageDict = {} # dictionary of bus voltages


def checkWindingVoltage(line,currentBusList,BusIndex):
	"""
	function to set proper winding voltage if it deviates
	by more than 20% of the nominal voltage
	"""

	words = line.split(',')
	WindVolt = words[0].strip()
	NomVolt = words[1].strip()
	Bus = currentBusList[BusIndex]
	if Bus in OldBusSet:
		Bus = MapDict[Bus]
	if float(NomVolt) == 0.0: 
		NomVolt = BusVoltageDict[Bus]
	percentDiff = abs(float(WindVolt) - float(NomVolt))/float(NomVolt)

	if percentDiff > 0.2: # if difference greater than 20%, set to nominal voltage
		words[0] = NomVolt
		currentLine = ''
		for word in words:
			currentLine +=word
			currentLine += ','
		tfLines.append(currentLine[:-1])
	else:
		tfLines.append(line)


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


# gets the bus voltage info
with open(BusData,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		words = line.split(',')
		if len(words) <2:
			continue
		Bus = words[0].strip()
		Volt = words[2].strip()
		BusVoltageDict[Bus] = Volt



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
		line = fileLines[i]
		words = line.split(',')
		Bus1 = words[0].strip()
		Bus2 = words[1].strip()
		Bus3 = words[2].strip()
		
		# currentBusList contains a list of all the buses in the transformer, 
		# needed for checkWindingVoltage()
		currentBusList = []
		for j in range(3):
			currentBusList.append(words[j].strip())

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

			if Bus2 in OldBusSet:
				#print line
				line = changeBus(Bus2,words,MapDict)
				words = line.split(',')

			tfLines.append(line)
			# next line (just append)
			i+=1
			line = fileLines[i]
			tfLines.append(line)

			# next line (compare Bus1 winding and nominal voltage)
			i+=1
			line = fileLines[i]
			checkWindingVoltage(line,currentBusList,0)


			# next line (compare Bus2 winding and nominal voltage)
			i+=1
			line = fileLines[i]
			checkWindingVoltage(line, currentBusList, 1)


			i+=1 # go to next line



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

			if Bus2 in OldBusSet:
				#print line
				line = changeBus(Bus2,words,MapDict)
				words = line.split(',')

			if Bus3 in OldBusSet:
				#print line
				line = changeBus(Bus3,words,MapDict)
				words = line.split(',')

			tfLines.append(line)

			# next line (just append)
			i+=1
			line = fileLines[i]
			tfLines.append(line)

			# next line (compare Bus1 winding and nominal voltage)
			i+=1
			line = fileLines[i]
			checkWindingVoltage(line,currentBusList,0)


			# next line (compare Bus2 winding and nominal voltage)
			i+=1
			line = fileLines[i]
			checkWindingVoltage(line,currentBusList,1)

			# next line (compare Bus3 winding and nominal voltage)
			i+=1
			line = fileLines[i]
			checkWindingVoltage(line,currentBusList,2)


			i+=1



with open(newtfData, 'w') as f:
	for line in tfLines:
		f.write(line)
		f.write('\n')





