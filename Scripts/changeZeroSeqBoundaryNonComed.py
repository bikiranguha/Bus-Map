"""
	Get boundary non-comed mapping (CAPE to planning) and substitute the CAPE non-comed bus numbers with the planning bus numbers
"""

def writeLines(lineList):
	for line in lineList:
		f.write(line)
		f.write('\n')
# Files to work with
seqFileOrg = 'CAPENewSeqAll2Winder.seq' # org seq file with all the renumbering done, as well as the 3 winder to 2 winder conversion done
seqFileNew = 'CAPENewSeqAll2WinderBoundaryFixed.seq' # boundary non-comed buses are changed to planning bus numbers

BoundaryMapFile = 'BoundaryMapHemanth_0626.txt'
BoundaryMapDict = {}

newBranchLines = []
newMutualZLines = []
beforeBranchLines = []
aftermutualZLines = []
# get the boundary maps
with open(BoundaryMapFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		# header or blank line
		if '->' not in line:
			continue
		words = line.split('->')
		CAPESide = words[0]
		planningSide = words[1]

		BoundaryMapDict[CAPESide] = planningSide




# change the data
with open(seqFileOrg,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')


branchStartIndex = fileLines.index("0/ End of Zero Sequence Shunt Loads Data; Start zero sequence branch data") + 1
branchEndIndex = fileLines.index("0/ End of Zero Sequence Nontransformer Branch Data")

# get everything from start till branch data starts

for i in range(branchStartIndex):
	line = fileLines[i]
	beforeBranchLines.append(line)

# zero seq line data
for i in range(branchStartIndex, branchEndIndex):
	line = fileLines[i]
	#words = line.split(',')
	branchID = line[:18]
	RestOfLine = line[18:]

	if branchID in BoundaryMapDict.keys():
	#	print branchID
		newBranchID = BoundaryMapDict[branchID]

		newLine = newBranchID + RestOfLine
		print newLine
		newBranchLines.append(newLine)
	else:
		newBranchLines.append(line)



mutualZStartIndex = fileLines.index("0/ End of Zero Sequence Nontransformer Branch Data") + 1
mutualZEndIndex = fileLines.index("0/ End of Zero Sequence Mutual Impedance Data; Begin Zero Sequence Transformer Data")
for i in range(mutualZStartIndex, mutualZEndIndex):
	line = fileLines[i]
	fromSide = line[:18]
	toSide = line[19:19+18]

	newfromSide = fromSide
	newtoSide = toSide
	RestOfLine = line[19+18:]

	if fromSide in BoundaryMapDict.keys():
		newfromSide = BoundaryMapDict[fromSide]
	if toSide in BoundaryMapDict.keys():
		newtoSide = BoundaryMapDict[toSide]

	newLine = newfromSide + ',' + newtoSide + RestOfLine
	#if fromSide in BoundaryMapDict.keys() or toSide in BoundaryMapDict.keys():
	#	print newLine
	newMutualZLines.append(newLine)


for i in range(mutualZEndIndex,len(fileLines)):
	line = fileLines[i]
	aftermutualZLines.append(line)	




with open(seqFileNew,'w') as f:
	writeLines(beforeBranchLines)
	#f.write('\n')

	writeLines(newBranchLines)
	f.write("0/ End of Zero Sequence Nontransformer Branch Data")
	f.write('\n')

	writeLines(newMutualZLines)
	#f.write('\n')

	writeLines(aftermutualZLines)





"""
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	if Bus1 in changeOldToNewDict.keys():
		newBus1 = changeOldToNewDict[Bus1]
		words[0] = ' '*(6-len(newBus1)) + newBus1

	if Bus2 in changeOldToNewDict.keys():
		newBus2 = changeOldToNewDict[Bus2]
		words[1] = ' '*(6-len(newBus2)) + newBus2

	line = reconstructLine2(words)
	newBranchLines.append(line)

# mutual impedance data
newMutualZLines = []
mutualZStartIndex = fileLines.index("0/ End of Zero Sequence Nontransformer Branch Data") + 1
mutualZEndIndex = fileLines.index("0/ End of Zero Sequence Mutual Impedance Data; Begin Zero Sequence Transformer Data")

for i in range(mutualZStartIndex, mutualZEndIndex):
	line = fileLines[i]
	words = line.split(',')
	# From end buses
	Bus1F = words[0].strip()
	Bus2F = words[1].strip()

	if Bus1F in changeOldToNewDict.keys():
		newBus1F = changeOldToNewDict[Bus1F]
		words[0] = ' '*(6-len(newBus1F)) + newBus1F

	if Bus2F in changeOldToNewDict.keys():
		newBus2F = changeOldToNewDict[Bus2F]
		words[1] = ' '*(6-len(newBus2F)) + newBus2F


	# From end buses
	Bus1T = words[3].strip()
	Bus2T = words[4].strip()

	if Bus1T in changeOldToNewDict.keys():
		newBus1T = changeOldToNewDict[Bus1T]
		words[3] = ' '*(6-len(newBus1T)) + newBus1T

	if Bus2T in changeOldToNewDict.keys():
		newBus2T = changeOldToNewDict[Bus2T]
		words[4] = ' '*(6-len(newBus2T)) + newBus2T

	line = reconstructLine2(words)
	newMutualZLines.append(line)

"""