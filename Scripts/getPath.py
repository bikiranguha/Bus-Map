"""
Script to get path from one bus to another bus (within a prespecified depth)
"""

CAPERaw = 'Raw0509.raw'
from getNeighboursAtCertainDepthFn import getNeighboursDepthN
while True:
	OriginBus = raw_input('Please enter the origin bus: ').strip()
	endBus = raw_input('Please enter the end bus: ').strip()
	searchDepth = int(raw_input('Search depth: '))


	tmpData = getNeighboursDepthN(OriginBus,CAPERaw,searchDepth)
	try:
		toBusInd = tmpData[OriginBus].toBus.index(endBus)

		print 'Path:'
		P = tmpData[OriginBus].Path[toBusInd]
		print P
		print '\n\n\n'
	except ValueError:
		print 'No bus found in specified searchDepth, please try again! \n'

	