from generateNeighbours import BranchConnDict, tfConnDict


verifiedMapFile = 'PSSEGenMapVerified.txt'
NewRaw = 'NewCAPERawClean.raw'

PSSEGenVoltDict = {}
CAPEGenVoltDict = {}
GenMapDict = {}
PSSEGenBusSet = set()
CAPEGenBusSet = set()
Gen34kVSet = set() # set of 34 kV buses which are either gen bus or are connected to gen buses somehow
BusVoltDict = {}




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
		PSSEVolt = float(words[3].strip())
		CAPEBus = words[5].strip()
		CAPEVolt = float(words[7].strip())
		PSSEGenBusSet.add(PSSEBus)
		#CAPEGenBusSet.add(CAPEBus)
		GenMapDict[CAPEBus] = PSSEBus
		PSSEGenVoltDict[PSSEBus] = PSSEVolt
		#CAPEGenVoltDict[CAPEBus] = CAPEVolt

		# if any of the gen buses are 34 kV, then they need to be handled carefully
		if CAPEVolt >= 30.0 and CAPEVolt <= 40.0:
			#print PSSEBus
			Gen34kVSet.add(PSSEBus)


# generate NeighbourDict for branches
with open(NewRaw, 'r') as f:
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
		#angle = float(words[8].strip())
		area = words[4].strip()
		#AreaDict[Bus] = area

		if area == '222':
			#BusAngleDict[Bus] = angle
			BusVoltDict[Bus] = BusVolt
			#ComedBusSet.add(Bus)


# investigate any branch connections
branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA') + 1
branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')
for i in range(branchStartIndex,branchEndIndex):
	line = fileLines[i]
	words = line.split(',')

	Bus1 = words[0].strip()
	Bus2 = words[1].strip()

	status = words[-5].strip()

	noGenBranchConnections = 1
	# verified that none of these generator buses are connected to branches, only tf
	if Bus1 in CAPEGenBusSet or Bus2 in CAPEGenBusSet:
		if status == '1':
			print line
			noGenBranchConnections = 0

if noGenBranchConnections == 1:
	print "No generator buses have branch connections! Yesss!"

#################################


# investigate the tf connections of the gen buses
for Bus in list(PSSEGenBusSet):

	if Bus in tfConnDict.keys():
		for neighbour in tfConnDict[Bus]: # tf conn of gen buses
			if BusVoltDict[neighbour] > 40.0: # One of the tf winding is HV, continue to next gen bus
				break

			if neighbour in BranchConnDict.keys(): # LV neighbour has branches
				print 'Bus ' + Bus + ' has a LV tf connection ' + neighbour + ' which contains branches.'

			if neighbour in Gen34kVSet: # LV neighbour already identifed as a 34 kV gen bus
				continue
			
			neighboursDepth2 = tfConnDict[neighbour] # depth 2 neighbour of current gen bus

			for neighbourD2 in neighboursDepth2:
				if neighbourD2 not in PSSEGenBusSet and BusVoltDict[neighbourD2] < 40.0:
					print 'Bus ' + Bus + ' has a LV tf connection ' + neighbour + ' which are connected to other LV buses through transformers.'
	else:
		if Bus in Gen34kVSet: # 34 kV gen bus, already acknowledged in script
			continue
		print 'Bus ' + Bus + ' does not have a direct HV tf connection. Please investigate.'



print 'Set of 34 kV generator buses:'
print Gen34kVSet



