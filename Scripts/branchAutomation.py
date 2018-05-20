# starting from a CAPE bus whose mapping is definite, map all its branch neighbours to planning buses. Also use the bus name match dictionary to make sure the match is correct
# for neighbours for which no equivalent match was found, go to a depth of 2 and look for neighbours which belong to the same substation as that of the planning neighbour
# if such a neighbour is found, then try to match the sum of the line impedances in CAPE to that of planning
# if branch impedance values are small, map those buses to the same planning bus
# Please note that the map generated here should only be used for bus mapping, not load or tf mapping

# Data import from other files
from generateBranchNeighboursFn import generateNeighbours # function which generates in-service branch neighbour dictionary given raw file
from getBranchGroupFn import makeBranchGroups # this function will help map any ties to buses which are already mapped
from getNeighboursAtCertainDepthFn import getNeighboursDepthN
from getBusNameDict import BusNum2SubNameDict # value: 345 Planning Bus number, value: corresponding CAPE substation name
from getCAPESubstationDict import SubStationDictNew # key: substation name, value: list of all buses (new bus numbers) belonging to the substation
######################################


# External files being used
CAPERaw = 'Raw0509.raw'
planningRaw = 'hls18v1dyn_new.raw'
ManualMapFile = 'test_branch_comparison.txt'
sortedMismatchData345 = 'sortedMismatchData345.txt'
mapping_priority1 = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/' + 'mapping_priority1.txt'
AllMapFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/' + 'AllMappedLog.txt'



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
maxDepth = 3
planningUnmappedList = []
#################################


# get all the ties to buses which have no mismatch
BranchGroupDict = makeBranchGroups(CAPERaw) # every value here is a set
#_, BranchDataDictCAPE = generateNeighbours(CAPERaw)
_, BranchDataDictPlanning = generateNeighbours(planningRaw)




def scanNeighbourDepth(MultDepthBranchDataDict,CAPEBus,currentDepth,maxDepth,potentialMaps,autoMappedSet,planningNeighbourZ):
	# scan given depth of CAPEBus neighbours to try and get potentialMaps
	for neighbour in MultDepthBranchDataDict[CAPEBus].toBus:
		# scan every neighbour within maxDepth of CAPEBus
		if currentDepth > maxDepth:
			break

		if neighbour in autoMappedSet:
			continue

		neighbourInd = MultDepthBranchDataDict[CAPEBus].toBus.index(neighbour)
		neighbourDepth = MultDepthBranchDataDict[CAPEBus].depth[neighbourInd]
		if neighbourDepth != currentDepth:
			continue 
		
		CAPEneighbourZ = MultDepthBranchDataDict[CAPEBus].Z[neighbourInd]
		error = abs((planningNeighbourZ - CAPEneighbourZ)/planningNeighbourZ)*100

		if error < 2.0:
			potentialMaps.append(neighbour)

	return potentialMaps

def getProperMapping(potentialMaps, planningNeighbour):
	# handle situations when there is one or more maps
	skip = False
	if len(potentialMaps) == 1:
		CAPEneighbour = potentialMaps[0]
		autoMapDict[CAPEneighbour] = planningNeighbour
		autoMappedSet.add(CAPEneighbour)

		try:
			planningSubStation = BusNum2SubNameDict[planningNeighbour]
			if CAPEneighbour not in SubStationDictNew[planningSubStation]:
				print planningNeighbour ' is an impedance match but not substation match to ' + CAPEneighbour
				skip = True
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
					autoMapDict[CAPEneighbour] = planningNeighbour
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
		ManualMappingDict[CAPEBus] = planningBus

