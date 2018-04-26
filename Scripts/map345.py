"""
 use the verified mapping of the 345 system to generate 345 kV bus data
"""

from mapAndcopyGen import MapDict,PSSEBusSet, CAPEBusSet

PSSEMap = 'PSSE345Mapverified.txt' # verified 345 kV bus map data
CAPEBranchGroupFile = 'branchGroupv3.txt' # groups of buses which are basically sub-sections of the same bus


groupList = [] # list of the bus group data


# get the bus group data
with open(CAPEBranchGroupFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		words = line.split(',')
		lst = []
		for word in words:
			lst.append(word.strip())
		groupList.append(lst)


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
			for lst in groupList: # add all the buses grouped to it
				if CAPEBus in lst:
					for Bus in lst:
						if Bus!= CAPEBus: # generate key-value pairs for the remaining buses in the group
							MapDict[Bus] = PSSEBus
							CAPEBusSet.add(Bus) 
					break
#print len(CAPEBusSet)