"""
generate a 2 winder tf neighbour dict for the planning case
"""


Raw = 'NewCAPERawClean.raw'
#CAPERaw = 'CAPE_RAW0225v33.raw'

tf2wNeighbourDictCAPE = {}
AreaDict = {}

def BusAppend(Bus,NeighbourBus,tfNeighbourDict):
	if Bus not in tfNeighbourDict.keys():
		tfNeighbourDict[Bus] = []
	tfNeighbourDict[Bus].append(NeighbourBus)


with open(Raw, 'r') as f:
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
		AreaDict[Bus] = area

	"""
	branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA') + 1
	branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')

	for i in range(branchStartIndex, branchEndIndex):
		line = fileLines[i]
		words = line.split(',')
		Bus1 = words[0].strip()
		Bus2 = words[1].strip()
		BusAppend(Bus1,Bus2,NeighbourDict)
		BusAppend(Bus2,Bus1,NeighbourDict)
	"""

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
			BusAppend(Bus1,Bus2,tf2wNeighbourDictCAPE)
			BusAppend(Bus2,Bus1,tf2wNeighbourDictCAPE)
			i+=4



		else: # three winder
			"""
			BusAppend(Bus1,Bus2,tfNeighbourDictCAPE)
			BusAppend(Bus1,Bus3,tfNeighbourDictCAPE)
			BusAppend(Bus2,Bus1,tfNeighbourDictCAPE)
			BusAppend(Bus2,Bus3,tfNeighbourDictCAPE)
			BusAppend(Bus3,Bus1,tfNeighbourDictCAPE)
			BusAppend(Bus3,Bus2,tfNeighbourDictCAPE)
			"""
			i+=5


