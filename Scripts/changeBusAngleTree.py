"""
	Script to implement BFS to shift bus angles of all neighbours of original buses which had their angles shifted
"""

from Queue import Queue
import shutil
import correctAngles # correct the bus phase shifts in FinalRaw03272018.raw (wrong due to opposite phase shift direction earlier)

busAngleChangeLog = 'newBusAngles.txt' # file containing changed bus angle list
angleChangeFile = 'logAngleChange.txt' # file containing bus angle changes
CAPERaw = 'NewCAPERawClean.raw' # to be consistent with the raw file used in change3winderDatav14
toChangeAnglesFile = 'toChangeAngles.txt' # file which contains all the new bus data whose angles need to change
AllAnglesChangeFile =  'AllAngleChangedLines.txt' # contains all the buses which got their angles changed
traceBackFile = 'traceback.txt' # file used to trace back the angle change (from child to parent)
#AllBusFileOld = 'AllMappedBusDataIter2.txt'  # File containing the bus data (old)
#AllBusFileNew = 'AllMappedBusDataIter3.txt' # Latest bus data file
old2winderRawFile = 'FinalRAW03272018.raw'
new2winderRawFile = 'FinalRAW03312018.raw'

HVShiftSet = set() # set of HV bus which have phase shifts
originalAngleChangeSet = set() # set of all buses which have their angles changed, also a list of 
BusVoltDict = {} # key: bus voltage, value: Bus voltage
AngleChangeDict = {} # key: bus, value: angle change
BranchConnDict = {} # key: CAPE comed bus, value: neighbour branches
#TFConnDict = {}
AreaDict = {} # key: bus, value: area code
ParentDict = {} # key: child node in BFS algorithm, value: parent node in BFS algorithm
newAngleChangeLines = [] # list of new bus data, whose angles are going to be changed here
NoAngleChangeBusLines = [] # Data of buses which do not have any angles changed
toChangeAngles = [] # list of bus (along with bus data) which needs angles changed
newRawLines = [] # lines of new raw file
#### Functions

def getPhaseShifts(i, fileLines, Bus3):
	#get original tf phase shifts, to be added in to new 2 winders
	PSList = [] # ordered as primary, secondary and tertiary
	
	if Bus3 != '0': # three winder
		i+=2 #skip this line and the next line

		line = fileLines[i]
		words = line.split(',')
		PS = words[2].strip()
		PSList.append(float(PS))

		i+=1
		line = fileLines[i]
		words = line.split(',')
		PS = words[2].strip()
		PSList.append(float(PS))

		i+=1
		line = fileLines[i]
		words = line.split(',')
		PS = words[2].strip()
		PSList.append(float(PS))
	else: # two winder
		i+=2 #skip this line and the next line
		line = fileLines[i]
		words = line.split(',')
		PS = words[2].strip()
		PSList.append(float(PS))


	return PSList

def BusAppend(Bus,NeighbourBus,NeighbourDict):
	if Bus not in NeighbourDict.keys():
		NeighbourDict[Bus] = set()
	NeighbourDict[Bus].add(NeighbourBus)

def reconstructLine2(words):
	currentLine = ''
	for word in words:
		currentLine += word
		currentLine += ','
	return currentLine[:-1]
#############################



