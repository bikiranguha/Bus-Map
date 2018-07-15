"""
Script which returns BranchNeighbourDict whose values are a set of neighbours
"""

def getBranchNeighbours(Raw):

	BranchNeighbourDict = {} # Dictionary of branch and tf connections
	def BusAppend(Bus,NeighbourBus,BranchNeighbourDict):
		if Bus not in BranchNeighbourDict.keys():
			BranchNeighbourDict[Bus] = set()
		BranchNeighbourDict[Bus].add(NeighbourBus)


	with open(Raw, 'r') as f:
		filecontent = f.read()
		fileLines = filecontent.split('\n')


		# get branch data
		branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA') + 1
		branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')

		for i in range(branchStartIndex, branchEndIndex):
			line = fileLines[i]
			words = line.split(',')
			Bus1 = words[0].strip()
			Bus2 = words[1].strip()
			#status = words[13].strip()

			#if status == '1':
			BusAppend(Bus1,Bus2,BranchNeighbourDict)
			BusAppend(Bus2,Bus1,BranchNeighbourDict)



	return BranchNeighbourDict


