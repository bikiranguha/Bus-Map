rawfile = 'CAPE_RAW1116v33.raw'

newrawFile = 'CAPE_RAW0225v33.raw'

newBranchLines = []

with open(rawfile,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split('\n')

# get branch start and end indices
for line in fileLines:
    if 'END OF GENERATOR DATA' in line:
        branchStartIndex = fileLines.index(line) + 1
    if 'END OF BRANCH DATA' in line:
        branchEndIndex = fileLines.index(line)


# change branch data
for i in range(branchStartIndex, branchEndIndex):
	line = fileLines[i]
	words = line.split(',')
	R = float(words[3].strip())/3
	X = float(words[4].strip())/3

	Rstr = '%.5E' %R
	Xstr = '%.5E' %X

	words[3] = ' ' + Rstr
	words[4] = ' ' + Xstr
	newLine = ''
	for word in words:
		newLine += word
		newLine += ','
	newLine = newLine[:-1] 

	newBranchLines.append(newLine)


# change transformer data
for line in fileLines:
    if 'END OF BRANCH DATA' in line:
        tfStartIndex = fileLines.index(line) + 1
    if 'END OF TRANSFORMER DATA' in line:
        tfEndIndex = fileLines.index(line)

i = tfStartIndex 

newtfLines = []
while i < tfEndIndex:
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	Bus3 = words[2].strip()
	newtfLines.append(line)
	if Bus3 == '0': # two winder
		i+=1
		RXLine = fileLines[i]
		RXwords = RXLine.split(',')
		# get relevant values and change them
		R12 = float(RXwords[0].strip())/3
		X12 = float(RXwords[1].strip())/3

		R12str = '%.5E' %R12
		X12str = '%.5E' %X12

		RXwords[0] = ' ' + R12str
		RXwords[1] = ' ' + X12str
		# re-construct the line
		newLine = ''
		for word in RXwords:
			newLine += word
			newLine += ','
		newLine = newLine[:-1]

		newtfLines.append(newLine)

		# get the remaining lines
		for j in range(2):
			i+=1
			line = fileLines[i]
			newtfLines.append(line)
		i+=1
	
	else: # three winder
		i+=1
		RXLine = fileLines[i]
		RXwords = RXLine.split(',')
		# get relevant values and change them
		R12 = float(RXwords[0].strip())/3
		X12 = float(RXwords[1].strip())/3

		R23 = float(RXwords[3].strip())/3
		X23 = float(RXwords[4].strip())/3

		R31 = float(RXwords[6].strip())/3
		X31 = float(RXwords[7].strip())/3

		R12str = '%.5E' %R12
		X12str = '%.5E' %X12

		R23str = '%.5E' %R23
		X23str = '%.5E' %X23

		R31str = '%.5E' %R31
		X31str = '%.5E' %X31

		RXwords[0] = ' ' + R12str
		RXwords[1] = ' ' + X12str

		RXwords[3] = ' ' + R23str
		RXwords[4] = ' ' + X23str

		RXwords[6] = ' ' + R31str
		RXwords[7] = ' ' + X31str

		# re-construct the line
		newLine = ''
		for word in RXwords:
			newLine += word
			newLine += ','
		newLine = newLine[:-1]

		newtfLines.append(newLine)

		# get the remaining lines
		for j in range(3):
			i+=1
			line = fileLines[i]
			newtfLines.append(line)
		i+=1








with open(newrawFile,'w') as f:
	# change MVA info in the first line
	f.write('0,   100.00, 33, 0, 1, 60.00     / PSS(R)E-33.3    TUE, JAN 30 2018  17:47')
	f.write('\n')
	# write data from start till start of branch data
	for i in range(1,branchStartIndex):
		line = fileLines[i]
		f.write(line)
		f.write('\n')
	# write new branch data
	for line in newBranchLines:
		f.write(line)
		f.write('\n')
	
	# write lines between branch and transformer data
	for i in range(branchEndIndex,tfStartIndex):
		line = fileLines[i]
		f.write(line)
		f.write('\n')

	# write new branch data
	for line in newtfLines:
		f.write(line)
		f.write('\n')	

	#write rest of data
	for i in range(tfEndIndex,len(fileLines)):
		line = fileLines[i]
		f.write(line)
		f.write('\n')


