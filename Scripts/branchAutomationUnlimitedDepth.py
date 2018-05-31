# starting from a CAPE bus whose mapping is definite, map all its branch neighbours to planning buses. Also use the bus name match dictionary to make sure the match is correct
# for neighbours for which no equivalent match was found, go till a depth of 3 and look for neighbours which belong to the same substation as that of the planning neighbour
# if such a neighbour is found, then try to match the sum of the line impedances in CAPE to that of planning
# for ties in CAPE, map to same planning bus (and to its ties, if any)
# After finding new maps, repeat the same process over them
# Please note that the map generated here should only be used for bus mapping, not load or tf mapping

import sys
sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2')
# Data import from other files
from getBusDataFn import getBusData
from generateBranchNeighboursFn import generateNeighbours # function which generates in-service branch neighbour dictionary given raw file
from getBranchGroupFn import makeBranchGroups as  makeBranchGroupsCAPE # this function will help map any ties to buses which are already mapped
from getNeighboursAtCertainDepthFn import getNeighboursDepthN
from getBusNameDict import BusNum2SubNameDict # value: 345 Planning Bus number, value: corresponding CAPE substation name
from getCAPESubstationDict import SubStationDictNew # key: substation name, value: list of all buses (new bus numbers) belonging to the substation
from Queue import Queue
#from getBranchGroupsPlanning import BranchGroupDictPlanning # needed to look at ties of planning bus for more mapping
from getBranchGroupFnPlanning import makeBranchGroups as makeBranchGroupsPlanning # function to generate a group of ties (including itself) of the bus given as key
######################################


# External files being used
CAPERaw = 'Raw0509.raw'
planningRaw = 'hls18v1dyn_new.raw'
ManualMapFile = 'test_branch_comparison2.txt'



# variables defined in this file
ManualMappingDict = {} # dict constructed from the entries given in the manual map file
autoMapDict = {} # dictionary which generates mapping
autoMappedSet =set()
changeDictNewToOld ={}
changeDictOldToNew = {}
mismatchBusSet345 = set()
noMismatch345Set = set() # set of 345 buses (not including fict midpoints) which show no mismatch
ComedCAPESet345 = set()
MapDict = {} # dict containing all CAPE bus maps (the bus numbers all include the latest numbers, ie, include 75xxxxx and 27xxxxx)
maxDepth = 3 # max depth in CAPE for impedance branch comparison
planningUnmappedList = []
explored = set()
planningExplored = set()
#################################


# get all the ties to buses which have no mismatch
BranchGroupDict = makeBranchGroupsCAPE(CAPERaw) # every value here is a set
#_, BranchDataDictCAPE = generateNeighbours(CAPERaw)
_, BranchDataDictPlanning = generateNeighbours(planningRaw)
BusDataDict = getBusData(CAPERaw)
BranchGroupDictPlanning = makeBranchGroupsPlanning(planningRaw)




def printUsefulMappingOutput(originBus,CAPEneighbour,planningBus,planningNeighbour,searchDepth):
	# output mapping info which helps in checking its validity, originBus: CAPE origin bus, CAPEneighbour: CAPE to bus, planningBus: planning from Bus, planningNeighbour: planning to bus
	# searchDepth: depth from CAPE to and from bus
	print CAPEneighbour + '->' + str(autoMapDict[CAPEneighbour]) + '\t' + planningBus + ',' + planningNeighbour + ',' + originBus + ',' + CAPEneighbour + ',' + str(searchDepth)

def scanNeighbourDepth(MultDepthBranchDataDict,Bus,currentDepth,maxDepth,potentialMaps,autoMappedSet,planningNeighbourZ):
	# scan given depth of CAPEBus neighbours to try and get potentialMaps
	for neighbour in MultDepthBranchDataDict[Bus].toBus:
		# scan every neighbour within maxDepth of CAPEBus
		if currentDepth > maxDepth:
			break

		if neighbour in autoMappedSet:
			continue

		neighbourInd = MultDepthBranchDataDict[Bus].toBus.index(neighbour)
		neighbourDepth = MultDepthBranchDataDict[Bus].depth[neighbourInd]
		if neighbourDepth != currentDepth:
			continue 
		
		CAPEneighbourZ = MultDepthBranchDataDict[Bus].Z[neighbourInd]
		error = abs((planningNeighbourZ - CAPEneighbourZ)/planningNeighbourZ)*100

		if error < 5.0:
			potentialMaps.append(neighbour)

	return potentialMaps

