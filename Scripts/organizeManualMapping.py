# make a dict of the mapping done in mapping_priority1
# look at the mappings done in manual_map_compile.txt
	# if the current mapping is already done in mapping_priority1, skip
	# if the left-hand bus is in the planning case, just go ahead and add the line
	# else, get the mapping from AllMappedBusLog and then update the line and add
	# if the bus on the right is present in the dict generated here, then skip the line


mapping_priority1 = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/' + 'mapping_priority1.txt'

mapping_priority1_new = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/' + 'mapping_priority1new.txt'
AllMapFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/' + 'AllMappedLog.txt'
manual_map_comp = 'manual_map_compile.txt'
planningRaw = 'hls18v1dyn_new.raw'
mappedCAPESetNew = set() # set of CAPE buses which have been mapped in the manual maps being searched here, with all bus no adhering to the latest Raw file
mappedCAPESetOriginal = set() # set of CAPE buses which have been mapped in the manual maps being searched here, with all bus no adhering to the original Raw file
planningComedBusSet = set()

MappingDictOriginal = {} # keys are original CAPE buses
MappingDictNew = {} # keys are original planning buses
MapDict = {} # dict from AllMapFile
mapLinestoAdd = []
# assemble all the data in mapping_priority1
with open(mapping_priority1,'r') as f:
	originalManualMapContents = f.read()
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		if '->' not in line: # skip header
			continue
		words = line.split('->')
		LHSBus = words[0].strip()
		RHSBus  = words[1].strip()
		if '[' in RHSBus:
			splitOldNew = RHSBus.split('[')
			NewBusNo = splitOldNew[0].strip()
			OldBusNo = splitOldNew[1].strip(']')
			mappedCAPESetNew.add(NewBusNo)
			mappedCAPESetOriginal.add(OldBusNo)
			MappingDictNew[NewBusNo] = LHSBus
			MappingDictOriginal[OldBusNo] = LHSBus
		else:
			mappedCAPESetNew.add(RHSBus)
			mappedCAPESetOriginal.add(RHSBus)
			MappingDictNew[RHSBus] = LHSBus



# get all the previous mapped data 
with open(AllMapFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'CAPE' in line:
			continue

		words = line.split('->')
		if len(words) < 2:
		    continue
		PSSEBus = words[0].strip()
		CAPEBus = words[1].strip()
		MapDict[CAPEBus] = PSSEBus 

# get the set of planning comed buses
with open(planningRaw, 'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if ('PSS' in line) or ('COMED' in line) or ('DYNAMICS' in line):
			continue
		if 'END OF BUS DATA' in line:
			break
		words = line.split(',')
		if len(words) <2:
			continue
		Bus = words[0].strip()
		area = words[4].strip()
		if area == '222':
			planningComedBusSet.add(Bus)


	
# assemble all the data in manual_map_compile
with open(manual_map_comp,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		if '->' not in line: # skip header
			continue
		words = line.split('->')
		LHS = words[0].strip()
		RHS  = words[1].strip()

		# take care of any parentheses
		if '[' in LHS:
			LHSBus = LHS.split('[')[1].strip(']') # get the part in brackets, since it will be used to get mapping
			
		else:
			LHSBus = LHS

		
		if '[' in RHS:
			RHSBusNew = RHS.split('[')[0].strip()
			RHSBusOld = RHS.split('[')[1].strip(']')
			RHSBus = RHSBusOld
		else:
			RHSBus = RHS

		if RHSBus in mappedCAPESetOriginal:
			print 'Mapping exists already: ', line
			continue

		if LHSBus in planningComedBusSet:
			mapLinestoAdd.append(line)
		else: # LHS is a CAPE comed bus
			ActualLHS = MapDict[LHSBus] # The planning Bus
			newLine = ActualLHS + '->' + RHS
			mapLinestoAdd.append(newLine)


# generate the new complete manual mapping file
with open(mapping_priority1_new,'w') as f:
	f.write(originalManualMapContents)
	f.write('\n')
	for line in mapLinestoAdd:
		f.write(line)
		f.write('\n')


