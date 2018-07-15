# check to see if the sort idea to get correct nomv and windv values work. Good news, they do work

from getBusDataFn import getBusData
ThreeWToThreeWSubFile = 'All3wTo3wSubDataCleaned_Mod.txt'
PSSErawFile = 'hls18v1dyn_new.raw'
CAPERaw = 'RAW0620.raw'
changeLog = 'changeBusNoLog.txt'
planningBusDataDict = getBusData(PSSErawFile)
CAPEBusDataDict = getBusData(CAPERaw)
changeNameDictOldToNew = {}



# look at log files which contains all the changed bus numbers in the previous iteration (first time i did this)
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
		changeNameDictOldToNew[OldBus] = NewBus
# get relevant data (no change and 3w->3w cases) from this file
with open(ThreeWToThreeWSubFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if '->' not in line:
			continue
		words = line.split('->')
		CAPEPart = words[0].strip()
		CAPEBus1 = CAPEPart.split(',')[0].strip()
		CAPEBus2 = CAPEPart.split(',')[1].strip()
		CAPEBus3 = CAPEPart.split(',')[2].strip()
		cktID  = CAPEPart.split(',')[3].strip()

		# change to new bus numbers
		if CAPEBus1 in changeNameDictOldToNew.keys():
			CAPEBus1 = changeNameDictOldToNew[CAPEBus1]

		if CAPEBus2 in changeNameDictOldToNew.keys():
			CAPEBus2 = changeNameDictOldToNew[CAPEBus2]

		if CAPEBus3 in changeNameDictOldToNew.keys():
			CAPEBus3 = changeNameDictOldToNew[CAPEBus3]

		CAPEBus1Volt = float(CAPEBusDataDict[CAPEBus1].NominalVolt)
		CAPEBus2Volt = float(CAPEBusDataDict[CAPEBus2].NominalVolt)
		CAPEBus3Volt = float(CAPEBusDataDict[CAPEBus3].NominalVolt)

		CAPEPart =  CAPEBus1 + ',' + CAPEBus2 + ',' + CAPEBus3 + ',' + cktID
		#print CAPEPart
		planningPart = words[1].strip()

		# Add if-else for 3w-3w cases
		planningWords = planningPart.split(',')
		planningBus1 = planningWords[0].strip()
		planningBus2 = planningWords[1].strip()
		planningBus3 = planningWords[2].strip()

		planningBus1Volt = float(planningBusDataDict[planningBus1].NominalVolt)
		planningBus2Volt = float(planningBusDataDict[planningBus2].NominalVolt)
		planningBus3Volt = float(planningBusDataDict[planningBus3].NominalVolt)

		bus1VoltDiff  = abs((planningBus1Volt - CAPEBus1Volt)/planningBus1Volt)*100
		bus2VoltDiff  = abs((planningBus2Volt - CAPEBus2Volt)/planningBus2Volt)*100
		bus3VoltDiff  = abs((planningBus3Volt - CAPEBus3Volt)/planningBus3Volt)*100

		if bus1VoltDiff > 1 or bus2VoltDiff >1 or bus3VoltDiff > 1:
			print CAPEPart + ' -> ' +  planningPart