for CAPEBus in ManualMappingDict.keys():
	# map all the ties of this bus

	#exploredCAPENeighbours = set() # set of buses while mapping neighbours of CAPEBus
	#exploredCAPENeighbours.add(CAPEBus)
	MultDepthBranchDataDict =  getNeighboursDepthN(CAPEBus,CAPERaw,maxDepth) # dictionary with the CAPEBus as key and multi-depth branch data as class structure
	mappedPlanningNeighbour = set() # set of branch neighbours of the planning bus which are yet to be mapped
	stillToBeMappedPlanningNeighbour = [] # the name says it all
 	CAPEBranchTies = list(BranchGroupDict[CAPEBus]) # get a list of all the ties, including the CAPEBus itself
	planningBus = ManualMappingDict[CAPEBus] 
	for tie in CAPEBranchTies:
		if tie != CAPEBus:
			autoMapDict[tie] = planningBus 
			autoMappedSet.add(tie)
	#############
	# search by depth
	#currentDepth = 1
	
	PlanningBranchList = BranchDataDictPlanning[planningBus].toBus # get all the branches

	for planningNeighbour in PlanningBranchList: # try to get a mapping of all planningBus neighbours
		currentDepth = 1 # initial depth
		potentialMaps = []
		planningNeighbourInd = PlanningBranchList.index(planningNeighbour)
		PlanningBranchZ = BranchDataDictPlanning[planningBus].Z[planningNeighbourInd]
		potentialMaps =  scanNeighbourDepth(MultDepthBranchDataDict,CAPEBus,currentDepth,maxDepth,potentialMaps,autoMappedSet,PlanningBranchZ)

		if len(potentialMaps) == 1:
			CAPEneighbour = potentialMaps[0]
			autoMapDict[CAPEneighbour] = planningNeighbour
			autoMappedSet.add(CAPEneighbour)

			try:
				planningSubStation = BusNum2SubNameDict[planningNeighbour]
			except:
				print planningNeighbour + ' has no substation info.'
				continue

			if CAPEneighbour not in SubStationDictNew[planningSubStation]:
				print planningNeighbour
			#mappedPlanningNeighbour.add(planningNeighbour)
			continue # move to next planning neighbour
		elif len(potentialMaps) > 1:
			# need to determine the right CAPENeighbour using Name and Substation Matching
			# once a mapping is found, add the CAPE neighbour and the planning neighbour into appropriate sets
			try:
				planningSubStation = BusNum2SubNameDict[planningNeighbour]
			except:
				print planningNeighbour + ' has no substation info'
				continue

			SubStationDictNew[planningSubStation]
			for CAPEneighbour in potentialMaps:				
				if CAPEneighbour in SubStationDictNew[planningSubStation]:
					autoMapDict[CAPEneighbour] = planningNeighbour
					autoMappedSet.add(CAPEneighbour)
					break
			continue

		# no match found in depth 1, continue to depth 2
		currentDepth +=1
		potentialMaps =  scanNeighbourDepth(MultDepthBranchDataDict,CAPEBus,currentDepth,maxDepth,potentialMaps,autoMappedSet,PlanningBranchZ)

		if len(potentialMaps) == 1:
			CAPEneighbour = potentialMaps[0]
			autoMapDict[CAPEneighbour] = planningNeighbour
			autoMappedSet.add(CAPEneighbour)

			try:
				planningSubStation = BusNum2SubNameDict[planningNeighbour]
			except:
				print planningNeighbour + ' has no substation info'
				continue

			if CAPEneighbour not in SubStationDictNew[planningSubStation]:
				print planningNeighbour

			#mappedPlanningNeighbour.add(planningNeighbour)
			continue # move to next planning neighbour
		elif len(potentialMaps) > 1:
			# need to determine the right CAPENeighbour using Name and Substation Matching
			# once a mapping is found, add the CAPE neighbour and the planning neighbour into appropriate sets
			try:
				planningSubStation = BusNum2SubNameDict[planningNeighbour]
			except:
				print planningNeighbour + ' has no substation info'
				continue

			for CAPEneighbour in potentialMaps:				
				if CAPEneighbour in SubStationDictNew[planningSubStation]:
					autoMapDict[CAPEneighbour] = planningNeighbour
					autoMappedSet.add(CAPEneighbour)
					break
			continue

		# no match found in depth 2, continue to depth 3
		currentDepth +=1
		potentialMaps =  scanNeighbourDepth(MultDepthBranchDataDict,CAPEBus,currentDepth,maxDepth,potentialMaps,autoMappedSet,PlanningBranchZ)

		if len(potentialMaps) == 1:
			CAPEneighbour = potentialMaps[0]
			autoMapDict[CAPEneighbour] = planningNeighbour
			autoMappedSet.add(CAPEneighbour)

			try:
				planningSubStation = BusNum2SubNameDict[planningNeighbour]
			except:
				print planningNeighbour + ' has no substation info'
				continue

			if CAPEneighbour not in SubStationDictNew[planningSubStation]:
				print planningNeighbour
			#mappedPlanningNeighbour.add(planningNeighbour)
			continue # move to next planning neighbour
		elif len(potentialMaps) > 1:
			# need to determine the right CAPENeighbour using Name and Substation Matching
			# once a mapping is found, add the CAPE neighbour and the planning neighbour into appropriate sets
			try:
				planningSubStation = BusNum2SubNameDict[planningNeighbour]
			except:
				print planningNeighbour + ' has no substation info'
				continue
			SubStationDictNew[planningSubStation]
			for CAPEneighbour in potentialMaps:				
				if CAPEneighbour in SubStationDictNew[planningSubStation]:
					autoMapDict[CAPEneighbour] = planningNeighbour
					autoMappedSet.add(CAPEneighbour)
					break
			continue

		# no match found, add planningBus and planningNeighbour combo
		combo = planningBus + ',' + planningNeighbour
		planningUnmappedList.append(combo)




	"""
	# compare all branch neighbours
	CAPEBranchList = BranchDataDictCAPE[CAPEBus].toBus
	CAPEBranchZ  = BranchDataDictCAPE[CAPEBus].Z

	planningBus = ManualMappingDict[CAPEBus]

	PlanningBranchList = BranchDataDictPlanning[planningBus].toBus
	PlanningBranchZ  = BranchDataDictPlanning[planningBus].Z



	for i in range(len(PlanningBranchList)):
		# scan planning neighbours
		planningNeighbour = PlanningBranchList[i]
		planningNeighbourZ = PlanningBranchZ[i]
		#exploredCAPENeighbours.add(neighbour)
		potentialMaps = []

		for j in range(len(CAPEBranchList)):
			CAPEneighbour = CAPEBranchList[j]
			# CAPE bus already mapped
			if CAPEneighbour in autoMappedSet:
				continue

			CAPEneighbourZ = CAPEBranchZ[j]
			error = abs((planningNeighbourZ - CAPEneighbourZ)/planningNeighbourZ)*100

			if error < 2.0:
				potentialMaps.append(CAPEneighbour)

		if len(potentialMaps) == 1:
			CAPEneighbour = potentialMaps[0]
			autoMapDict[CAPEneighbour] = planningNeighbour
			autoMappedSet.add(CAPEneighbour)
			mappedPlanningNeighbour.add(planningNeighbour)
		elif len(potentialMaps) > 1:
			# need to determine the right CAPENeighbour using Name and Substation Matching
			# once a mapping is found, add the CAPE neighbour and the planning neighbour into appropriate sets
			pass


	# get the unmapped planning neighbours
	for planningBranch in PlanningBranchList:
		if planningBranch not in mappedPlanningNeighbour:
			stillToBeMappedPlanningNeighbour.append(planningNeighbour)
			# search the corresponding branch impedance in depth 2 and see if there is a match
			# if there is a match, that depth 2 neighbour of CAPEBus should be mapped to this planning neighbour
	"""








	"""
	for i in range(len(CAPEBranchList)):
		# scan CAPE neighbours
		neighbour = CAPEBranchList[i]
		exploredCAPENeighbours.add(neighbour)
		neighbourZ = CAPEBranchZ[i]
		potentialMaps = []
		# for each CAPE neighbour, scan all planning neighbours to get a branch impedance match
		for j in range(len(PlanningBranchList)):
			planningNeighbour = PlanningBranchList[j]
			planningNeighbourZ = PlanningBranchZ[j]
			error = abs((planningNeighbourZ - neighbourZ)/planningNeighbourZ)*100

			if error < 2.0:
				potentialMaps.append(planningNeighbour)
				#autoMapDict[neighbour] = planningNeighbour
				#autoMappedSet.add(neighbour)
				#break
		if len(potentialMaps) == 1:
			autoMapDict[neighbour] = potentialMaps[0]
			autoMappedSet.add(potentialMaps[0])

		elif len(potentialMaps) > 1:
			# need to match using the nameMatchDict
			pass
		elif len(potentialMaps) == 0: 
			# search in a depth of 2
			n2List = BranchDataDictCAPE[neighbour].toBus # depth 2 neighbours of CAPEBus
			n2ZList = BranchDataDictCAPE[neighbour].Z # depth 2 neighbour branch impedance info
			for k in range(len(n2List)):
				n2 = n2List[k]
				if n2 in exploredCAPENeighbours or n2 in autoMappedSet:
					continue
				n2Z = n2ZList[k]
				totalCAPEZ = neighbourZ + n2Z
				error = abs((planningNeighbourZ - totalCAPEZ)/planningNeighbourZ)*100

				if error < 2.0:
					potentialMaps.append(planningNeighbour)

	"""





print 'Please note that the map generated here should only be used for bus mapping, not load or tf mapping'


