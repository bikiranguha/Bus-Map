# now compile the new raw file, problems will arise during getting the load flow data, since a lot of one-to-one mappings will not be present
	# From the raw file, grab all the bus (branch, load, tf, gen, shunt) data for buses in AllToBeMappedSet, which do not belong to ArtificialLoadBusSet
	# For ArtificialLoadBusSet, only add those connections where the other end belongs to AllToBeMappedSet
	# Get the AL branch data, get the flows and put them in as load data
	# add all non-comed data using the cropped data, find out how the boundary branches were being incorporated


import sys
sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2')
sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/Automate 345 kV mapping')
from writeFileFn import writeToFile # function to write a list of lines to a given text file
from getBusDataFn import getBusData # create a dictionary which organizes all bus data
from analyzeBusReportFn import BusFlowData # generates bus flow report dictionary with from Bus as key
from ArtificialLoadFnv2 import artificialLoad # generatesa all the artificial load data

CAPERaw = 'RAW0602.raw' # old merged raw file, which will be cropped
newRawFile = 'RAWCropped.raw' # new cropped raw file
AllToBeMappedSet =set() # set of  comed buses which will be there in the cropped raw file
ArtificialLoadBusSet = set() #  set of artificial load buses in comed
AllToBeMappedFile = 'AllToBeMappedFile.txt'
newBusData = 'newBusData.txt' # bus data
newBranchData ='newBranchData.txt' # branch (line) data
newGenData = 'newGenData.txt' # gen data
newTFData = 'newTFData.txt' # transformer data
ArtificialLoadBusFile = 'ArtificialLoadBusFile.txt'
newLoadData = 'newLoadData.txt' # load data
newFSData = 'newFSData.txt' # fixed shunt data
newSSData = 'newSSData.txt' # switched shunt data
planningFlowReport = 'BusReports_Planning.txt' 
planningRaw = 'hls18v1dyn_1219.raw'
ArtificialLoadMappingFile = 'ArtificialLoadMapping.txt' # input mapping file for artificial loads
CAPEBusDataDict = getBusData(CAPERaw)
######### read all the necessary files

