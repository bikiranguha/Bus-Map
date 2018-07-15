# Now read the latestMapFile in convert3wto2w0seqv2.py to get the new zero seq file with all the 3 winders converted to 2 winders. If the three winder does not appear in the dict, skip it 

""" 
	Script to scan a zero seq file (v30) exported from CAPE and generate a new zero seq file
	where all the three winders have been converted to 2 winders
	The new bus numbers are extracted from the tmap file
"""


# Files to work with
seqFileOrg = 'CAPENewSeq.seq'
#seqFileOrg = 'JQSetv4ExpImp1116.seq'
seqFileNew = 'CAPENewSeqAll2Winder.seq'

#rawFile = 'JQSetv4ExpImp.raw' # The raw file without the 3 winder midpoint buses added
tmapFile = 'latestMapFile.txt'
##########################

newBusDict = {}
keySet = set() # set of 3 winders whose tmaps are there

with open(tmapFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		# header or blank line
		if ',' not in line:
			continue


		words = line.split(',')
		if len(words) <2 :
			continue
		Bus1 = words[0].strip()
		Bus2 = words[1].strip()
		Bus3 = words[2].strip()
		cktID = words[3].strip()
		newBus = words[4].strip()
		key = Bus1 + ',' + Bus2 + ',' + Bus3 + ',' + cktID
		keySet.add(key)
		#print key
		newBusDict[key] = newBus



#newBus = 11000

def convert3wTo2w(lineList,newBusDict, keySet):
	bus1 = lineList[0] # Here lessWords should be passed as cktID
	bus2 = lineList[1]
	bus3 = lineList[2]
	oldcktID = lineList[3]
	zeroBus = ' '*6 + '0' # Since third column is always zero for a 2 winder
	cktID = "'1 '"  # Since we are generating new fictitious buses now
	CC = lineList[4]
	RG1 = lineList[5]
	XG1 = lineList[6]
	R01 = lineList[7]
	X01 = lineList[8]
	R02 = lineList[9]
	X02 = lineList[10]
	R03 = lineList[11]
	X03 = lineList[12]
	largeR = ' 10000000.000000 '  # largeR and largeX are used for CC = 433
	largeX = ' 10000000.000000 '

	lenbus1 = 6
	lenbus2 = 7
	lenbus3 = 7
	lencktID = 5
	lenCC = 4
	lenRG1 = 14
	lenXG1 = 14
	lenR01 = 14
	lenX01 = 14
	lenR02 = 14
	lenX02 = 14
	lenR03 = 14
	lenX03 = 14


	key = bus1.strip() + ',' + bus2.strip() + ',' + bus3.strip() + ',' + oldcktID
	if key not in keySet:
		print key
		return


	FictBus = newBusDict[key]
	
	newBus1 = ' '*(lenbus1-len(bus1)) + bus1
	newBus2 = ' '*(lenbus1-len(bus2)) + bus2
	newBus3 = ' '*(lenbus1-len(bus3)) + bus3
	newFictBus = ' '*(lenbus3-len(FictBus)) + FictBus # Len of FictBus is same as other buses
	newcktID = ' '*(lencktID-len(cktID)) + cktID
	newCC0 = ' '*(lenCC-len(CC[0])) + CC[0]
	newCC1 = ' '*(lenCC-len(CC[1])) + CC[1]
	newCC2 = ' '*(lenCC-len(CC[2])) + CC[2]
	newRG1 = ' '*(lenRG1-len(RG1)) + RG1
	newXG1 = ' '*(lenXG1-len(XG1)) + XG1
	if CC != '433':
		newR01 = ' '*(lenR01-len(R01)) + R01
		newX01 = ' '*(lenX01-len(X01)) + X01
	else:
		newR01 = largeR
		newX01 = largeX
	newR02 = ' '*(lenR02-len(R02)) + R02
	newX02 = ' '*(lenX02-len(X02)) + X02
	newR03 = ' '*(lenR03-len(R03)) + R03
	newX03 = ' '*(lenX03-len(X03)) + X03


	line1 = newBus1 + newFictBus + zeroBus + newcktID + newCC0 + newRG1 + newXG1 + newR01 + newX01 + '\n'
	line2 = newBus2 + newFictBus + zeroBus + newcktID + newCC1 + newRG1 + newXG1 + newR02 + newX02 + '\n'
	line3 = newBus3 + newFictBus + zeroBus + newcktID + newCC2 + newRG1 + newXG1 + newR03 + newX03 + '\n'

	newLine = line1 + line2+ line3
	return newLine













zeroSeq3wList = [] # list of all three winder zero seq data
zeroseq2wList = [] # list of all two winder zero seq data
with open(seqFileOrg,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	zeroSeqTFStart = fileLines.index('0/ End of Zero Sequence Mutual Impedance Data; Begin Zero Sequence Transformer Data') + 1
	zeroSeqTFEnd = fileLines.index('0/ End of Zero-Sequence Transformer data; Begin Area Data')

	for i in range(zeroSeqTFStart,zeroSeqTFEnd):
		line = fileLines[i]
		words = line.split(' ')
		lessWords = [word for word in words if word != '']
		if lessWords[2].strip("'") != '0':
			zeroSeq3wList.append(line)
		else:
			zeroseq2wList.append(line)

# Go through the 3 winder list, and make a new list of two winder conversion
twoWinderLines = []

for line in zeroSeq3wList:
	words = line.split(' ')
	lessWords = [word for word in words if word != '']
	if len(lessWords[3]) == 2:
		lessWords[3] = lessWords[3] + " '"
	else:
		lessWords[3] = lessWords[3] + "'"
	del lessWords[4]
	#CC = lessWords[4]
	#print lessWords[3]

	newLines = convert3wTo2w(lessWords,newBusDict,keySet)
	#exception when tf does not exist in input tmapping
	if newLines == None:
		continue
	twoWinderLines.append(newLines)

# now need to append the two winders to a seq file which contains everything else from the original seq file

with open(seqFileOrg,'r') as f:
	filecontent = f.read()
	splitLine1 = '0/ End of Zero Sequence Mutual Impedance Data; Begin Zero Sequence Transformer Data'
	splitLine2 = '0/ End of Zero-Sequence Transformer data; Begin Area Data'
	fileSplit1 = filecontent.split(splitLine1)
	fileSplit2 = filecontent.split(splitLine2)
	newFilePart1 = fileSplit1[0]
	newFilePart2 = fileSplit2[1]
	fileLines = filecontent.split('\n')

with open(seqFileNew,'w') as f:
	# add everything before zero seq transformer data
	f.write(newFilePart1)
	f.write(splitLine1)
	f.write('\n')
	# add the 2 winder zero seq data
	for tf2 in zeroseq2wList:
		f.write(tf2)
		f.write('\n')
	# add the newly created 2 winder (from 3 winder) zero seq data
	for tf3 in twoWinderLines:
		f.write(tf3)

	# add everything after transformer data
	f.write(splitLine2)
	f.write(newFilePart2)


	
