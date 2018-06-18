"""
Find path from one bus to another (branch or TF using BFS)
"""

from generateNeighboursFn import getNeighbours
from Queue import Queue

CAPERaw = 'RAW0602.raw'
print 'Compiling the neighbour data from the Raw file. May take some time. Please wait.'
print '\n'
CAPENeighbourDict = getNeighbours(CAPERaw)
print 'Ok, done!'


# Use CAPENeighbourDict and BFS to find path from one bus to another. Use the concept given in getNeighboursAtCertainDepthFn
while True:
	PathDict = {}
	explored = set()
	startBus = raw_input('Enter start bus: ')
	endBus = raw_input('Enter end bus: ')



	frontier = Queue(maxsize=0)
	frontier.put(startBus)

	while not frontier.empty():
		currentBus = frontier.get()
		frontier.task_done()
		if currentBus == endBus:
			break
		NeighBourList = list(CAPENeighbourDict[currentBus])

		#if currentBus in explored:
		#	continue
		explored.add(currentBus)

		for neighbour in NeighBourList:
			if neighbour in explored:
				continue

			if currentBus in PathDict.keys():
				PathDict[neighbour] = PathDict[currentBus] + '->' + neighbour
			else: # if currentBus is the start bus
				PathDict[neighbour] = currentBus + '->' + neighbour

			frontier.put(neighbour)

	print PathDict[endBus]

