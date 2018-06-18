"""
Get a list of starting buses and then generate their paths to a 345 bus
The path is found using the CAPENeighbourDict and BFS algorithm
"""
import sys
sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2')
# Data import from other files
from getBusDataFn import getBusData
from generateNeighboursFn import getNeighbours
from Queue import Queue



def generate345PathList(Raw,startBusList):
	# Function to generate the list of paths

	print 'Compiling the neighbour data from the Raw file. May take some time. Please wait.'
	print '\n'
	CAPENeighbourDict = getNeighbours(Raw) # key: any bus in the raw file, value: set of all neighbours (line and tf)
	BusDataDict = getBusData(Raw) # Dict whose values are all the relevant info about any bus, key is the bus itself
	print 'Ok, done!'

	ImpPathDict = {}
	# Use CAPENeighbourDict and BFS to find path from one bus to another. Use the concept given in getNeighboursAtCertainDepthFn
	for startBus in startBusList:
		PathDict = {}
		explored = set()
		#startBus = raw_input('Enter start bus: ')
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
			BusArea = BusDataDict[currentBus].area
			if BusVolt >= 345.0 and not BusName.startswith('T3W') and not BusName.endswith('M') and BusArea == '222': # see if the bus is a legit 345 kV bus
				endBus = currentBus
				break
			NeighBourList = list(CAPENeighbourDict[currentBus])


			explored.add(currentBus)

			for neighbour in NeighBourList:
				try:
					NeighBourArea = BusDataDict[neighbour].area
				except: # probably type 4 bus
					continue
				if NeighBourArea != '222': # go to next neighbour if 
					continue
				if neighbour in explored:
					continue

				if currentBus in PathDict.keys():
					PathDict[neighbour] = PathDict[currentBus] + '->' + neighbour
				else: # if currentBus is the start bus
					PathDict[neighbour] = currentBus + '->' + neighbour
 
				frontier.put(neighbour)

		#print PathDict[endBus]
		ImpPathDict[startBus] = PathDict[endBus]
	
	return ImpPathDict

