# apply manual bus mappings and bus disconnections in given file

changeFile = 'manualChangesFile.txt'
planningRaw = 'hls18v1dyn_new.raw'
CAPERaw = 'tmp_island_branch_fixedv2AngleShifted.raw'
newRawFile  = 'Raw0414tmp.raw'

ManualMapDict = {} # key: planningBus whose bus volt and angle to substitute, value: CAPEBus whose bus volt and angle will be substituted
planningBusSet = set() # set of all planning buses whose bus data will be used for substitution
CAPEBusVoltSet = set() # set of all CAPE buses whose bus data will be substituted
CAPEBusDisconnectSet = set() # set of CAPE buses which will be disconnected
CAPENewVoltDict = {} # key: CAPEBus whose bus volt and angle will be substituted, value: new volt and angle data
newRawLines = []
currentBusSet = set() # set of all buses in the newRawFile

def reconstructLine2(words):
	currentLine = ''
	for word in words:
		currentLine += word
		currentLine += ','
	return currentLine[:-1]




# open the file which contains the list of manual changes necessary
with open(changeFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

busMapStartIndex = fileLines.index('Change in bus mapping:') +1
busMapEndIndex = fileLines.index('Disconnect Bus (due to the fact that they are mapped to disconnected bus):')

# get the bus substitution data
for i in range(busMapStartIndex,busMapEndIndex):
	line = fileLines[i]
	if line == '':
		continue

	words = line.split('->')
	if len(words) <2:
		continue
	planningBus = words[0].strip()
	CAPEBus = words[1].strip()
	ManualMapDict[planningBus] = CAPEBus 
	planningBusSet.add(planningBus)
	CAPEBusVoltSet.add(CAPEBus)

# get the bus disconnect data
for i in range(busMapEndIndex,len(fileLines)):
	line = fileLines[i]

	if line == '':
		continue

	CAPEBusDisconnectSet.add(line.strip())

# get the planning bus data to be substituted
with open(planningRaw,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split("\n")
	for line in fileLines:
		if ('PSS' in line) or ('COMED' in line) or ('DYNAMICS' in line):
			continue
		if 'END OF BUS DATA' in line:
			break
		words = line.split(',')
		if len(words)<2: # continue to next iteration of loop if its a blank line
			continue

		Bus = words[0].strip()

			
		if Bus in planningBusSet:
			Vmag = words[7]
			Vang = words[8]
			CAPEBus = ManualMapDict[Bus]
			CAPENewVoltDict[CAPEBus] = [Vmag, Vang]



# generate the new raw file data
with open(CAPERaw,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	# reconstruct bus status
	for line in fileLines:
		if ('PSS' in line) or ('COMED' in line) or ('DYNAMICS' in line):
			continue
		if 'END OF BUS DATA' in line:
			break
		words = line.split(',')
		if len(words) <2:
			continue
		Bus = words[0].strip()

		if Bus in currentBusSet: 
			# in CAPERaw, there are several buses which appear twice. This gets rid of that problem
			continue
		else:
			currentBusSet.add(Bus)

		if Bus in CAPEBusVoltSet:
			NewVoltageData = CAPENewVoltDict[Bus]
			words[7] = NewVoltageData[0] # pu volt substitution
			words[8] = NewVoltageData[1]
			newline = reconstructLine2(words)
			newRawLines.append(newline)

		elif Bus in CAPEBusDisconnectSet:
			words[3] = '4'
			newline = reconstructLine2(words)
			newRawLines.append(newline)			

		else:
			newRawLines.append(line)

# add these two bus lines, for some reason they were missing
newRawLines.append("243083,'05CAMPSS    ', 138.0000,1, 205,1251,   1,1.01145, -55.0773")
newRawLines.append("658082,'MPSSE  7    ', 115.0000,1, 652,1624, 658,1.02055, -45.2697")

busEndIndex = fileLines.index('0 / END OF BUS DATA, BEGIN LOAD DATA')

branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA') + 1
branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')


# add anything between end of bus data and beginning of branch data
for i in range(busEndIndex,branchStartIndex):
	line = fileLines[i]
	newRawLines.append(line)

# disconnect all type 4 bus branches
for i in range(branchStartIndex,branchEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	status = words[-5].strip()

	if Bus1 in CAPEBusDisconnectSet or Bus2 in CAPEBusDisconnectSet:
		if status != '0':
			words[-5] = '0'
			line = reconstructLine2(words)

	newRawLines.append(line)

newRawLines.append('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')


tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')


# disconnect all transformers connected to type 4 buses
i = tfStartIndex
while i < tfEndIndex:
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()

	if Bus1 in CAPEBusDisconnectSet or Bus2 in CAPEBusDisconnectSet:
		status = words[11].strip()
		if status != '0':
			words[11] = '0'
			line = reconstructLine2(words)

	newRawLines.append(line)

	for j in range(3):
		i+=1
		line = fileLines[i]
		newRawLines.append(line)

	i+=1


# append remaining lines
for i in range(tfEndIndex,len(fileLines)):
	line = fileLines[i]
	newRawLines.append(line)


# output the new raw data
with open(newRawFile,'w') as f:
	f.write('0,   100.00, 33, 1, 1, 60.00     / PSS(R)E-33.3    TUE, DEC 13 2016  22:08')
	f.write('\n')
	f.write('COMED 2018,  HLS18V1, N18S OUTSIDE AND 18 INTCHNG')
	f.write('\n')
	f.write('DYNAMICS REVSION 01')
	f.write('\n')
	for line in newRawLines:
		f.write(line)
		f.write('\n')

# keep track of the updates in the bus mapping, see if you can implement in mapped_buses.csv