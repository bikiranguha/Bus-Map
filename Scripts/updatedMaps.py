"""
Keeps track of the manual and auto bus mappings using MapDictNew and MapDictOld
First priority is mapping_prirority1 and then AllMappedLog.txt
"""

changeLog = 'changeBusNoLog.txt'
mapping_priority1 =  'mapping_priority1.txt'
AllMapFile ='AllMappedLog.txt'
MapDictNew = {} # keys are new CAPE bus numbers (gen and conflicts are changed)
MapDictOld = {} # keys are old (or original) CAPE bus numbers
changeDictNewToOld = {} # keeps track of new to old changes
changeDictOldToNew = {} # keeps track of old to new changes
manualMapSet = set() # all CAPE buses which have already been mapped

# get all the bus number changes
with open(changeLog,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split('\n')
    for line in fileLines:
        if 'CAPE' in line:
            continue
        words = line.split('->')
        if len(words) < 2:
            continue
        OldBus = words[0].strip()
        NewBus = words[1].strip()
        changeDictNewToOld[NewBus] = OldBus
        changeDictOldToNew[OldBus] = NewBus


# get the updated manual maps

with open(mapping_priority1,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		if '->' not in line: # skip header
			continue
		words = line.split('->')
		LHSBus = words[0].strip() # planning bus
		RHSBus  = words[1].strip() # CAPE bus (new numbering system)
		MapDictNew[RHSBus] = LHSBus
		if RHSBus in changeDictNewToOld.keys():
			OldCAPEBus =  changeDictNewToOld[RHSBus]
			MapDictOld[OldCAPEBus] = LHSBus
			manualMapSet.add(OldCAPEBus)
		else:
			MapDictOld[RHSBus] = LHSBus
			manualMapSet.add(RHSBus)

# get the auto maps only if they dont exist in the manual (priority 1 maps)
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
		OldCAPEBus = words[1].strip()
		if OldCAPEBus in manualMapSet:
			continue
		if OldCAPEBus in changeDictOldToNew.keys():
			NewCAPEBus = changeDictOldToNew[OldCAPEBus]
		else:
			NewCAPEBus = OldCAPEBus

		MapDictNew[NewCAPEBus] = PSSEBus
		MapDictOld[OldCAPEBus] = PSSEBus



		
		


