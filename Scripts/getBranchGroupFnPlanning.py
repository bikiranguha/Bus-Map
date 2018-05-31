"""
	Function to generate a dictionary which will contain a list of ties of the bus. 
	Bus will not be present in keys if no ties connected to it
"""
import math
from Queue import Queue
#import sys
#sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2')
#from getBusDataFn import getBusData

highImpedanceTieList = []

def makeBranchGroups(planningRaw):
	BranchGroupDict = {}
	#BranchGroupList = []
	with open(planningRaw,'r') as f:
		filecontent = f.read()
		fileLines = filecontent.split('\n')
		branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA')+1
		branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')
		#BusDataDict = getBusData(Raw)
		for i in range(branchStartIndex,branchEndIndex): # search through branch data
			words = fileLines[i].split(',')
			#BranchCode = words[2].strip()
			R = float(words[3].strip())
			X = float(words[4].strip())
			Z = math.sqrt(R**2 + X**2)
			status = words[-5].strip()

			if Z <= 2e-4 and status == '1':

				Bus1 = words[0].strip()
				Bus2 = words[1].strip()
				"""
				#check whether all lines with ckt id == '99' are just ties
				Bus1Area = BusDataDict[Bus1].area
				Bus2Area = BusDataDict[Bus2].area

				if Z > 4e-6 and Bus1Area == '222' and Bus2Area == '222':
					highImpedanceTieList.append(fileLines[i])
				"""

				if Bus1 not in BranchGroupDict.keys():
					BranchGroupDict[Bus1] = set()
				BranchGroupDict[Bus1].add(Bus2)

				if Bus2 not in BranchGroupDict.keys():
					BranchGroupDict[Bus2] = set()
				BranchGroupDict[Bus2].add(Bus1)

		
		# get complete bus groups
		CompleteBranchGroupDict = {} # each bus has the full bus group as a set

		for Bus in BranchGroupDict.keys(): # scan each key and generates a full bus group set
			if Bus in CompleteBranchGroupDict.keys(): # Bus already has the group, so skip
				continue
			frontier = Queue(maxsize=0)
			frontier.put(Bus)
			BusGroup = set()

			# do something similar to BFS
			while not frontier.empty():
				currentBus = frontier.get()
				frontier.task_done()

				BusGroup.add(currentBus)

				ties = BranchGroupDict[currentBus]

				for tie in ties:
					if tie not in BusGroup:
						frontier.put(tie)
						BusGroup.add(tie)
			####
			for t in list(BusGroup):
				CompleteBranchGroupDict[t] = BusGroup



	return CompleteBranchGroupDict

if __name__ == "__main__":
	planningRaw = 'hls18v1dyn_1219.raw'
	BranchGroupDict = makeBranchGroups(planningRaw)
	
	while True:
		searchTerm = raw_input('Enter bus number whose list of ties you are looking for: ')
		if searchTerm in BranchGroupDict.keys():
			for Bus in list(BranchGroupDict[searchTerm.strip()]):
				print Bus
		else:
			print 'Bus has no ties'
	"""
	with open('tmp.txt','w') as f:
		for line in highImpedanceTieList:
			f.write(line)
			f.write('\n')
	"""
