"""

"""


from map345 import MapDict,PSSEBusSet, CAPEBusSet, groupList
from generateNeighbours import NeighbourDict # Dictionary of neighbours for each bus in CAPE

mapFile = 'mapped_buses_cleaned.csv' # manual map file
PSSEBusData = 'PSSE_bus_data.txt' 
#mapFile = 'mapped_buses_cleaned.csv'
outsideComedFile = 'outsideComedBusesv4.txt' # list of buses which are outside comed in the CAPE case
GenBusChangeLog = 'GenBusChange.log' # file which helps decide which buses should be gen buses in the new raw file
changeBusNoLog = 'changeBusNoLog.txt' # file containing bus renumbering
isolatedCAPEBusList = 'isolatedCAPEBusList.txt' # list of buses which are isolated in cape
CAPERaw = 'CAPE_RAW0228v33.raw'
AllMappedBusData = 'AllMappedBusData.txt' # output file which contains all the CAPE bus data, with voltages mapped from planning
AllMappedLog = 'AllMappedLog.txt' # the log of which bus maps to what


AllCAPEBuses = set()
AllPSSEBuses = set()
unmappedCAPEset = set()
TrueGenBusSet = set()
noNeedtoMapSet = set()
planningGenMap = {}
VoltageDict = {}
changeBusNumber = {}

