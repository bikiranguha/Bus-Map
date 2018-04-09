NewRaw = 'RAW0406018.raw'
BranchConnDict = {}
tfConnDict = {}
ComedBusSet = set()
#AreaDict = {}

def BusAppend(Bus,NeighbourBus,NeighbourDict):
	if Bus not in NeighbourDict.keys():
		NeighbourDict[Bus] = []
	NeighbourDict[Bus].append(NeighbourBus)


with open(NewRaw, 'r') as f:
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
		area = words[4].strip()
		if area == '222':
			ComedBusSet.add(Bus)
		#AreaDict[Bus] = area


	branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA') + 1
	branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')

	for i in range(branchStartIndex, branchEndIndex):
		line = fileLines[i]
		words = line.split(',')
		Bus1 = words[0].strip()
		Bus2 = words[1].strip()
		status = words[-5].strip()

		if Bus1 in ComedBusSet or Bus2 in ComedBusSet:
			if status == '1':
				BusAppend(Bus1,Bus2,BranchConnDict)
				BusAppend(Bus2,Bus1,BranchConnDict)

	tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
	tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')
	i = tfStartIndex
	while i < tfEndIndex:
		line = fileLines[i]
		words = line.split(',')
		Bus1 = words[0].strip()
		Bus2 = words[1].strip()
		Bus3 = words[2].strip()

		if Bus3 == '0': # two winder
			if Bus1 not in ComedBusSet: # non-comed tf, increment i and continue
				i+=4
				continue

			BusAppend(Bus1,Bus2,tfConnDict)
			BusAppend(Bus2,Bus1,tfConnDict)
			i+=4



		else: # three winder
			if Bus1 not in ComedBusSet:# non-comed tf, increment i and continue
				i+=5
				continue
			BusAppend(Bus1,Bus2,tfConnDict)
			BusAppend(Bus1,Bus3,tfConnDict)
			BusAppend(Bus2,Bus1,tfConnDict)
			BusAppend(Bus2,Bus3,tfConnDict)
			BusAppend(Bus3,Bus1,tfConnDict)
			BusAppend(Bus3,Bus2,tfConnDict)
			i+=5


