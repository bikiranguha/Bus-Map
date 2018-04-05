"""
	Script to isolate cases where two adjacent buses (with very low branch impedance) have significant angle impedance
"""

import math


Raw2winder = 'FinalRAW03312018MM2.raw'
#Raw2winder = 'FinalRAW03312018.raw'
new2winderRawFile = 'testRAW04042018.raw' # new raw file with angles changed
HVIssueFile = 'HVIssues.txt' # HV buses which should have angles same (needs to be looked into)


ComedBusSet = set()
BusVoltDict = {}
BusAngleDict = {}
BusAngleOldDict = {} # Original angles for buses which had angles changed 
changeAngleSet = set()
newRawLines = []
HVIssues = [] # HV buses which should have angles same (needs to be looked into)


ZThreshold = 1e-3
AngleThreshold = 1.0


def reconstructLine2(words):
	currentLine = ''
	for word in words:
		currentLine += word
		currentLine += ','
	return currentLine[:-1]



# generate NeighbourDict for branches
with open(Raw2winder, 'r') as f:
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
		BusVolt = float(words[2].strip())
		angle = float(words[8].strip())
		area = words[4].strip()
		#AreaDict[Bus] = area

		if area == '222':
			BusAngleDict[Bus] = angle
			BusVoltDict[Bus] = BusVolt
			ComedBusSet.add(Bus)

branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA') + 1
branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')



troubleSomeLines = [] # lines which have been highlighted by the script

for i in range(branchStartIndex,branchEndIndex):

	line = fileLines[i]

	words = line.split(',')

	Bus1 = words[0].strip()
	Bus2 = words[1].strip()

	if Bus1 in ComedBusSet and Bus2 in ComedBusSet:
		R = float(words[3].strip())
		X = float(words[4].strip())

		Z = math.sqrt(R**2 + X**2)

		AngleDiff = abs(BusAngleDict[Bus1] - BusAngleDict[Bus2])

		if Z < ZThreshold:
			if AngleDiff > AngleThreshold:


				msg = 'Bus1: ' +  Bus1 + ',' + str(BusAngleDict[Bus1]) + ',' +  'Bus2: ' +  Bus2 + ',' + str(BusAngleDict[Bus2]) + ',' + 'Impedance: ' + str(R) + ',' + str(X)
				if BusVoltDict[Bus1] > 138.0:
					#print msg

					HVIssues.append(msg)
				#troubleSomeLines.append(msg)


				# keep a log of the changes
				Bus2Angle = BusAngleDict[Bus2]
				BusAngleOldDict[Bus2] = Bus2Angle
				# change the Bus2 angle to be the same as Bus1
				BusAngleDict[Bus2] = BusAngleDict[Bus1]
				changeAngleSet.add(Bus2)


#
with open(HVIssueFile,'w') as f:
	for line in HVIssues:
		f.write(line)
		f.write('\n')

"""
# keep a log of old issues
with open('tmp.txt','w') as f:
	for line in troubleSomeLines:
		f.write(line)
		f.write('\n')
"""





# reconstruct bus angle data
for line in fileLines:
	if ('PSS' in line) or ('COMED' in line) or ('DYNAMICS' in line):
		continue
	if 'END OF BUS DATA' in line:
		break
	words = line.split(',')
	if len(words) <2:
		continue
	Bus = words[0].strip()

	if Bus in changeAngleSet:
		newAngle = "%.4f" %BusAngleDict[Bus]
		words[8] = ' '*(9-len(newAngle)) +  newAngle

		newline = reconstructLine2(words)
		newRawLines.append(newline)

	else:
		newRawLines.append(line)


# add these two bus lines, for some reason they were missing
newRawLines.append("243083,'05CAMPSS    ', 138.0000,1, 205,1251,   1,1.01145, -55.0773")
newRawLines.append("658082,'MPSSE  7    ', 115.0000,1, 652,1624, 658,1.02055, -45.2697")


busEndIndex = fileLines.index('0 / END OF BUS DATA, BEGIN LOAD DATA')

# append the remaining data in the old raw file
for i in range(busEndIndex, len(fileLines)):
	line = fileLines[i]
	newRawLines.append(line)




with open(new2winderRawFile,'w') as f:
	f.write('0,   100.00, 33, 1, 1, 60.00     / PSS(R)E-33.3    TUE, DEC 13 2016  22:08')
	f.write('\n')
	f.write('COMED 2018,  HLS18V1, N18S OUTSIDE AND 18 INTCHNG')
	f.write('\n')
	f.write('DYNAMICS REVSION 01')
	f.write('\n')
	for line in newRawLines:
		f.write(line)
		f.write('\n')