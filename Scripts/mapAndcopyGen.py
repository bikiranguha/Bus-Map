"""
Extracts the gen map and constructs the gen data with CAPE buses renumbered to planning numbers
Gen data is imported from planning
"""

verifiedMapFile = 'PSSEGenMapVerified.txt' # verified mapping of the gen data
PSSE_Raw = 'hls18v1dyn_1219.raw' # raw file from planning
BusChangeLog = 'GenBusChange.log' # log file of CAPE buses which have been renumbered to PSSE gen bus numbers
verifiedGenData  = 'verifiedGenData.txt' # this file contains the verified gen data
GenBusMapLog = 'GenBusMap.log' # gen map used later on


PSSEBusSet = set() # set of all psse bus numbers in the mapping file
MapDict = {} # key: mapped CAPE gen bus, value: mapped planning bus
CAPEBusSet = set() # set of all CAPE bus numbers in the mapping file
#VoltageDict = {}
#newBusLines = []
GenBusSet = set() # set of all gen buses
#genLines = [] 
verifiedGenLines = [] # generator data lines

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
		PSSEBusSet.add(PSSEBus)
		CAPEBusSet.add(CAPEBus)
		MapDict[CAPEBus] = PSSEBus

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
	if Bus not in PSSEBusSet:
		if Bus != '274847': # This bus has been excluded from the mapping
			print "Gen Bus Not Mapped Yet: ", Bus


# create a log file of CAPE buses which have been renumbered to PSSE gen bus numbers
with open(BusChangeLog,'w') as f:
	f.write('CAPEBus->PSSEBus\n')
	for key in MapDict:
		mapStr = key + '->' + MapDict[key]
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
		#if Bus in PSSEBusSet:
		if Bus in GenBusSet:
			if Bus != '274847': # special case, chosen to exclude
				verifiedGenLines.append(fileLines[i])

# this file contains the verified gen data
with open(verifiedGenData,'w') as f:
	#f.write('List of simple gen data imported from planning:\n\n')
	for line in verifiedGenLines:
		f.write(line)
		f.write('\n')


# gen map used later on
with open(GenBusMapLog,'w') as f:
	f.write('PSSEBus->CAPEBus\n')
	for key in MapDict:
		mapStr = MapDict[key] + '->' + key
		f.write(mapStr)
		f.write('\n')
#print len(CAPEBusSet)