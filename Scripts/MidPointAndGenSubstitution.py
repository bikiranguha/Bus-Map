from getTFDataFn import getTFData
from getBusDataFn import getBusData
planningRaw = 'hls18v1dyn_new.raw'
newMidPointList = 'MidPointBusesAdded.txt'
MidpointSet = set()
MidPtTMap = {}
oldGenAndMidPtSubFile = 'genAndMidpoint3wMaps.txt'
Comed3WinderPlanningDict = {}
planningBusDataDict = getBusData(planningRaw)
planningTFDataDict = getTFData(planningRaw)




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
    	planningPart = words[1].strip()
    	planningBuses = planningPart.split(',')
    	planningSet = set()
    	for Bus in planningBuses:
    		planningSet.add(Bus)

    	for tf in Comed3WinderPlanningDict.keys():
    		currentSet = Comed3WinderPlanningDict[tf]
    		if currentSet == planningSet:
    			print CAPEPart + '->' + tf
    			break



		"""
		if key in ImpPlanningTFSet:
			CZ = words[5]
			i+=1
			line = fileLines[i]
			words = line.split(',')
			R12 = words[0]
			X12 = words[1]
			SBASE12 = words[2]
			R23 = words[3]
			X23 = words[4]
			SBASE23 = words[5]
			R31 = words[6]
			X31 = words[7]
			SBASE31 = words[8]
			if key not in planningTFDict.keys():
				planningTFDict[key] = [CZ,R12,X12,SBASE12,R23,X23,SBASE23,R31,X31,SBASE31]
			else:
				print 'Multiple CAPE 3 winder mapped to single PSSE 3 winder: ', key
				sameBusMultiTFset.add(key)
			i+=4 # continue to next TF
		else: # 3 winder of no interest
			i+=5
		"""









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

