"""
Output all the 3 winder substitutions in proper format from oldGenAndMidPtSubFile
Output all the midpoint data from the same file
"""


from getTFDataFn import getTFData
from getBusDataFn import getBusData
planningRaw = 'hls18v1dyn_new.raw'
newMidPointList = 'MidPointBusesAdded.txt'
MidpointSet = set()
MidPtTMap = {} # key: Midpoint, value: set of its connections
MidPtIDMap = {} # key: Midpoint, value: csv of its tf IDs
oldGenAndMidPtSubFile = 'genAndMidpoint3wMaps.txt'
Comed3WinderPlanningDict = {}
planningBusDataDict = getBusData(planningRaw)
planningTFDataDict = getTFData(planningRaw)



# get the set of planning midpoint buses imported into the merged raw file
with open(newMidPointList,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		words = line.split(',')
		Bus = words[0].strip()
		MidpointSet.add(Bus)

# using the tf data function, create a tmap for these midpoints
for Midpoint in list(MidpointSet):
	tfN = planningTFDataDict[Midpoint].toBus
	MidPtTMap[Midpoint] = set(tfN)


# read planning raw file and a dictionary of all the comed 3 winders, with the set of its 3 buses as value
with open(planningRaw,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split("\n")


# build a dictionary of comed transformer (relevant) data to be substituted into CAPE data
tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')
# generate a dictionary from the planning data, values are relevant tf info
i = tfStartIndex
while i < tfEndIndex:
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	Bus3 = words[2].strip()
	cktID = words[3].strip()
	key = Bus1+','+Bus2+','+Bus3+','+cktID
	if Bus3 == '0': # dont care about 2 winders
		if Bus1 in MidpointSet:
			key = Bus1.rjust(6)+','+Bus2.rjust(6)+','+Bus3.rjust(6)+','+cktID 
			if Bus1 not in MidPtIDMap.keys(): # first time addition
				MidPtIDMap[Bus1] = key
			else: 
				MidPtIDMap[Bus1] += ',' + key

		if Bus2 in MidpointSet:
			key = Bus1.rjust(6)+','+Bus2.rjust(6)+','+Bus3.rjust(6)+','+cktID 
			if Bus2 not in MidPtIDMap.keys(): # first time addition
				MidPtIDMap[Bus2] = key
			else: 
				MidPtIDMap[Bus2] += ',' + key
		i+=4
		continue


	else: # three winder
		Bus1Area = planningBusDataDict[Bus1].area 
		if Bus1Area == '222':
			tfSet = set([Bus1,Bus2,Bus3])
			Comed3WinderPlanningDict[key] = tfSet

		i+=5


with open(oldGenAndMidPtSubFile,'r') as f:

	filecontent = f.read()
	fileLines = filecontent.split("\n")
	for line in fileLines:
		if '->' not in line:
			continue
		words = line.split('->')
		CAPEPart = words[0].strip()
		CAPEWords = CAPEPart.split(',')
		CAPEBus1 = CAPEWords[0].strip()
		CAPEBus2 = CAPEWords[1].strip()
		CAPEBus3 = CAPEWords[2].strip()
		cktID = CAPEWords[3].strip()
		CAPEPart = CAPEBus1.rjust(6)+','+CAPEBus2.rjust(6)+','+CAPEBus3.rjust(6)+','+cktID 

		planningPart = words[1].strip()
		planningBuses = planningPart.split(',')
		planningSet = set()
		for Bus in planningBuses:
			planningSet.add(Bus.strip())

		#print planningSet
		threeToThreeSubFound = 0
		for tf in Comed3WinderPlanningDict.keys():
			currentSet = Comed3WinderPlanningDict[tf]
			if currentSet == planningSet:
				#print CAPEPart + '->' + tf
				threeToThreeSubFound = 1
				break

		if threeToThreeSubFound == 0: # see if its a midpoint case
			MidPtFound = 0
			for Midpt in MidPtTMap.keys():
				currentMidPtSet =  MidPtTMap[Midpt]
				if currentMidPtSet == planningSet:
					print CAPEPart + '->' + MidPtIDMap[Midpt]
					MidPtFound = 1
					break
		#if MidPtFound == 0 and threeToThreeSubFound == 0:
		#	print line














"""
# get the set of planning midpoint buses imported into the merged raw file
with open(newMidPointList,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		words = line.split(',')
		Bus = words[0].strip()
		MidpointSet.add(Bus)

# using the tf data function, create a tmap for these midpoints
for Midpoint in list(MidpointSet):
	tfN = planningTFDataDict[Midpoint].toBus
	MidPtTMap[Midpoint] = set(tfN)












# Now use the MidPtTMap to figure out which cases in genAndMidpoint3wMaps.txt involve midpoint sets and which ones are just 3 winder subs
# Then do the subs

with open(oldGenAndMidPtSubFile,'r') as f:
	filecontent = f.read()
	oldSubFileLines = filecontent.split('\n')	

"""