# Read the set of buses which had phases shifted
with open(busAngleChangeLog,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	originalAngleChangeLines = list(fileLines)
	for line in fileLines:
		if 'Log' in line:
			continue

		if line == '':
			continue

		words = line.split(',')
		Bus = words[0].strip()
		BusVolt = float(words[2].strip())
		originalAngleChangeSet.add(Bus)


		
		if BusVolt >=69.00: # if a HV bus got its angle shifted
			print 'Alert, HV bus has phase shift: ', Bus
			HVShiftSet.add(Bus)
			pass
			#print line
		



# Read the angle change values and generate a dict
with open(angleChangeFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'Bus' in line:
			continue

		if line == '':
			continue

		words = line.split('->')
		Bus = words[0].strip()
		Angle = float(words[1].strip()) 

		if Angle == 0.0: # Add to dictionary only if there is a phase shift
			print Bus
			continue
		
		AngleChangeDict[Bus] = Angle





# generate NeighbourDict for branches
with open(CAPERaw, 'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if ('PSS' in line) or ('COMED' in line):
			continue
		if 'END OF BUS DATA' in line:
			break
		words = line.split(',')
		if len(words) <2:
			continue
		Bus = words[0].strip()
		BusVolt = float(words[2].strip())
		area = words[4].strip()
		AreaDict[Bus] = area
		BusVoltDict[Bus] = BusVolt


	branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA') + 1
	branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')

	for i in range(branchStartIndex, branchEndIndex):
		line = fileLines[i]
		words = line.split(',')
		Bus1 = words[0].strip()
		Bus2 = words[1].strip()
		status = words[-5].strip()

		try:
			if AreaDict[Bus1] == '222' and AreaDict[Bus2] == '222' and status == '1':
				BusAppend(Bus1,Bus2,BranchConnDict)
				BusAppend(Bus2,Bus1,BranchConnDict)
		except:
			#print line # two lines were giving trouble, but they are outside the comed region, so ignore
			pass

	


	# Note: In any case where a HV bus gets phase shifted, the other bus voltage < 138 kV
	#		All the HV phase shifts occur in two winders, not in 3 winders
	"""
	# check if HV phase shifts occur on tf where the other bus is also >= 138 kV
	tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
	tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')
	i = tfStartIndex
	while i < tfEndIndex:
		line = fileLines[i]
		words = line.split(',')
		Bus1 = words[0].strip()
		Bus2 = words[1].strip()
		Bus3 = words[2].strip()

		PSList = getPhaseShifts(i, fileLines, Bus3)

		if Bus3 == '0': # two winder
			if Bus1 in HVShiftSet:
				if PSList[0] != 0.0:
					if BusVoltDict[Bus2] >= 138.00:
						print Bus2

			if Bus2 in HVShiftSet:
				if PSList[0] != 0.0:
					if BusVoltDict[Bus1] >= 138.00:
						print Bus1

			i+=4

		else: # three winder
			if Bus1 in HVShiftSet:
				if PSList[0] != 0.0:
					print Bus1

			if Bus2 in HVShiftSet:
				if PSList[1] != 0.0:
					print Bus2

			if Bus3 in HVShiftSet:
				if PSList[2] != 0.0:
					print Bus3

			i+=5
	########################
	"""





# start the BFS search of changing bus angles


frontier = Queue(maxsize=0)
explored = set() # set of all buses which need angles changed (including original buses which have their angles changed already)

# put all the original phase shift buses in frontier
for bus in list(originalAngleChangeSet):
	frontier.put(bus)

# put buses in explored if they belong to originalAngleChangeSet or connected to them via branches
while not frontier.empty():
	currentBus =  frontier.get()
	frontier.task_done()
	if currentBus not in BranchConnDict.keys(): # bus has no branch connections
		continue

	NeighbourBus = BranchConnDict[currentBus]
	if currentBus not in explored:
		explored.add(currentBus)
		if currentBus not in AngleChangeDict.keys(): # add angle shift values if not already done for the bus
			AngleChangeDict[currentBus] = AngleChangeDict[ParentDict[currentBus]]

	for neighbour in NeighbourBus:
		if neighbour not in originalAngleChangeSet:
				if neighbour not in explored:
					if neighbour not in ParentDict.keys():
						# Helps to keep track of the value of angle change
						ParentDict[neighbour] = currentBus

					frontier.put(neighbour)
		"""
		# check to see if the phase shifts are close to neighbouring buses which had their phase shifted in the previous iteration
		else: # neighbour in originalAngleChangeSet 
			if currentBus not in originalAngleChangeSet:
				print currentBus
		"""

#print len(explored)


# generate the list of bus whose angles need changing
with open(CAPERaw, 'r') as f:
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
		if Bus in explored and Bus not in originalAngleChangeSet: # new bus whose angle needs changing
			# generate a list of bus data to be changed
			toChangeAngles.append(line)

			# change angle and reconstruct lines
			Angle = words[8].strip()
			newAngle = float(Angle) + AngleChangeDict[Bus]
			words[8] = ' '*(9- len(str(newAngle))) + str(newAngle)
			nLine = reconstructLine2(words)
			newAngleChangeLines.append(nLine)

# list of all bus data whose angles need to be changed
with open(toChangeAnglesFile,'w') as f:
	for line in toChangeAngles:
		f.write(line)
		f.write('\n')

# generate a file which contains ALL the bus data which had angles changed. Angles are already changed here 
with open(AllAnglesChangeFile, 'w') as f:
	for line in originalAngleChangeLines:
		f.write(line)
		f.write('\n')
	f.write('New buses which are neighbours of original set:')
	f.write('\n')
	for line in newAngleChangeLines:
		f.write(line)
		f.write('\n')

# trace back the angle change (from child to parent)
with open(traceBackFile,'w') as f:
	f.write('Child->Parent')
	f.write('\n')
	for child in ParentDict.keys():
		string = child + '->' + ParentDict[child]
		f.write(string)
		f.write('\n')





# generate the new raw file
with open(old2winderRawFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')


busEndIndex = fileLines.index('0 / END OF BUS DATA, BEGIN LOAD DATA')

# generate bus data
for line in fileLines:
	if ('PSS' in line) or ('COMED' in line) or ('DYNAMICS' in line):
	    continue
	if 'END OF BUS DATA' in line:
	    break
	words = line.split(',')
	if len(words)<2: # continue to next iteration of loop if its a blank line
		continue
	Bus = words[0].strip()

	if Bus in explored: # bus needs to have angle changed
		continue
	else: # bus does not need to have angle changed
		newRawLines.append(line)

# add these two bus lines, for some reason they were missing
newRawLines.append("243083,'05CAMPSS    ', 138.0000,1, 205,1251,   1,1.01145, -55.0773")
newRawLines.append("658082,'MPSSE  7    ', 115.0000,1, 652,1624, 658,1.02055, -45.2697")

# add all the phase shifted bus data
for line in originalAngleChangeLines:
	if line == '':
		continue
	if 'Log' in line:
		continue
	newRawLines.append(line)
for line in newAngleChangeLines:
	if line == '':
		continue
	if 'Log' in line:
		continue
	newRawLines.append(line)

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


"""
# generate new bus data with all the angle shifts incorporated
###### generate new bus angles according to phase shift

with open(AllBusFileOld,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		words = line.split(',')
		if len(words) <2:
			continue

		Bus = words[0].strip()

		if Bus in explored: # bus needs to have angle changed
			continue
		else: # bus does not need to have angle changed
			NoAngleChangeBusLines.append(line)


# generate a new list which will contain the entire set of CAPE bus data
AllBusLines = NoAngleChangeBusLines
for line in originalAngleChangeLines:
	AllBusLines.append(line)
for line in newAngleChangeLines:
	AllBusLines.append(line)


# write the bus data to a file
with open(AllBusFileNew,'w') as f:
	for line in AllBusLines:
		f.write(line)
		f.write('\n')

# make a copy in Donut Hole v2
dest = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/AllMappedBusData.txt'
shutil.copyfile(AllBusFileNew,dest)
"""