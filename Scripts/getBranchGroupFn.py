"""
	Function to generate a dictionary which will contain a list of ties of the bus. 
	Bus will not be present in keys if no ties connected to it
"""

def makeBranchGroups(Raw):
	BranchGroupDict = {}
	#BranchGroupList = []
	with open(Raw,'r') as f:
		filecontent = f.read()
		fileLines = filecontent.split('\n')
		branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA')+1
		branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')
		for i in range(branchStartIndex,branchEndIndex): # search through branch data
			words = fileLines[i].split(',')
			BranchCode = words[2].strip()
			status = words[-5].strip()
			if BranchCode == "'99'" and status == '1':
				Bus1 = words[0].strip()
				Bus2 = words[1].strip()

				if Bus1 not in BranchGroupDict.keys():
					BranchGroupDict[Bus1] = set()
				BranchGroupDict[Bus1].add(Bus2)

				if Bus2 not in BranchGroupDict.keys():
					BranchGroupDict[Bus2] = set()
				BranchGroupDict[Bus2].add(Bus1)

				"""
				# add ties of ties for both Bus1 and Bus2
				for Bus in list(BranchGroupDict[Bus1]):
					if Bus != Bus2:
						BranchGroupDict[Bus2].add(Bus)

				for Bus in list(BranchGroupDict[Bus2]):
					if Bus != Bus1:
						BranchGroupDict[Bus1].add(Bus)
				"""

		for Bus in BranchGroupDict.keys():
			ties = list(BranchGroupDict[Bus])
			moreTies = set()
			for tie in ties:
				tieSet = BranchGroupDict[tie]
				for t in list(tieSet):
					moreTies.add(t)
			for t in list(moreTies):
				BranchGroupDict[Bus].add(t)



	return BranchGroupDict

if __name__ == "__main__":
	Raw = 'RAW0501.raw'
	BranchGroupDict = makeBranchGroups(Raw)
	while True:
		searchTerm = raw_input('Enter bus number whose list of ties you are looking for: ')
		if searchTerm in BranchGroupDict.keys():
			for Bus in list(BranchGroupDict[searchTerm.strip()]):
				print Bus
		else:
			print 'Bus has no ties'
