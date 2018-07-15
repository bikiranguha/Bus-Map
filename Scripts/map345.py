"""
 use the verified mapping of the 345 system to generate 345 kV bus data
"""

from mapAndcopyGen import MapDict,PSSEBusSet, CAPEBusSet
from getBranchGroupFn import makeBranchGroups
PSSEMap = 'PSSE345Mapverified.txt' # verified 345 kV bus map data
CAPEBranchGroupFile = 'branchGroupv3.txt' # groups of buses which are basically sub-sections of the same bus
CAPERaw = 'MASTER_CAPE_Fixed.raw'
BranchGroupDict = makeBranchGroups(CAPERaw)


# open the 345 map and generate a dictionary of PSSE->CAPE maps, also generate sets of PSSE and CAPE buses to be mapped
with open(PSSEMap,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		words = line.split(',')
		if len(words) <2:
			continue
		PSSEBus = words[0].strip()
		CAPEBus = words[5].strip()

		if CAPEBus not in CAPEBusSet: # if CAPE bus not already mapped
			if PSSEBus not in PSSEBusSet: 
				PSSEBusSet.add(PSSEBus)
			MapDict[CAPEBus] = PSSEBus 
			CAPEBusSet.add(CAPEBus) # log that the CAPE Bus has been mapped

			if CAPEBus in BranchGroupDict.keys(): # CAPE Bus has ties
				# Map all ties to the same bus
				BusGroupSet = BranchGroupDict[CAPEBus]
				for Bus in list(BusGroupSet):
					MapDict[Bus] = PSSEBus
					CAPEBusSet.add(CAPEBus)

#print len(CAPEBusSet)