# open up CAPE data to get a set of all original CAPE buses
with open(CAPERaw,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if ('PSS' in line) or ('COMED' in line):
			continue
		if 'END OF BUS DATA' in line:
			break
		words = line.split(',')
		if len(words) < 2:
			continue
		Bus = words[0].strip()
		AllCAPEBuses.add(Bus)

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



# open the simple map and generate a dictionary of PSSE->CAPE maps, also generate sets of PSSE and CAPE buses to be mapped
with open(mapFile,'r') as f:
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
		if CAPEBus in CAPEBusSet: #already mapped in Gen345 Mapping
			#print CAPEBus
			continue

		if PSSEBus not in PSSEBusSet: 
			PSSEBusSet.add(PSSEBus)
		MapDict[CAPEBus] = PSSEBus 
		CAPEBusSet.add(CAPEBus) # log that the CAPE Bus has been mapped
		for lst in groupList:
			if CAPEBus in lst:
				for Bus in lst:
					if Bus!= CAPEBus: # generate key-value pairs for the remaining buses in the group
						if Bus not in noNeedtoMapSet:
							MapDict[Bus] = PSSEBus
							CAPEBusSet.add(Bus) 
				break

#print len(CAPEBusSet)


# get a list of unmapped set
for Bus in AllCAPEBuses:
	if Bus not in CAPEBusSet:
		if Bus not in noNeedtoMapSet:
			unmappedCAPEset.add(Bus)


# map all the neighbours with same voltage and angle
# keep doing this iteratively until all connected buses are mapped

#print noNeedtoMapSet
#print 'Initial number of unmapped buses: ', len(unmappedCAPEset)
iteration = 0
#while ((len(unmappedCAPEset)>0) or (iteration <1000)):
while iteration <10:
	print 'Iteration: ' + str(iteration) + ' Number of unmapped buses: ' + str(len(unmappedCAPEset))
	for Bus in AllCAPEBuses:
		if Bus not in noNeedtoMapSet:
			if Bus in CAPEBusSet:
				neighboursList = NeighbourDict[Bus]
				for neighbour in neighboursList:
					if neighbour in unmappedCAPEset:
						MapDict[neighbour] = MapDict[Bus]
						CAPEBusSet.add(neighbour)
						unmappedCAPEset.remove(neighbour)
	
	iteration +=1

#print MapDict['8064']

"""
#print 'Initial number of unmapped buses: ', len(unmappedCAPEset)
iteration = 0
#while ((len(unmappedCAPEset)>0) or (iteration <1000)):
while iteration <10:
	print 'Iteration: ' + str(iteration) + ' Number of unmapped buses: ' + str(len(unmappedCAPEset))
	for Bus in AllCAPEBuses:
		if Bus in AllCAPEMappedSets:
			neighboursList = NeighbourDict[Bus]
			for neighbour in neighboursList:
				if neighbour in unmappedCAPEset:
					MapDict[neighbour] = MapDict[Bus]
					AllCAPEMappedSets.add(neighbour)
					unmappedCAPEset.remove(neighbour)
	
	iteration +=1
"""



# open up PSSE bus data and make a dictionary of Vmag and Vang
with open(PSSEBusData,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		words = line.split(',')
		if len(words) < 2:
			continue
		Bus = words[0]
		AllPSSEBuses.add(Bus.strip())
		Vmag = words[7]
		Vang = words[8]
		if Bus in PSSEBusSet:
			VoltageDict[Bus] = [Vmag, Vang]


# TrueGenBusSet decides if the new buses will be generator buses or not
with open(GenBusChangeLog,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	genfileLines = fileLines
	for line in fileLines:
		if 'CAPE' in line:
			continue
		words = line.split('->')
		if len(words) < 2:
			continue
		planningBus =  words[1].strip()
		#planningGenSet.add(planningBus)
		TrueGenBus = words[0].strip()
		TrueGenBusSet.add(TrueGenBus)
		planningGenMap[TrueGenBus] = planningBus


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

		# Check if there is any Bus number conflict
		if Bus not in noNeedtoMapSet:
			if Bus not in TrueGenBusSet: # Bus number already changed to PSSE Gen Bus Number
				if Bus in AllPSSEBuses:
					newNoFound = 0
					if newBus not in AllPSSEBuses:
						if newBus not in AllCAPEBuses:
							changeBusNumber[Bus] = str(newBus)
							words[0] = str(newBus)
							newBus +=1
							newNoFound = 1
						else:
							newBus +=1
					else:
						newBus +=1
		noNeedtoMapSet.add('998884') # temporary addition, does not seem to be connected to anything in comed


		# generate new line to add to output file
		if Bus not in noNeedtoMapSet:
			if Bus not in unmappedCAPEset:
				currentLine = ''
				PSSEBus = MapDict[Bus]
				Vmag = VoltageDict[PSSEBus][0]
				Vang = VoltageDict[PSSEBus][1]
				words[7] = Vmag
				words[8] = Vang

				if Bus in TrueGenBusSet:
					planningBus = planningGenMap[Bus]
					words[0] = planningBus

				else:
					words[3] = '1' # keep the cicruit id = 1
				words[4] = ' 222'
				for word in words:
					currentLine += word
					currentLine +=','

				newBusLines.append(currentLine[:-1])

# make a new file which has the changed bus data (changed bus numbers with copied Vmag and Vang)
with open(AllMappedBusData,'w') as f:
	for line in newBusLines:
		f.write(line)
		f.write('\n')

# log file of PSSE-CAPE voltage mapping
with open(AllMappedLog,'w') as f:
	f.write('PSSEBus->CAPEBus\n')
	for key in MapDict:
		mapStr = MapDict[key] + '->' + key
		f.write(mapStr)
		f.write('\n')

# new log file for bus number conflict resolution
with open(changeBusNoLog,'w') as f:
	f.write('CAPE-> PSSE Gen Bus')
	f.write('\n')
	for i in range(1,len(genfileLines)):
		line  = genfileLines[i]
		if line == '':
			continue
		f.write(line)
		f.write('\n')
	f.write('Old CAPE->New\n')
	for key in changeBusNumber:
		mapStr = key + '->' + changeBusNumber[key]
		f.write(mapStr)
		f.write('\n')


with open(isolatedCAPEBusList,'w') as f:
	f.write('List of isolated buses in CAPE:\n')
	for bus in unmappedCAPEset:
		f.write(bus)
		f.write('\n')