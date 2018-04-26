"""

Script which tries to solve some of the problems which occur in the CAPE three winder to PSSE two winder maps
The main issue is that of multiple mappings of the same planning 2 winder
The manual map file is used for reference here
ThreetoTwoWinderManualMap.txt contains the new maps of the CAPE three winders
ThreetoTwoWinderNewIsssues.txt lists the new issues. Any bus which has no map has been labeled as 0.

"""


mapFile = 'mapped_buses_cleaned0313.csv'
OldtfReplaceFile = 'threetoTwoWinderAuto.txt'
changeLog = 'changeBusNoLog.txt'
newtfReplaceFile = 'ThreetoTwoWinderManualMap.txt' # new file, which will contain the new maps
newIssueFile = 'ThreetoTwoWinderNewIsssues.txt'

ManualMapDict = {} # maps which have been done manually
CAPEBusSet = set()
oldNoDict = {} # key: changed CAPE bus no., value: original CAPE bus no.
newMapLines = [] # new lines, to be written to file
issueLines = [] # lines which need to be investigated manually
includedPlanningSet = set() # set to keep track of planning tf which are being included already
# open the simple map and generate a dictionary of PSSE->CAPE maps, also generate sets of PSSE and CAPE buses to be mapped
with open(mapFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		words = line.split(',')
		if len(words) <2:
			continue
		PSSEBus = words[0].strip()
		CAPEBus = words[5].strip()
		PSSEBusCode = words[2].strip()
		#if CAPEBus in noNeedtoMapSet:
		#	#print CAPEBus
		#	continue
		if 'M' in PSSEBusCode:
			continue
		if PSSEBus in ['NA','']:
			continue
		if CAPEBus in ['NA','']:
			continue
		if CAPEBus in CAPEBusSet: #already mapped in Gen345 Mapping
			print CAPEBus
			continue
		else:
			ManualMapDict[CAPEBus] = PSSEBus 

# look at log files which contains all the changed bus number
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
		#OldBusSet.add(OldBus)
		#NewBusSet.add(NewBus)
		oldNoDict[NewBus] = OldBus
		#newNoDict[OldBus] = NewBus

# look at the CAPE cases and generate new 2 winder tf replacements
with open(OldtfReplaceFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'CAPE' in line:
			continue
		words = line.split('->')
		if len(words) <2:
			continue

		# extract the CAPE bus info
		CAPEPart = words[0].split(',')
		Bus1 = CAPEPart[0].split('[')
		Bus1 = Bus1[0].strip() # the new CAPE bus numbers
		if Bus1 in oldNoDict.keys():
			originalBus1 = oldNoDict[Bus1] # original CAPE bus numbers
		else:
			originalBus1 = Bus1

		Bus2 = CAPEPart[1].split('[')
		Bus2 = Bus2[0].strip()
		if Bus2 in oldNoDict.keys():
			originalBus2 = oldNoDict[Bus2]
		else:
			originalBus2 = Bus2

		Bus3 = CAPEPart[2].split('[')
		Bus3 = Bus3[0].strip()
		if Bus3 in oldNoDict.keys():
			originalBus3 = oldNoDict[Bus3]
		else:
			originalBus3 = Bus3

		# generate the  new PSSE 2w tf maps
		if originalBus1 in ManualMapDict.keys():
			planningBus1 = ManualMapDict[originalBus1]
		else:
			planningBus1 = '     0'

		if originalBus2 in ManualMapDict.keys():
			planningBus2 = ManualMapDict[originalBus2]
		else:
			planningBus2 = '     0'

		planningBus3 = '     0' # dont care about the third winder

		CAPESide = Bus1 + ',' + Bus2 + ',' + Bus3
		planningSide = planningBus1 + ',' + planningBus2 + ',' + planningBus3

		# generate new lines
		newLine = CAPESide + '->' + planningSide
		newMapLines.append(newLine)

		if planningBus1.strip() == '0' or planningBus2.strip() == '0':
			issueLines.append(newLine)
			continue

		if planningSide in includedPlanningSet:
			issueLines.append(newLine)
		else:
			includedPlanningSet.add(planningSide)


		#print newLine


with open(newtfReplaceFile,'w') as f:
	for line in newMapLines:
		f.write(line)
		f.write('\n')

with open(newIssueFile,'w') as f:
	for line in issueLines:
		f.write(line)
		f.write('\n')
