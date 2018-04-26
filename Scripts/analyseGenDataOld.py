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



def checkVoltageTFWindings(tfBusList,currentBus):

	for Bus in tfBusList:
		if Bus == currentBus:
			continue

		if Bus == '0':
			continue

		if BusVoltDict[Bus] <= 40.0:
			print "Bus: ", Bus
			print "Voltage: ", BusVoltDict[Bus]
			print '\n'












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

# check the transformer connections of the generator buses:
tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')
i = tfStartIndex
while i < tfEndIndex:
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	Bus3 = words[2].strip()

	tfBusList = [Bus1,Bus2,Bus3]

	#PSList = getPhaseShifts(i, fileLines, Bus3)

	if Bus3 == '0': # two winder
		if Bus1 in PSSEGenBusSet:
			checkVoltageTFWindings(tfBusList,Bus1)


		if Bus2 in PSSEGenBusSet:
			checkVoltageTFWindings(tfBusList,Bus2)


		i+=4


	else: # three winder


		if Bus1 in PSSEGenBusSet:
			checkVoltageTFWindings(tfBusList,Bus1)

		if Bus2 in PSSEGenBusSet:
			if BusVoltDict[Bus1] > 40.0:
				i+=5
				continue

		if Bus3 in PSSEGenBusSet:
			if BusVoltDict[Bus1] > 40.0:
				i+=5
				continue
			checkVoltageTFWindings(tfBusList,Bus3)

		i+=5