def getProperMapping(potentialMaps, planningNeighbour,searchDepth,originBus,planningBus):
	# handle situations when there is one or more maps
	skip = False
	if len(potentialMaps) == 1:
		CAPEneighbour = potentialMaps[0]
		try:
			planningSubStation = BusNum2SubNameDict[planningNeighbour]
			if CAPEneighbour in SubStationDictNew[planningSubStation]: # names match and impedances match
				frontier.put(CAPEneighbour)
				autoMapDict[CAPEneighbour] = set()
				autoMapDict[CAPEneighbour].add(planningNeighbour)
				# map all ties of planning bus to this CAPE tie as well
				if planningNeighbour in BranchGroupDictPlanning.keys():
					planningTies = list(BranchGroupDictPlanning[planningNeighbour])
					for planningTie in planningTies:
						autoMapDict[CAPEneighbour].add(planningTie)
				#printUsefulMappingOutput(originBus,CAPEneighbour,planningBus,planningNeighbour,searchDepth)
				autoMappedSet.add(CAPEneighbour)
				skip = True
			else:
				print planningNeighbour +  ' is an impedance match but not substation match to ' + CAPEneighbour + ',' + planningBus + ',' + originBus		
		except: 
			print planningNeighbour + ' has no substation info.'
			skip = True
			


	elif len(potentialMaps) > 1:
		# need to determine the right CAPENeighbour using Name and Substation Matching
		# once a mapping is found, add the CAPE neighbour and the planning neighbour into appropriate sets
		try:
			planningSubStation = BusNum2SubNameDict[planningNeighbour]
			for CAPEneighbour in potentialMaps:				
				if CAPEneighbour in SubStationDictNew[planningSubStation]:
					#if CAPEneighbour not in explored and CAPEneighbour in NeighbourSetDepth5:
					if CAPEneighbour not in explored:
						frontier.put(CAPEneighbour)
						autoMapDict[CAPEneighbour] = set()
						autoMapDict[CAPEneighbour].add(planningNeighbour)
						# map all ties of planning bus to this CAPE tie as well
						if planningNeighbour in BranchGroupDictPlanning.keys():
							planningTies = list(BranchGroupDictPlanning[planningNeighbour])
							for planningTie in planningTies:
								autoMapDict[CAPEneighbour].add(planningTie)
						#printUsefulMappingOutput(originBus,CAPEneighbour,planningBus,planningNeighbour,searchDepth)
						autoMappedSet.add(CAPEneighbour)
						break
			skip = True
		except:
			print planningNeighbour + ' has no substation info'
			skip = True


	return skip
#################


# generate a dictionary whose keys are new CAPE bus numbers and whose values are the corresponding CAPE substation names


