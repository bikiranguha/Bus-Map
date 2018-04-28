"""
 generate branch neighbours only for comed buses in Raw0414tmp_loadsplit.raw, even for disconnected branch neighbours
"""


NewRaw = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/Island 34 system' + '/' + 'Raw0414tmp_loadsplit.raw'
BranchConnDict = {}
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
		# status = words[-5].strip()

		if Bus1 in ComedBusSet or Bus2 in ComedBusSet:
			BusAppend(Bus1,Bus2,BranchConnDict)
			BusAppend(Bus2,Bus1,BranchConnDict)




