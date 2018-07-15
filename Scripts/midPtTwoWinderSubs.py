# carries out the midpoint 2w->2w transformer substitutions specified in tf2tfmaps_2winder_cleaned.txt 

from tfMapFnv4 import doTFMaps
from getBusDataFn import getBusData
from generatePSDataFn import getPSData # get phase shift info for all tf from given raw file, needed by doTFMaps
planningRaw = 'hls18v1dyn_1219.raw'
CAPERaw = 'new_Raw0706_CCMapsApplied.raw' # output of CAPE to CAPE mapping script
newRawFile = 'new_Raw0706_midptTFDone.raw'
tmap_file = 'tmap_Raw0706.raw'
changeLog = 'changeBusNoLog.txt'
#oldTFData = 'TFSubManualDone.txt'
#newTFData = 'TFSubGenTFFixRemaining.txt'
#BusDataDicts are needed for nominal voltage info only
planningBusDataDict = getBusData(planningRaw)
CAPEBusDataDict = getBusData(CAPERaw)
tMapDict = {}
changeDict = {}
input_file = 'tf2tfmaps_2winder_cleaned.txt'
tfSubLines = []
oldTFLines = []

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
        changeDict[OldBus] = NewBus


# get the tMap Info
with open(tmap_file,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line =='':
			continue
		tfInfo = line[:25]
		MidPoint = line[26:].strip()
		#print tfInfo
		#print MidPoint
		#tMapDict[MidPoint] = tfInfo
		tMapDict[tfInfo] = MidPoint




with open(input_file,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

# get the relevant inputs
startIndex = fileLines.index("Format: Planning 2 winder->CAPE real bus-> tmap info (get the tmap info and ckt id and place them accordingly)") + 1
endIndex = fileLines.index('Normal two winder substitutions from mapping_confirmed_0606:')
for i in range(startIndex,endIndex):
	line = fileLines[i]
	words = line.split('->')
	planningTF = words[0].strip()
	CAPEBus1 = words[1].strip()
	if CAPEBus1 in changeDict:
		CAPEBus1 = changeDict[CAPEBus1]
	CAPEBus1 = CAPEBus1.rjust(6)

	midptTFKey = words[2].strip()
	midptTFWords = midptTFKey.split(',')
	MidBus1 = midptTFWords[0].strip()
	MidBus2 = midptTFWords[1].strip()
	MidBus3 = midptTFWords[2].strip()
	cktID = midptTFWords[3].strip()
	if MidBus1 in changeDict:
		MidBus1 = changeDict[MidBus1]

	if MidBus2 in changeDict:
		MidBus2 = changeDict[MidBus2]

	if MidBus3 in changeDict:
		MidBus3 = changeDict[MidBus3]

	midptTFKey = MidBus1.rjust(6) + ',' + MidBus2.rjust(6) + ',' + MidBus3.rjust(6) + ',' + cktID

	cktIDStripped = cktID.strip("'")
	#print cktIDStripped
	MidPoint = tMapDict[midptTFKey]
	newCAPETF = CAPEBus1 + ',' + MidPoint  + ',' + cktIDStripped
	subLine = planningTF + '->' +newCAPETF
	print subLine
	tfSubLines.append(subLine)


# get the current CAPE tf data, which will be the old tf data
with open(CAPERaw,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
	tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')

	for i in range(tfStartIndex,tfEndIndex):
		line = fileLines[i]
		oldTFLines.append(line)
TFPSDict = getPSData(CAPERaw)
# do the tf subs on the old tf data to get new tf data
newTFLines = doTFMaps(tfSubLines,oldTFLines,planningBusDataDict,CAPEBusDataDict,TFPSDict)


# now generate the new raw file, with tf data substituted
with open(newRawFile,'w') as f:
	for i in range(tfStartIndex):
		line = fileLines[i]
		f.write(line)
		f.write('\n')

	for line in newTFLines:
		f.write(line)
		f.write('\n')	
	
	for i in range(tfEndIndex,len(fileLines)):
		line = fileLines[i]
		f.write(line)
		f.write('\n')			
