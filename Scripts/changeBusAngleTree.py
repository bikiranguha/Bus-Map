"""
	Script to implement BFS to shift bus angles of all neighbours of original buses which had their angles shifted
	Any buses connected downstream through transformers are also phase shifted alongwith branches
"""

from Queue import Queue
import shutil
from generatetfNeighboursCAPE import tf2wNeighbourDictCAPE # list of 2 winder tf neighbours of the bus

directory = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/'
busAngleChangeLog = directory +  'newBusAnglesSorted.txt' # file containing changed bus angle list
#busAngleChangeLog = 'newBusAngles.txt' # file containing changed bus angle list
angleChangeFile = directory + 'logAngleChange.txt' # file containing bus angle changes
CAPERaw = 'NewCAPERawClean.raw' # to be consistent with the raw file used in change3winderDatav14
toChangeAnglesFile = 'toChangeAngles.txt' # file which contains all the new bus data whose angles need to change
AllAnglesChangeFile = directory + '/' +  'AllAngleChangedLines.txt' # contains all the buses which got their angles changed
traceBackFile = 'traceback.txt' # file used to trace back the angle change (from child to parent)
#AllBusFileOld = 'AllMappedBusDataIter2.txt'  # File containing the bus data (old)
#AllBusFileNew = 'AllMappedBusDataIter3.txt' # Latest bus data file

HVShiftSet = set() # set of HV bus which have phase shifts
originalAngleChangeList = [] # list of all buses which have their angles changed, sorted in descending order of voltage
BusVoltDict = {} # key: bus voltage, value: Bus voltage
AngleChangeDict = {} # key: bus, value: angle change
BranchConnDict = {} # key: CAPE comed bus, value: neighbour branches
#TFConnDict = {}
AreaDict = {} # key: bus, value: area code
ParentDict = {} # key: child node in BFS algorithm, value: parent node in BFS algorithm
newAngleChangeLines = [] # list of new bus data, whose angles are going to be changed here
NoAngleChangeBusLines = [] # Data of buses which do not have any angles changed
toChangeAngles = [] # list of bus (along with bus data) which needs angles changed
DownStreamShiftSet = set() # to keep track of which LV bus angles are being shifted because they were connected to phase shift tf
ComedBusSet = set() # set of all Comed buses in CAPE
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
		if area == '222':
			ComedBusSet.add(Bus)


	branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA') + 1
	branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')

	for i in range(branchStartIndex, branchEndIndex):
		line = fileLines[i]
		words = line.split(',')
		Bus1 = words[0].strip()
		Bus2 = words[1].strip()

		try:
			if AreaDict[Bus1] == '222' and AreaDict[Bus2] == '222':
				BusAppend(Bus1,Bus2,BranchConnDict)
				BusAppend(Bus2,Bus1,BranchConnDict)
		except:
			#print line # two lines were giving trouble, but they are outside the comed region, so ignore
			pass




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
		originalAngleChangeList.append(Bus)

		if Bus not in ComedBusSet:
			print 'Alert, Bus ' + Bus + ' not in Comed in busAngleChangeLog.' 

		
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
		AngleChangeDict[Bus] = Angle

		if Bus not in ComedBusSet:
			print 'Alert, Bus ' + Bus + ' not in Comed in angleChangeFile.' 











# start the BFS search of changing bus angles


frontier = Queue(maxsize=0)
explored = set() # set of all buses which need angles changed (including original buses which have their angles changed already)

# put all the original phase shift buses in frontier
for bus in list(originalAngleChangeList):
	frontier.put(bus)

# put buses in explored if they belong to originalAngleChangeList or connected to them via branches
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

			# add phase shift to any LV bus connected downstream through tf
			if currentBus in tf2wNeighbourDictCAPE.keys():
				LVtfConn = [x for x in tf2wNeighbourDictCAPE[currentBus] if BusVoltDict[currentBus] > BusVoltDict[x] ] 

				if len(LVtfConn) > 0:
					for conn in LVtfConn:
						if conn not in DownStreamShiftSet:
							if conn in AngleChangeDict.keys(): # already has some phase shift, add this phase shift as well
								AngleChangeDict[conn] += AngleChangeDict[currentBus]
							else: # non-phase shift transformer
								AngleChangeDict[conn] = AngleChangeDict[currentBus]
							DownStreamShiftSet.add(conn)
							if conn in originalAngleChangeList:
								originalAngleChangeList.remove(conn) # do this so that this 
							frontier.put(conn) # branches of this bus needs to be phase shifted as well
							ParentDict[conn] = currentBus
						#else:
							#print 'Special case, multiple phase shift warning: ', conn
		


	for neighbour in NeighbourBus:
		if neighbour not in originalAngleChangeList:
				if neighbour not in explored:
					if neighbour not in ParentDict.keys():
						# Helps to keep track of the value of angle change
						ParentDict[neighbour] = currentBus

					frontier.put(neighbour)
		"""
		# check to see if the phase shifts are close to neighbouring buses which had their phase shifted in the previous iteration
		else: # neighbour in originalAngleChangeList 
			if currentBus not in originalAngleChangeList:
				print currentBus
		"""

#print len(explored)
print 'Any case of double appearance of downstream LV buses have been investigated and deemed to be harmless!'
# generate the list of bus whose angles need changing
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
		if Bus in AngleChangeDict.keys() and Bus not in originalAngleChangeList: # new bus whose angle needs changing
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


with open(angleChangeFile,'w') as f:
	line = 'Bus->Angle Change for all buses in change3winderData.py and changeBusAngleTree.py'
	f.write(line)
	f.write('\n')
	for key in AngleChangeDict.keys():
		line = key + '->' + str(AngleChangeDict[key])
		f.write(line)
		f.write('\n')
# generate new bus data with all the angle shifts incorporated
###### generate new bus angles according to phase shift
"""
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