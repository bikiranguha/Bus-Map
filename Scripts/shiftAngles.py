# get a list of all buses which need their angles shifted
# get a list of all buses which had their angles shifted manually
# for every bus whose angles were shifted, if they dont appear in the manual change set, incorporate new bus data


directory  = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders'
AngleChangeFile  = directory + '/' +   'AllAngleChangedLines.txt' # all buses which got their phases shifted due to being connected to tf or due to their neighbouring branches
manualChangeFile = directory + '/' + 'manual_changes.txt'
latestRaw = 'tmp_island_branch_fixedv2.raw'
newRawFile = 'tmp_island_branch_fixedv2AngleShifted.raw'

PhaseShiftSet = set() # set of all buses which got their phase shifted
PhaseShiftLinesDict = {} # key: phase shift bus, value: bus data
manualChangeSet = set() # set of buses whose voltage and angles were changed due to manual mapping
newRawLines = []



def reconstructLine2(words):
	currentLine = ''
	for word in words:
		currentLine += word
		currentLine += ','
	return currentLine[:-1]



# get the phase shift info
with open(AngleChangeFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'Log' in line:
			continue

		if line == '':
			continue

		words = line.split(',')

		if len(words) < 3: # should skip any header lines with this one
			continue
		
		Bus = words[0].strip()
		PhaseShiftSet.add(Bus)
		PhaseShiftLinesDict[Bus] = line


# get the set of manual mapping bus set
with open(manualChangeFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if '->' not in line:
			continue
		words = line.split('->')
		CAPEBus = words[1].strip()
		manualChangeSet.add(CAPEBus)

		




"""
for Bus in PhaseShiftSet:
	if Bus in manualChangeSet:
		print Bus
"""
print 'Verified that no overlap exists between the manual changes and the phase shifts'

# Change the bus lines for all the buses which got their phases shifted

with open(latestRaw,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if ('PSS' in line) or ('COMED' in line) or ('DYNAMICS' in line):
		    continue
		if 'END OF BUS DATA' in line:
		    break
		words = line.split(',')
		if len(words)<2: # continue to next iteration of loop if its a blank line
		    continue

		Bus  = words[0].strip()
		BusType = words[3].strip()
		if Bus in PhaseShiftSet: 
			if BusType == '4': # need to change the BusType Data in the new lines
				currentLine = PhaseShiftLinesDict[Bus]
				wordsTemp = currentLine.split(',')
				wordsTemp[3] = '4'
				newLine = reconstructLine2(wordsTemp)
				PhaseShiftLinesDict[Bus] = newLine

			else: # just skip, since Bus type is not important
				continue

		#if Bus in PhaseShiftSet:
		#	continue

		newRawLines.append(line)

	# add the phase shifted bus information
	for Bus in PhaseShiftLinesDict.keys():
		line = PhaseShiftLinesDict[Bus]
		newRawLines.append(line)


# add these two bus lines, for some reason they were missing
newRawLines.append("243083,'05CAMPSS    ', 138.0000,1, 205,1251,   1,1.01145, -55.0773")
newRawLines.append("658082,'MPSSE  7    ', 115.0000,1, 652,1624, 658,1.02055, -45.2697")


busEndIndex = fileLines.index('0 / END OF BUS DATA, BEGIN LOAD DATA')

# append the remaining data in the old raw file
for i in range(busEndIndex, len(fileLines)):
	line = fileLines[i]
	newRawLines.append(line)

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