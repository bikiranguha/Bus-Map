# Generate a set of all buses which need to be mapped in CAPE raw file. When a mapping has been found, remove it from the set
# Do the gen maps first
# Map all the cases provided by hemanth, if they appear in the current CAPE raw file

# functions or external datasets
from getBusDataFn import getBusData
from writeFileFn import writeToFile
from generateNeighboursFn import getNeighbours

# functions
def reconstructLine2(words):
	currentLine = ''
	for word in words:
		currentLine += word
		currentLine += ','
	return currentLine[:-1]
########


# files
verifiedMapFile = 'PSSEGenMapVerified.txt' # verified mapping of the gen data'
CAPERaw = 'MASTER_CAPE_Fixed.raw'
PSSE_Raw = 'hls18v1dyn_1219.raw' # raw file from planning
outsideComedFile = 'outsideComedBusesv4.txt' # list of buses which are outside comed in the CAPE case
BusChangeLog = 'GenBusChange.log' # log file of CAPE buses which have been renumbered to PSSE gen bus numbers
GenBusMapLog = 'GenBusMap.log' # gen map used later on
isolatedCAPEBusList = 'isolatedCAPEBusList_All.txt' # list of buses which are isolated in cape
verifiedGenData  = 'verifiedGenData.txt' # this file contains the verified gen data
busMappingConfirmedFile = 'mapping_confirmed_old_numbers.txt' # bus mapping provided by hemanth (includes old bus numbers and tf midpoints)
PSSEMap = 'PSSE345Mapverified.txt' # verified 345 kV bus map data
manualMapFile = 'mapped_buses_cleaned0407.csv' # manual map file
changeLogPrevious  = 'changeBusNoLogPrevious.txt' # log of all bus number changes carried out previously
angleChangeFile = 'logAngleChange.txt'
changeLog  = 'changeBusNoLog.txt'
AllMappedBusData = 'AllMappedBusData.txt' # output file which contains all the CAPE bus data, with voltages mapped from planning
AllMappedLog = 'AllMappedLog.txt' # the log of which bus maps to what
newMidPointList = 'MidPointBusesAdded.txt' # list of all planning midpoint maps added
# variables
MappedPSSEGenBusSet = set() # set of PSSE Comed gen bus which has been mapped
noNeedtoMapSet = set() # set of non-comed and isolated CAPE buses
CAPEBusDataDict = getBusData(CAPERaw)
planningBusDataDict = getBusData(PSSE_Raw)
GenBusSet = set() # set of all Comed gen buses in planning
MapAllExceptGenDict = {} # contains all the mappings
MapAllExceptGenSet = set() # set of buses which have been except for gen buses
stillUnmappedSet = set() # dynamically keep track of the buses which are still to be mapped
GenMapDict = {} # key: CAPEBus, value: planningBus 
AllCAPEBuses = set() # set of all CAPE buses which are needed (except outside comed and isolated)
verifiedGenLines = []
CAPENeighbourDict = getNeighbours(CAPERaw)
MappedCAPEGenBusSet = set()
changeNameDictNewToOld = {}# key: changed bus numbers, value: original bus numbers
AngleChangeDict = {} # key: original bus numbers, value: phase shifts in float
changeBusNumber = {} # dict which contains all the bus number changes
MappingConfirmedSet = set() # set of maps which are extracted from mapping_confirmed file
NewMidPointLines = [] # lines containing bus data of all the planning midpoints added
doNotChangeNominalVoltagePlanning = ['274848'] # do not change the voltage of these buses, the gen bus not connected to any tf in CAPE 
doNotChangeNominalVoltageCAPE = ['2117','2118','1878', '2564', '2568','2770','7395','30030','30031'] # voltages not properly assigned in corresponding mapping
# get the set of planning midpoint buses imported into the merged raw file
with open(newMidPointList,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		NewMidPointLines.append(line)
		#words = line.split(',')
		#Bus = words[0].strip()
		#MidpointSet.add(Bus)


# look at log files which contains all the changed bus numbers in the previous iteration (first time i did this)
with open(changeLogPrevious,'r') as f:
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
		#OldBusSet.add(OldBus)
		#NewBusSet.add(NewBus)
		changeNameDictNewToOld[NewBus] = OldBus

# get all the phase shifts
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
			#print Bus
			continue	
		if Bus in changeNameDictNewToOld.keys():
			Bus = changeNameDictNewToOld[Bus]
		AngleChangeDict[Bus] = Angle


# get a set of all buses outside the comed region in the CAPE model
with open(outsideComedFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'Manually' in line:
			continue
		if line.strip() != '':
			noNeedtoMapSet.add(line.strip())
			#CAPEMappedSet.add(line.strip())


# get the set of isolated buses and add them to no need to Map Set
with open(isolatedCAPEBusList,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'isolated' in line:
			continue
		noNeedtoMapSet.add(line.strip())


# get all the buses in CAPERaw which need to be mapped
for Bus in CAPEBusDataDict.keys():
	if Bus not in noNeedtoMapSet:
		stillUnmappedSet.add(Bus)
		AllCAPEBuses.add(Bus)



# open up the verified gen map file and extract the info into a set and a dictionary
with open(verifiedMapFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'Manual' in line:
			continue
		words = line.split(',')
		if len(words) < 2:
			continue
		PSSEBus = words[0].strip()
		CAPEBus = words[5].strip()
		MappedPSSEGenBusSet.add(PSSEBus)
		MappedCAPEGenBusSet.add(CAPEBus)
		#CAPEBusSet.add(CAPEBus)
		GenMapDict[CAPEBus] = PSSEBus
		changeBusNumber[CAPEBus] = PSSEBus
		stillUnmappedSet.remove(CAPEBus)

# get an actual list of gen buses inside comed
with open(PSSE_Raw,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split("\n")
    for line in fileLines:
        if ('PSS' in line) or ('COMED' in line) or ('DYNAMICS' in line):
            continue
        if 'END OF BUS DATA' in line:
            break
        words = line.split(',')
        if len(words)<2: # continue to next iteration of loop if its a blank line
            continue
        BusCode = words[3].strip()
        area = words[4].strip()
        if BusCode == '2' and area == '222':
            #genLines.append(line)
            GenBusSet.add(words[0].strip())

# make sure all gen buses have been mapped, else print bus numbers
for Bus in GenBusSet:
	if Bus not in MappedPSSEGenBusSet:
		if Bus != '274847': # This bus has been excluded from the mapping
			print "Gen Bus Not Mapped Yet: ", Bus


# create a log file of CAPE buses which have been renumbered to PSSE gen bus numbers
with open(BusChangeLog,'w') as f:
	f.write('CAPEBus->PSSEBus\n')
	for key in GenMapDict:
		mapStr = key + '->' + GenMapDict[key]
		f.write(mapStr)
		f.write('\n')

# get the gen data lines for the planning buses inside comed whose voltage values have been successfully mapped
with open(PSSE_Raw,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	# look at each line in branch data and add one end to Boundary Set if the other end is not present in BusSet
	genStartIndex = fileLines.index('0 / END OF FIXED SHUNT DATA, BEGIN GENERATOR DATA')+1
	genEndIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA')
	for i in range(genStartIndex,genEndIndex):
		words = fileLines[i].split(',')
		if len(words) <2:
			continue
		Bus = words[0].strip()
		#if Bus in MappedPSSEGenBusSet:
		if Bus in GenBusSet:
			if Bus != '274847': # special case, chosen to exclude
				verifiedGenLines.append(fileLines[i])

# this file contains the verified gen data
writeToFile(verifiedGenData,verifiedGenLines,'')



# gen map used later on
with open(GenBusMapLog,'w') as f:
	f.write('PSSEBus->CAPEBus\n')
	for key in GenMapDict:
		mapStr = GenMapDict[key] + '->' + key
		f.write(mapStr)
		f.write('\n')
#print len(CAPEBusSet)


#################################


# start the process of mapping all the remaining buses

# map all the confirmed buses 
with open(busMappingConfirmedFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue

		words = line.split('->')
		if len(words) < 2:
			continue
		PSSEBus = words[0].strip()
		CAPEBus = words[1].strip()

		# add maps only if they are not tf midpoints (which are generated later on)
		if CAPEBus in CAPEBusDataDict.keys():
			MapAllExceptGenDict[CAPEBus] = PSSEBus
			MapAllExceptGenSet.add(CAPEBus)
			try:
				stillUnmappedSet.remove(CAPEBus)
				MappingConfirmedSet.add(CAPEBus)
			except:
				pass
			

# get any additional 345 maps
with open(PSSEMap,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		words = line.split(',')
		if len(words) <2:
			continue
		PSSEBus = words[0].strip()
		CAPEBus = words[5].strip()

		if CAPEBus in stillUnmappedSet: # only add maps which have not been done already
		#	print CAPEBus
			MapAllExceptGenDict[CAPEBus] = PSSEBus
			MapAllExceptGenSet.add(CAPEBus)
			stillUnmappedSet.remove(CAPEBus)


# get any additional maps provided by the CS guys

# open the simple map and generate a dictionary of PSSE->CAPE maps, also generate sets of PSSE and CAPE buses to be mapped
with open(manualMapFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		words = line.split(',')
		if len(words) <2:
			continue
		PSSEBus = words[0].strip()
		CAPEBus = words[5].strip()
		PSSEBusCode = words[2].strip()
		if CAPEBus in noNeedtoMapSet:
			#print CAPEBus
			continue
		if 'M' in PSSEBusCode:
			continue
		if PSSEBus in ['NA','']:
			continue
		if CAPEBus in ['NA','']:
			continue
		if CAPEBus not in stillUnmappedSet: #already mapped, skip
			#print CAPEBus
			continue
		if PSSEBus not in planningBusDataDict.keys(): # type 4 bus, which should not be mapped
			print 'Type 4 planning bus does not need to be mapped in manual_map file: ' +  PSSEBus
			continue
		MapAllExceptGenDict[CAPEBus] = PSSEBus
		MapAllExceptGenSet.add(CAPEBus)
		stillUnmappedSet.remove(CAPEBus)

print 'Getting maps for all remaining Buses by using BFS algorithm:'
iteration = 0
#while ((len(unmappedCAPEset)>0) or (iteration <1000)):
while iteration <10:
	print 'Iteration: ' + str(iteration) + ' Number of unmapped buses: ' + str(len(stillUnmappedSet))
	for Bus in AllCAPEBuses:
			if Bus in MappedCAPEGenBusSet or Bus in MapAllExceptGenSet:
				neighboursList = list(CAPENeighbourDict[Bus])
				for neighbour in neighboursList:
					if neighbour in stillUnmappedSet:
						try: # bus is not a gen bus
							planningMap = MapAllExceptGenDict[Bus]
						except: # bus is a gen bus
							planningMap = GenMapDict[Bus]
						MapAllExceptGenDict[neighbour] = planningMap
						MapAllExceptGenSet.add(neighbour)
						stillUnmappedSet.remove(neighbour)
	
	iteration +=1



# generate the new bus data by looking at the CAPE raw file and the maps

newBusLines = []
newBus = 750000
# open CAPE raw file and extract gen bus data which has been mapped and verified
with open(CAPERaw,'r') as f:
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
		if Bus in noNeedtoMapSet:
			continue
		# change all the gen bus numbers
		if Bus in MappedCAPEGenBusSet:
			planningGenBus = GenMapDict[Bus]
			words[0] = planningGenBus

		# Check if there is any Bus number conflict
		elif Bus not in MappedPSSEGenBusSet: # Bus number is not a gen (which are already changed to PSSE Gen Bus Number)
			if Bus in planningBusDataDict.keys(): # Bus number has conflict with PSSE bus number set

				newNoFound = 0
				# loop till you find a non-conflicting bus number
				while newNoFound == 0:
					if newBus not in planningBusDataDict.keys(): # newBus does not exist in planningBusDataDict.keys()
						if newBus not in AllCAPEBuses: # newBus does not exist in AllCAPEBuses
							changeBusNumber[Bus] = str(newBus)
							words[0] = str(newBus)
							newBus +=1
							newNoFound = 1 # newBus has no conflicts
						else: # newBus still conflicts with AllCAPEBuses set
							newBus +=1
					else:
						newBus +=1



		# get volt, angle, phase shifts and apply
		if Bus in MappedCAPEGenBusSet:
			planningBus = GenMapDict[Bus]
			words[3] = '2'
		else:
			planningBus = MapAllExceptGenDict[Bus]
			words[3] = '1'

		PhaseShift = 0.0
		if Bus in AngleChangeDict.keys():
			PhaseShift = AngleChangeDict[Bus]
		Vmag = float(planningBusDataDict[planningBus].voltpu)
		VmagStr = '%.5f' %Vmag

		Vang = float(planningBusDataDict[planningBus].angle) + PhaseShift
		VangStr = '%.4f' %Vang
		VangStr = VangStr.rjust(9)

		words[4] = '222'
		words[7] =  VmagStr
		words[8] = VangStr


		# change the bus nominal voltage only if its Mapping Confirmed Set or a Generator Bus
		if Bus in MappingConfirmedSet or Bus in MappedCAPEGenBusSet:
			if planningBus not in doNotChangeNominalVoltagePlanning and Bus not in doNotChangeNominalVoltageCAPE:
				NomVolt = planningBusDataDict[planningBus].NominalVolt
				NomVolt = NomVolt.rjust(9)
				words[2] = NomVolt



		currentLine = reconstructLine2(words)
		newBusLines.append(currentLine)

# midpoint tf bus, whose tf data will be added later
newBusLines.append("275999,'DAVIS Fict;9M',138.0000,1, 222,   8, 222,0.99571, -54.8804,1.10000,0.90000,1.10000,0.90000")




# outputs
with open(AllMappedBusData,'w') as f:
	for line in newBusLines:
		f.write(line)
		f.write('\n')

	# add all the planning midpoints
	for line in NewMidPointLines:
		f.write(line)
		f.write('\n')
# log file of PSSE-CAPE voltage mapping
with open(AllMappedLog,'w') as f:
	f.write('PSSEBus->CAPEBus\n')

	# log all gen maps
	for key in GenMapDict:
		mapStr = GenMapDict[key] + '->' + key
		f.write(mapStr)
		f.write('\n')

	# log all non-gen maps
	for key in MapAllExceptGenDict:
		mapStr = MapAllExceptGenDict[key] + '->' + key
		f.write(mapStr)
		f.write('\n')

# new log file for bus number conflict resolution and for gen maps
with open(changeLog,'w') as f:
	f.write('Old CAPE -> New CAPE  (Includes gen number changes as well)')
	f.write('\n')
	for key in changeBusNumber.keys():
		mapStr = key + '->' + changeBusNumber[key]
		f.write(mapStr)
		f.write('\n')