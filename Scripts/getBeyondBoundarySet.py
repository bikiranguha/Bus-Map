"""
Apply Breadth First search algorithm to get all non-comed buses in CAPE raw file. Any associated data of these buses should not 
be added to the merged raw file
"""

from Queue import Queue
#from generateBranchNeighboursOutEvenFn import getBranchNeighbours
from getBusDataFn import getBusData
from generateNeighboursFn import getNeighbours
CAPERaw = 'MASTER_CAPE_Fixed.raw'
#CAPERaw = 'CAPE_RAW1116v33.raw'
boundaryFile = 'BoundaryplanningMapCleaned.txt' # Cleaned boundary maps to initialize searching points
boundarynoncomed = 'BoundaryNonComedv3.txt' # List of buses on the non-comed side of the boundary
outsideComedBuses = 'outsideComedBusesv4.txt' # generate a set of buses on the outside of comed area
hiddenboundaryList = 'hiddenboundarylistv4.txt'
ManuallyAddedList = ['50123','50124','50122','3039','757'] # list of buses to be manually added to outside comed buses
BoundaryList = [] # fill this up
nonComedBoundarySet = set()
explored = []
hiddenboundary = set()
BranchNeighbourDict = getNeighbours(CAPERaw)
BusDict = getBusData(CAPERaw)

# file contains CAPE boundary info
with open(boundaryFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		words = line.split('->')
		if len(words) < 2:
			continue
		CAPEWords = words[1].split(',')
		CAPEBoundary = CAPEWords[0].strip()
		BoundaryList.append(CAPEBoundary)



# file contains info for non-comed boundary info
with open(boundarynoncomed,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'Boundary' in line: # skip header
			continue
		words = line.split('->')
		if len(words) < 2:
			continue
		nonComedBoundary = words[1].strip()
		nonComedBoundarySet.add(nonComedBoundary)





# Breadth first search algorithm to find out all non-comed buses in CAPE
frontier = Queue(maxsize=0)
for bus in list(nonComedBoundarySet):
	frontier.put(bus)

while not frontier.empty():
	currentBus =  frontier.get()
	frontier.task_done()
	NeighbourBus = list(BranchNeighbourDict[currentBus])
	if currentBus not in explored:
		explored.append(currentBus)
	for neighbour in NeighbourBus:
		if neighbour not in BoundaryList:
				if neighbour not in explored:
					area = BusDict[neighbour].area
					if area not in ['1','0']:
						frontier.put(neighbour)
					else:
						hiddenboundary.add(neighbour)

with open(outsideComedBuses,'w') as f:
	for Bus in explored:
		f.write(Bus)
		f.write('\n')

	f.write('Manually added:')
	f.write('\n')
	for Bus in ManuallyAddedList:
		f.write(Bus)
		f.write('\n')

with open(hiddenboundaryList,'w') as f:
	for Bus in list(hiddenboundary):
		f.write(Bus)
		f.write('\n')




