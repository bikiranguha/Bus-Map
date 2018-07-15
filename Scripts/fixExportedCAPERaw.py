"""
Convert the exported raw file in CAPE to the one we used to generate the donut hole raw file:
	Add the new buses which represent fict tf midpoints (11000-11004, 100000-100013)
	Change branch impedance from MVA base of 300 to 100 MVA
	Change the tf data as detailed in CAPETFChanges.txt

"""

from writeFileFn import writeToFile

def reconstructLine2(words):
	currentLine = ''
	for word in words:
		currentLine += word
		currentLine += ','
	return currentLine[:-1]


originalCAPERaw = 'MASTER - CAPE File 8-17-2016v33.raw' # exported from CAPE database and converted to version 33
fixedCAPERaw = 'MASTER_CAPE_Fixed.raw' # raw file after changes applied
newlyIncludedBusFile = 'newCAPEBusData.txt' # bus data to be included in the modified raw file
tfChangeFile = 'CAPETFChanges.txt' # CAPE file which details all the tf changes
tfToSkipSet = set() # 3 winders to not add from the exported raw file
#FourWinderDataToAddLines = []
#ManualFictMidptSet = set()

# self explanatory lists
tfDataToAddLines = [] 
newRawLines = []
newlyIncludedBusLines = [] 
#####

# get the newly included bus data
with open(newlyIncludedBusFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

for line in fileLines:
	if line == '':
		continue
	newlyIncludedBusLines.append(line)

# get the tf changes
with open(tfChangeFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')


tMapStartIndex = fileLines.index('Three winder to two winder conversions:') + 1
tfAddStartIndex = fileLines.index('TF Data to add from CAPERaw_0228v3:') + 1

# get the tf to skip set as well as the manual fict midpoint set
for i in range(tMapStartIndex,tfAddStartIndex):
	line = fileLines[i]
	if '->' not in line:
		continue
	words = line.split('->')
	LHS = words[0]
	RHS = words[1]
	tfToSkipSet.add(LHS)
	#ManualFictMidptSet.add(RHS.strip())

# tf lines to add at the end of the tf data
for i in range(tfAddStartIndex,len(fileLines)):
	line = fileLines[i]
	if line == '':
		continue
	tfDataToAddLines.append(line)



# start generating the new raw lines by looking at the previous bus lines
with open(originalCAPERaw, 'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')


# change header so that it says the system MVA base is 100, instead of 300
header = '0,   100.00, 33, 0, 1, 60.00     / PSS(R)E-33.3    SUN, JUL 01 2018  10:49'
newRawLines.append(header)


busEndIndex = fileLines.index('0 / END OF BUS DATA, BEGIN LOAD DATA')
branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA') + 1
branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')

tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')

# add bus data, skipping the header
for i in range(1,busEndIndex):
	line  = fileLines[i]
	newRawLines.append(line)

# add the newly included bus data in CAPERaw0228v3.raw
for line in newlyIncludedBusLines:
	#line  = fileLines[i]
	newRawLines.append(line)	


# get everything from end of bus data till branch data
for i in range(busEndIndex,branchStartIndex):
	line  = fileLines[i]
	newRawLines.append(line)


# change MVA base in branch data and add
for i in range(branchStartIndex, branchEndIndex):
	line = fileLines[i]
	words = line.split(',')
	#Bus1 = words[0].strip()
	#Bus2 = words[1].strip()
	R = float(words[3].strip())
	X = float(words[4].strip())

	NewR = R/3

	NewRStr = '%.5E' % NewR
	NewX = X/3
	NewXStr = '%.5E' % NewX

	words[3] = NewRStr.rjust(12)
	words[4] = NewXStr.rjust(12)

	line = reconstructLine2(words)
	newRawLines.append(line)


newRawLines.append('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')


# get all the tf data except for the ones to skip
i = tfStartIndex
while i < tfEndIndex:
	line = fileLines[i]
	skipTF = 0
	# see if the line contains any tf skip id, then skip 5 lines
	for tf in list(tfToSkipSet):
		if tf in line:
			skipTF = 1
			break

	if skipTF == 1:
		i+=5
	else:
		newRawLines.append(line)
		i+=1

# add all the new tf data
for line in tfDataToAddLines:
	newRawLines.append(line)

for i in range(tfEndIndex,len(fileLines)):
	line = fileLines[i]
	newRawLines.append(line)
"""
for i in range(tfStartIndex,tfEndIndex):
	line = fileLines[i]


for i in range(tfEndIndex,len(fileLines)):
	line = fileLines[i]
	newRawLines.append(line)



# change MVA base in tf data if necessary
newRawLines.append('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')
i = tfStartIndex
while i < tfEndIndex:
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	Bus3 = words[2].strip()
	CZ = words[5].strip()

	# checked that all the tf in the raw file have CZ = 2, so no need to change tf impedance
	if Bus3 == '0':
		if CZ != '2':
			print line
		i+=4

	else:
		if CZ != '2':
			print line
		i+=5
	
"""




writeToFile(fixedCAPERaw,newRawLines,'')