# testing mapping of branch neighbours using comparison of branch impedances 
# ManualMapFile contains the mappings which have been verified
with open(ManualMapFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		# skip conditions
		#if 'Bus' in line:
		#	continue
		if line == '':
			continue
		##
		words = line.split('->')
		planningBus = words[0].strip()
		CAPEBus = words[1].strip()
		ManualMappingDict[CAPEBus] = [planningBus]

# get a set of all neighbours in a depth of 5 of the CAPE bus which has been manually mapped
for CAPEBus in ManualMappingDict.keys():
	Depth5BranchDataDict = getNeighboursDepthN(CAPEBus,CAPERaw,5)
	NeighbourSetDepth5 = list(set(Depth5BranchDataDict[CAPEBus].toBus)) # convert to set to eliminate any duplicates and then convert back to list


# Frontier will add only those CAPE buses which have a verified mapping
#print CAPEBus
frontier = Queue(maxsize=0)
frontier.put(CAPEBus)
autoMapDict = dict(ManualMappingDict)

# get any ties of the input planning bus
originPlanningBus = autoMapDict[CAPEBus][0] # the planning bus which is mapped to the CAPE bus given in the input file
if originPlanningBus in BranchGroupDictPlanning.keys(): # if the origin planning bus has any ties, map the set to the CAPEBus
	originPlanningTies = BranchGroupDictPlanning[originPlanningBus]
	autoMapDict[CAPEBus] = set(originPlanningTies)



print 'Mapping output format: CAPEMatch->[PlanningMatch]	PlanningTo,PlanningFrom,CAPETo,CAPEFrom,CAPESearchDepth'
print '\n'


# do the BFS like frontier additions
while not frontier.empty():
	# repeat the process of brance impedance matching for all the buses in frontier
	currentBus =  frontier.get()
	frontier.task_done()
	

	BusArea = BusDataDict[currentBus].area

	# skip if not a Comed bus
	if BusArea != '222':
		continue

	# put current bus in explored, so that its branches are not examined more than once
	if currentBus in explored:
		continue
	explored.add(currentBus)
	#print currentBus
	#print currentBus

	# before a bus is mapped, check whether it is in explored. If not, then add to frontier if its in depth of 5 
	# keep track of all the planning branches, so that they are not scanned twice

	# map all the ties of this bus
	#MultDepthBranchDataDict =  getNeighboursDepthN(currentBus,CAPERaw,maxDepth) # dictionary with the currentBus as key and multi-depth branch data as class structure
	mappedPlanningNeighbour = set() # set of branch neighbours of the planning bus which are yet to be mapped
	#stillToBeMappedPlanningNeighbour = [] # the name says it all
 	
	planningBusSet = autoMapDict[currentBus] # group of planning buses, if they are part of ties
	currentBusGroup = set() # list of buses belonging to the tie group 
	currentBusGroup.add(currentBus)
	for planningBus in list(planningBusSet):
		try: # see if there are any ties to this bus
			CAPEBranchTies = list(BranchGroupDict[currentBus]) # get a list of all the ties, including the currentBus itself
			for tie in CAPEBranchTies:
				if tie != currentBus:
					#if tie not in explored and tie in NeighbourSetDepth5:
					if tie not in explored:
						frontier.put(tie)
						# add to all the relevant tracking sets
						currentBusGroup.add(tie)
						autoMappedSet.add(tie)
						#explored.add(tie)
						###
						autoMapDict[tie] = set()
						autoMapDict[tie].add(planningBus)
						# map all ties of planning bus to this CAPE tie as well
						if planningBus in BranchGroupDictPlanning.keys():
							planningTies = list(BranchGroupDictPlanning[planningBus])
							for planningTie in planningTies:
								autoMapDict[tie].add(planningTie)
						#print tie + '->' + str(autoMapDict[tie]) + ',' + 'Tie to  Bus:' + originBus
						
		except: # no ties to this bus
			pass

			#############
	# search by depth
	#print planningBus

		PlanningBranchList = BranchDataDictPlanning[planningBus].toBus # get all the branches

		for planningNeighbour in PlanningBranchList: # try to get a mapping of all planningBus neighbours
			#print planningNeighbour

			# keep track of planning branches being scanned
			planningBranchStr = planningBus + ',' + planningNeighbour
			planningBranchStrReverse = planningNeighbour + ',' + planningBus

			if planningBranchStr in planningExplored:
				continue

			planningExplored.add(planningBranchStr)
			planningExplored.add(planningBranchStrReverse)
			###

			for Bus in list(currentBusGroup): # search for matches for this planning branch with every branch in the CAPE bus group
				currentDepth = 1 # initial depth
				potentialMaps = []
				MultDepthBranchDataDict =  getNeighboursDepthN(Bus,CAPERaw,maxDepth)
				planningNeighbourInd = PlanningBranchList.index(planningNeighbour)
				PlanningBranchZ = BranchDataDictPlanning[planningBus].Z[planningNeighbourInd]
				potentialMaps =  scanNeighbourDepth(MultDepthBranchDataDict,Bus,currentDepth,maxDepth,potentialMaps,autoMappedSet,PlanningBranchZ)
				skip = getProperMapping(potentialMaps, planningNeighbour,1,Bus,planningBus)
				if skip == True: # found proper map, break out of this loop and go to investigate the next planning branch
					break

				# no match found in depth 1, continue to depth 2
				currentDepth +=1
				potentialMaps =  scanNeighbourDepth(MultDepthBranchDataDict,Bus,currentDepth,maxDepth,potentialMaps,autoMappedSet,PlanningBranchZ)
				skip = getProperMapping(potentialMaps, planningNeighbour,2,Bus,planningBus)
				if skip == True: # found proper map, break out of this loop and go to investigate the next planning branch
					break

				# no match found in depth 2, continue to depth 3
				currentDepth +=1
				potentialMaps =  scanNeighbourDepth(MultDepthBranchDataDict,Bus,currentDepth,maxDepth,potentialMaps,autoMappedSet,PlanningBranchZ)
				skip = getProperMapping(potentialMaps, planningNeighbour,3,Bus,planningBus)
				if skip == True: # found proper map, break out of this loop and go to investigate the next planning branch
					break
			####

			if skip == True: # found match, dont need to add this branch to the unmapped planning neigbours
				continue
			# no match found, add planningBus and planningNeighbour combo
			combo = planningBus + ',' + planningNeighbour
			planningUnmappedList.append(combo)	


print 'List of mappings found by script ([PlanningBus] -> [CAPEBus]'
for key in autoMapDict.keys():
	string  = str(autoMapDict[key]) + '->' + key
	print string

"""
print '\n\n'

# get a list of all the unmapped buses
print 'List of buses not mapped yet within a depth of 5 of the CAPE bus provided in input file:'
unmappedCount = 0
for n in list(NeighbourSetDepth5):
	if n not in autoMappedSet:
		print n
		unmappedCount +=1
"""

print '\n\n'
print 'Number of neighbours mapped: ', len(autoMappedSet)
#print 'Number of neigbours not yet mapped: ', unmappedCount
print '\n\n'
print 'Please note that the map generated here should only be used for bus mapping, not load or tf mapping'


