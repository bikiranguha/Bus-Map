"""
Find path from any bus to a 345 bus (branch or TF using BFS)
"""
import sys
sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2')
# Data import from other files
from getBusDataFn import getBusData
from generateNeighboursFn import getNeighbours
from Queue import Queue

CAPERaw = 'RAW0602.raw'
print 'Compiling the neighbour data from the Raw file. May take some time. Please wait.'
print '\n'
CAPENeighbourDict = getNeighbours(CAPERaw)
BusDataDict = getBusData(CAPERaw)
print 'Ok, done!'


# Use CAPENeighbourDict and BFS to find path from one bus to another. Use the concept given in getNeighboursAtCertainDepthFn
while True:
	PathDict = {}
	explored = set()
	startBus = raw_input('Enter start bus: ')
	#endBus = raw_input('Enter end bus: ')



	frontier = Queue(maxsize=0)
	frontier.put(startBus)

	while not frontier.empty():
		currentBus = frontier.get()
		frontier.task_done()
		#if currentBus == endBus:
		#	break

		BusVolt = float(BusDataDict[currentBus].NominalVolt)
		BusName = BusDataDict[currentBus].name
		if BusVolt >= 345.0 and not BusName.startswith('T3W') and not BusName.endswith('M') : # see if the bus is a legit 345 kV bus
			endBus = currentBus
			break
		NeighBourList = list(CAPENeighbourDict[currentBus])


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

