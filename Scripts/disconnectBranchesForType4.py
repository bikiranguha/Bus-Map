"""
Disconnects all the branches and transformers connected to bus type 4
"""


raw_islanded = 'tmpv2_island.raw'


newRawLines=[] # lines in new raw file
disconnectedBranchLines = [] 
disconnectedtfLines = []
type4BusSet = set() 


def reconstructLine2(words):
	currentLine = ''
	for word in words:
		currentLine += word
		currentLine += ','
	return currentLine[:-1]


# get the bus data and the set of type 4 buses
with open(raw_islanded,'r') as f:
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
		BusType = words[3].strip()
		if BusType == '4':
			type4BusSet.add(Bus)
		
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

	if Bus1 in type4BusSet or Bus2 in type4BusSet:

		if status != '0':
			words[-5] = '0'
			line = reconstructLine2(words)
			disconnectedBranchLines.append(line)


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

	if Bus1 in type4BusSet or Bus2 in type4BusSet:
		status = words[11].strip()
		if status != '0':
			words[11] = '0'
			line = reconstructLine2(words)
			disconnectedtfLines.append(line)

	newRawLines.append(line)

	for j in range(3):
		i+=1
		line = fileLines[i]
		newRawLines.append(line)

	i+=1




# append the remaining data
for i in range(tfEndIndex,len(fileLines)):
	line = fileLines[i]
	newRawLines.append(line)

with open('tmp_island_branch_fixedv2.raw','w') as f:
	f.write('0,   100.00, 33, 1, 1, 60.00     / PSS(R)E-33.3    TUE, DEC 13 2016  22:08')
	f.write('\n')
	f.write('COMED 2018,  HLS18V1, N18S OUTSIDE AND 18 INTCHNG')
	f.write('\n')
	f.write('DYNAMICS REVSION 01')
	f.write('\n')
	for line in newRawLines:
		f.write(line)
		f.write('\n')