# look at tfLVBusSet and make a set of buses which belong to ring buses
# these buses should have neighbours within a depth of 2 buses which are on the LV side of a transformer connecting to the HV side
# if any of the buses have generic voltages (1.0 v with angles of 0.0 or 30.0 or -30.0), then we need to map them properly

from disconnectLVbusesv2 import tfLVBusSet, disconnectSet, BusVoltpuDict, BusAngleDict
from generateNeighbours_Disconnect import BranchConnDict, tfConnDict
from disconnectBranchesForType4 import disconnectedBranchLines, disconnectedtfLines

oldRawFile = 'Raw0414tmp.raw'
newRawFile = 'Raw0419_reen.raw'

#ParentDict = {} # dict to help keep track of paths to energize
energizeSet = set() # set of buses to turn back on
#exploredtfLVset = set()
newRawLines = []



def reconstructLine2(words):
	currentLine = ''
	for word in words:
		currentLine += word
		currentLine += ','
	return currentLine[:-1]


# get the required set
for bus in tfLVBusSet:
	if bus in BranchConnDict.keys():
		#exploredtfLVset.add(bus)  # this bus does not qualify as an end-point anymore for another bus in tfLVBusSet
		neighbourdepth1 = BranchConnDict[bus]  # get branches 
		for n in neighbourdepth1: # for each branch neighbour
			#ParentDict[n] = bus
			#if n in tfLVBusSet and n not in exploredtfLVset:
			#	energizeSet.add(n)

			neighbourdepth2 = BranchConnDict[n] # depth 2

			for n2 in neighbourdepth2:

				#ParentDict[n2] = n
				if n2 in tfLVBusSet and n2 != bus: 
					if n in disconnectSet: # had been disconnected before
						energizeSet.add(n) # add the depth 1 neighbour since it was disconnected earlier
						if BusVoltpuDict[n] == 1.0 and BusAngleDict[n] in [0.0,30.0,-30.0]: # buses having data which need to be fixed
							print n

					# depth 3, ignoring for now
					"""
					neighbourdepth3 = BranchConnDict[n2]
					for n3 in neighbourdepth3:
						if n3 in tfLVBusSet and n3 != n:
							if n2 in disconnectSet:
								energizeSet.add(n)

							if n in disconnectSet:
								energizeSet.add(n)
					"""

# this set consists of energizeSet and tfLVBusSet
relevantSet  = set(energizeSet)
relevantSet.update(tfLVBusSet)


with open(oldRawFile,'r') as f:
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

		if Bus in energizeSet:

			words[3] = '1'
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

# energize all the branches belonging to buses in energizeSet
for i in range(branchStartIndex,branchEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	status = words[-5].strip()

	if Bus1 in relevantSet and Bus2 in relevantSet: # the branch needs to have relevant buses (see relevantSet) on both side
		if line in disconnectedBranchLines: # branch was disconnected in disconnectBranchesForType4
			words[-5] = '1'
			line = reconstructLine2(words)

	newRawLines.append(line)

newRawLines.append('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')


tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')


# energize all the transformers belonging to buses in relevantSet
i = tfStartIndex
while i < tfEndIndex:
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()

	if Bus1 in relevantSet and Bus2 in relevantSet: # the tf needs to have relevant buses (see relevantSet) on both side
		if line in disconnectedtfLines: # tf was disconnected in disconnectBranchesForType4
			words[11] = '1'
			line = reconstructLine2(words)

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

# generate new raw file
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