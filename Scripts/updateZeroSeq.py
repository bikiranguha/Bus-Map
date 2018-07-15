"""
Does the re-numbering of the CAPE comed buses in the zero seq file. Includes buses which were changed coz of generator or becoz of merging conflicts
"""

changeLog = 'changeBusNoLog.txt'
changeOldToNewDict = {}
oldZeroSeq = 'CAPERaw.seq'
newSeqFile = 'CAPENewSeq.seq'

def reconstructLine2(words):
	currentLine = ''
	for word in words:
		currentLine += word
		currentLine += ','
	return currentLine[:-1]



def writeLines(lineList):
	for line in lineList:
		f.write(line)
		f.write('\n')

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
		changeOldToNewDict[OldBus] = NewBus

with open(oldZeroSeq,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

# pos seq gen data
newPosSeqGenLines = []
positiveSeqGenStartIndex = fileLines.index("0          / Tue Feb 28 19:13:11 2017") + 1
positiveSeqGenEndIndex = fileLines.index("0/ End of Positive Sequence Generator Data")

for i in range(positiveSeqGenStartIndex, positiveSeqGenEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus = words[0].strip()
	if Bus in changeOldToNewDict.keys():
		newBus = changeOldToNewDict[Bus]
		words[0] = ' '*(6-len(newBus)) + newBus
		nLine = reconstructLine2(words)
		newPosSeqGenLines.append(nLine)
	else:
		newPosSeqGenLines.append(line)

# neg seq gen data
newNegSeqLines = []
negativeSeqGenStartIndex = fileLines.index("0/ End of Positive Sequence Generator Data") + 1
negativeSeqGenEndIndex = fileLines.index("0/ End of Negative Sequence Generator Data")

for i in range(negativeSeqGenStartIndex, negativeSeqGenEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus = words[0].strip()
	if Bus in changeOldToNewDict.keys():
		newBus = changeOldToNewDict[Bus]
		words[0] = ' '*(6-len(newBus)) + newBus
		nLine = reconstructLine2(words)
		newNegSeqLines.append(nLine)
	else:
		newNegSeqLines.append(line)

# zero seq gen data
newZeroSeqLines = []
zeroSeqGenStartIndex = fileLines.index("0/ End of Negative Sequence Generator Data") + 1
zeroSeqGenEndIndex = fileLines.index("0/ End of Zero Sequence Generator Data")

for i in range(zeroSeqGenStartIndex, zeroSeqGenEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus = words[0].strip()
	if Bus in changeOldToNewDict.keys():
		newBus = changeOldToNewDict[Bus]
		words[0] = ' '*(6-len(newBus)) + newBus
		nLine = reconstructLine2(words)
		newZeroSeqLines.append(nLine)
	else:
		newZeroSeqLines.append(line)


# zero seq shunt data
newShuntLines = []
shuntStartIndex = fileLines.index("0/ End of Negative-Sequence Shunt-Load Data; start Zero-Sequence Shunt-Load Data") + 1
shuntEndIndex = fileLines.index("0/ End of Zero Sequence Shunt Loads Data; Start zero sequence branch data")

for i in range(shuntStartIndex, shuntEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus = words[0].strip()
	if Bus in changeOldToNewDict.keys():
		newBus = changeOldToNewDict[Bus]
		words[0] = ' '*(6-len(newBus)) + newBus
		nLine = reconstructLine2(words)
		newShuntLines.append(nLine)
	else:
		newShuntLines.append(line)


# zero seq line data
newBranchLines = []
branchStartIndex = fileLines.index("0/ End of Zero Sequence Shunt Loads Data; Start zero sequence branch data") + 1
branchEndIndex = fileLines.index("0/ End of Zero Sequence Nontransformer Branch Data")

for i in range(branchStartIndex, branchEndIndex):
	line = fileLines[i]
	words = line.split(',')
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

# zero seq transformer data
newTFLines = []
tfStartIndex = fileLines.index("0/ End of Zero Sequence Mutual Impedance Data; Begin Zero Sequence Transformer Data") + 1
tfEndIndex = fileLines.index("0/ End of Zero-Sequence Transformer data; Begin Area Data")

for i in range(tfStartIndex, tfEndIndex):
	line = fileLines[i]
	#words = line.split(',')
	Bus1 = line[:6]
	Bus2 = line[7:13]
	Bus3 = line[14:20]
	RestOfLine = line[20:]


	if Bus1.strip() in changeOldToNewDict.keys():
		Bus1 = changeOldToNewDict[Bus1.strip()]
		Bus1 = ' '*(6-len(Bus1)) + Bus1

	if Bus2.strip() in changeOldToNewDict.keys():
		Bus2 = changeOldToNewDict[Bus2.strip()]
		Bus2 = ' '*(6-len(Bus2)) + Bus2

	if Bus3.strip() in changeOldToNewDict.keys():
		Bus3 = changeOldToNewDict[Bus3.strip()]
		Bus3 = ' '*(6-len(Bus3)) + Bus3

	line = Bus1 + ' ' + Bus2 + ' ' + Bus3 + RestOfLine
 
	newTFLines.append(line)





# print new seq file
with open(newSeqFile,'w') as f:
	f.write("0          / Tue Feb 28 19:13:11 2017")
	f.write('\n')

	writeLines(newPosSeqGenLines)
	f.write("0/ End of Positive Sequence Generator Data")
	f.write('\n')

	writeLines(newNegSeqLines)
	f.write("0/ End of Negative Sequence Generator Data")
	f.write('\n')

	writeLines(newZeroSeqLines)
	f.write("0/ End of Zero Sequence Generator Data")
	f.write('\n')
	f.write("0/ End of Negative-Sequence Shunt-Load Data; start Zero-Sequence Shunt-Load Data")
	f.write('\n')

	writeLines(newShuntLines)
	f.write("0/ End of Zero Sequence Shunt Loads Data; Start zero sequence branch data")
	f.write('\n')

	writeLines(newBranchLines)
	f.write("0/ End of Zero Sequence Nontransformer Branch Data")
	f.write('\n')

	writeLines(newMutualZLines)
	f.write("0/ End of Zero Sequence Mutual Impedance Data; Begin Zero Sequence Transformer Data")
	f.write('\n')

	writeLines(newTFLines)
	f.write("0/ End of Zero-Sequence Transformer data; Begin Area Data")
	f.write('\n')

	f.write("0/ End of Zero Sequence Switched Shunt Data")
	f.write('\n')
	f.write("0/ End of Zero Sequence Fixed Shunt Data")