# get the necessary comed buses whose voltage value is less than 345 kV
with open(AllToBeMappedFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

	# grab bus data
	for line in fileLines:
		if line == '':
			continue
		if 'List of buses' in line: # skip the header file
			continue
		words = line.split(',')
		Bus = words[0].strip()
		AllToBeMappedSet.add(Bus)


# get the artificial load bus set
with open(ArtificialLoadBusFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

	# grab bus data
	for line in fileLines:
		if line == '':
			continue
		if 'List of buses' in line: # skip the header file
			continue
		words = line.split(',')
		Bus = words[0].strip()
		ArtificialLoadBusSet.add(Bus)


# generate artificial load bus data

planningFlowData = BusFlowData(planningFlowReport,planningRaw) # flow data for planning
artificialLoadLines = [] # lines which will contain all the artificial load data
with open(ArtificialLoadMappingFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

	# grab artificial load mapping data
	for line in fileLines:
		if line == '':
			continue	
		if 'CAPE' in line:
			continue

		outerwords = line.split('=')
		CAPESide = outerwords[0].strip()
		PlanningSide = outerwords[1].strip()

		CAPEBuses = CAPESide.split(',')
		CAPEToBus = CAPEBuses[1].strip()
		PlanningBuses = PlanningSide.split(',')
		PlanningFromBus = PlanningBuses[0].strip()
		PlanningToBus = PlanningBuses[1].strip()
		ALLine = artificialLoad(CAPEToBus, PlanningFromBus, PlanningToBus, planningFlowData)
		artificialLoadLines.append(ALLine)

# grab bus data for comed
newBusLines = [] # cropped bus data for comed

with open(CAPERaw,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

	# grab bus data
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
			continue
		if Bus in AllToBeMappedSet:
			newBusLines.append(line)

		# get all the 345 or higher buses
		elif CAPEBusDataDict[Bus].area == '222' and float(CAPEBusDataDict[Bus].NominalVolt) >= 345.0:
			newBusLines.append(line)
			AllToBeMappedSet.add(Bus)

# these 2 lines are never read, so i am manually adding them
#newBusLines.append("243083,'05CAMPSS    ', 138.0000,1, 205,1251,   1,1.01145, -55.0773")
#newBusLines.append("658082,'MPSSE  7    ', 115.0000,1, 652,1624, 658,1.02055, -45.2697")

writeToFile(newBusData,newBusLines,'') # writes all the lines in newBusLines to newBusData


# grab branch data properly 
# only include branches where either Bus1 or Bus2 appears in the AllToBeMappedSet but in ArtificialLoadBusSet. These are the buses whose branches are all included.
# This strategy also ensures that only the branches connecting the artificial load bus to an important bus is included. Any other branches to artificial load buses are excluded
#  Boundary branches are already there in croppedBranchFile.txt, so they dont need to be included here

newBranchLines = [] # cropped branch data for comed
branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA') + 1
branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')

for i in range(branchStartIndex, branchEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	status = words[13].strip()
	if status != '1':
		continue
	try:
		Bus1area = CAPEBusDataDict[Bus1].area
		Bus2area = CAPEBusDataDict[Bus2].area
	except: # will not work for branch data where the to or from bus is 243083 or 658082
		continue
	if Bus1area == '222' and Bus2area == '222': # only include internal comed branches, boundary branches are already included in croppedBranchFile.txt
		if Bus1 in AllToBeMappedSet and Bus1 not in ArtificialLoadBusSet:
			newBranchLines.append(line)
		elif Bus2 in AllToBeMappedSet and Bus2 not in ArtificialLoadBusSet:
			newBranchLines.append(line)

writeToFile(newBranchData,newBranchLines,'') # writes all the lines in newBusLines to newBusData


# grab gen data, only include generators which appear in AllToBeMappedSet
newGenLines = []
genStartIndex = fileLines.index('0 / END OF FIXED SHUNT DATA, BEGIN GENERATOR DATA')+1
genEndIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA')

for i in range(genStartIndex, genEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus = words[0].strip()
	if Bus in AllToBeMappedSet:
		newGenLines.append(line)

writeToFile(newGenData,newGenLines,'') # writes all the lines in newBusLines to newBusData

# grab tf data, logic is similar to that of branch data

newTFLines = []

tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')

i = tfStartIndex

while i<tfEndIndex:
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	status  = words[11].strip()
	if status != '1':
		i+=4
		continue
	try:
		Bus1area = CAPEBusDataDict[Bus1].area
		Bus2area = CAPEBusDataDict[Bus2].area
	except: # will not work for branch data where the to or from bus is 243083 or 658082
		i+=4
		continue

	needTF = 0 # flag to determine if we need (want to add) the tf
	if Bus1area == '222' and Bus2area == '222': # only include internal comed branches, boundary branches are already included in croppedBranchFile.txt
		if Bus1 in AllToBeMappedSet and Bus1 not in ArtificialLoadBusSet:
			needTF = 1
		elif Bus2 in AllToBeMappedSet and Bus2 not in ArtificialLoadBusSet:
			needTF = 1


	if needTF == 1:
		for j in range(4):
			newTFLines.append(line)
			i+=1
			line = fileLines[i]		

	else: # dont need tf, skip to next one
		i+=4

writeToFile(newTFData,newTFLines,'') # writes all the lines in newBusLines to newBusData


# grab load data only if the load belongs to an important bus (belongs to AllToBeMapped but not an ArtificialLoadBus)
newLoadLines = []
loadStartIndex = fileLines.index('0 / END OF BUS DATA, BEGIN LOAD DATA') + 1
loadEndIndex = fileLines.index('0 / END OF LOAD DATA, BEGIN FIXED SHUNT DATA')

for i in range(loadStartIndex,loadEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus = words[0].strip()
	if Bus in AllToBeMappedSet and Bus not in ArtificialLoadBusSet:
		newLoadLines.append(line)

# add all the artificial load data
for line in artificialLoadLines:
	newLoadLines.append(line)

writeToFile(newLoadData,newLoadLines,'') # writes all the lines in newBusLines to newBusData



# grab fixed shunt data only if it belongs to an important bus (belongs to AllToBeMapped but not an ArtificialLoadBus)
newFSLines = []

fixedShuntStartIndex = fileLines.index('0 / END OF LOAD DATA, BEGIN FIXED SHUNT DATA') + 1
fixedShuntEndIndex = fileLines.index('0 / END OF FIXED SHUNT DATA, BEGIN GENERATOR DATA')
for i in range(fixedShuntStartIndex,fixedShuntEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus = words[0].strip()
	if Bus in AllToBeMappedSet and Bus not in ArtificialLoadBusSet:
		newFSLines.append(line)


writeToFile(newFSData,newFSLines,'') # writes all the lines in newBusLines to newBusData


# grab switched shunt data only if it belongs to an important bus (belongs to AllToBeMapped but not an ArtificialLoadBus)
newSSLines = []
switchedShuntStartIndex = fileLines.index('0 / END OF FACTS DEVICE DATA, BEGIN SWITCHED SHUNT DATA') + 1
switchedShuntEndIndex = fileLines.index('0 / END OF SWITCHED SHUNT DATA, BEGIN GNE DATA')

for i in range(switchedShuntStartIndex,switchedShuntEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus = words[0].strip()
	if Bus in AllToBeMappedSet and Bus not in ArtificialLoadBusSet:
		newSSLines.append(line)


writeToFile(newSSData,newSSLines,'') # writes all the lines in newBusLines to newBusData




# compile new raw file
miscDataFile = 'miscData.txt'


# the set of cropped files contain the non-comed data. In here, the branch data also contains comed boundary branch data
croppedBusFile = 'croppedBusFile.txt'
croppedLoadFile = 'croppedLoadFile.txt'
croppedoutBranchFile = 'croppedBranchFile.txt'
croppedtfFile = 'croppedtfFile.txt'
croppedGenFile = 'croppedGenFile.txt'
croppedfsFile = 'croppedfsFile.txt'
croppedssFile = 'croppedssFile.txt'



# get all bus data
with open(newBusData,'r') as f:
	ComedBusData = f.read()
with open(croppedBusFile,'r') as f:
	otherBusData = f.read()


# Load data
with open(newLoadData,'r') as f:
	ComedLoadData = f.read()

with open(croppedLoadFile,'r') as f:
	otherLoadData = f.read()	

#Fixed shunt data
with open(newFSData,'r') as f:
	ComedfsData  = f.read()
with open(croppedfsFile,'r') as f:
	otherfsData = f.read()

# Gen data

with open(newGenData,'r') as f:
	ComedGenData = f.read()
with open(croppedGenFile,'r') as f:
	otherGenData = f.read()

# Branch data
with open(newBranchData,'r') as f:
	ComedBranchData = f.read()
with open(croppedoutBranchFile,'r') as f:
	otherBranchData = f.read()

# Transformer data
with open(newTFData,'r') as f:
	ComedtfData = f.read()
with open(croppedtfFile,'r') as f:
	othertfData = f.read()

# Misc data (such as Area, zone)
with open(miscDataFile,'r') as f:
	miscData = f.read()

# switched shunt data
with open(newSSData,'r') as f:
	ComedssData = f.read()
with open(croppedssFile,'r') as f:
	otherssData = f.read()

with open('footer.txt','r') as f:
	footerData = f.read()


# generate new raw file
with open(newRawFile,'w') as f:
	f.write('0,   100.00, 33, 1, 1, 60.00     / PSS(R)E-33.3    TUE, DEC 13 2016  22:08')
	f.write('\n')
	f.write('COMED 2018,  HLS18V1, N18S OUTSIDE AND 18 INTCHNG')
	f.write('\n')
	f.write('DYNAMICS REVSION 01')
	f.write('\n')

	f.write(ComedBusData)
	f.write(otherBusData)
	f.write('\n')
	f.write('0 / END OF BUS DATA, BEGIN LOAD DATA')
	f.write('\n')
	f.write(ComedLoadData)
	f.write(otherLoadData)
	f.write('\n')
	f.write('0 / END OF LOAD DATA, BEGIN FIXED SHUNT DATA')
	f.write('\n')
	f.write(ComedfsData)
	f.write(otherfsData)
	f.write('\n')
	f.write('0 / END OF FIXED SHUNT DATA, BEGIN GENERATOR DATA')
	f.write('\n')
	f.write(ComedGenData)
	f.write(otherGenData)
	f.write('\n')
	f.write('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA')
	f.write('\n')
	f.write(ComedBranchData)
	f.write(otherBranchData)
	f.write('\n')
	f.write('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')
	f.write('\n')
	f.write(ComedtfData)
	f.write(othertfData)
	f.write('\n')
	f.write('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')
	f.write('\n')
	f.write(miscData)
	f.write('\n')
	f.write(ComedssData)
	f.write(otherssData)
	f.write('\n')
	f.write(footerData)



# remove any blank lines
cleanLines = []
with open(newRawFile,'r')  as f:
	content = f.read()
	lines = content.split('\n')
	for line in lines:
		if line != '':
			cleanLines.append(line)
cleannewRawFile = newRawFile
with open(cleannewRawFile,'w') as f:
	for line in cleanLines:
		f.write(line)
		f.write('\n')