# Look at AllToBeMappedFile, ArtificialLoadMapping File (and manual), and Artificial Load bus file and update all the midpoint info 

from getBusDataFn import getBusData # create a dictionary which organizes all bus data

AllToBeMappedFile = 'AllToBeMappedFileFromHemanth.txt' # input file to AllToBeMappedSet
AllToBeMappedFileNew = 'AllToBeMappedFileUpDated.txt' # input file to AllToBeMappedSet
ArtificialLoadMappingFiles = ['ArtificialLoadMapping.txt', 'ArtificialLoadMapping_Manual.txt'] # input mapping file for artificial loads
ArtificialLoadMapFileNew = 'ArtificialLoadMapFileNew.txt'
#ArtificialLoadBusFile = 'ArtificialLoadBusFile.txt' # input file to ArtificialLoadBusSet
ArtificialLoadBusFile = 'ArtificialLoadBusFileFromHemanth.txt'
ArtificialLoadBusFileNew = 'ArtificialLoadBusFileUpdated.txt' # input file to ArtificialLoadBusSet
tmap_file_new = 'tmap_Raw0706.raw'
tmap_file_old = 'tmap_RAW03222018.raw'
#CAPERaw = 'new_Raw0706_midptTFDone.raw'
CAPERaw = 'new_Raw0706_CCMapsApplied.raw'
updatedToBeMappedLines = []
updatedALMLines = [] # updated lines for artificial load maps
updatedLoadBusLines = [] # self explanatory
tMapDictNew = {} # key: original 3 winder, value: Midpoint
tMapDictOld = {} # key: Midpoint, value: original 3 winder
CAPEBusDataDict = getBusData(CAPERaw)
# get the tMap Info
with open(tmap_file_old,'r') as f:
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
		tMapDictOld[MidPoint] = tfInfo


# get the tMap Info
with open(tmap_file_new,'r') as f:
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
		tMapDictNew[tfInfo] = MidPoint

# generate new lines for all to be mapped file
with open(AllToBeMappedFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if ',' not in line:
			continue
		words = line.split(',')
		Bus = words[0].strip()
		if Bus in tMapDictOld:
			tfKey = tMapDictOld[Bus]
			NewMidpt = tMapDictNew[tfKey]
			Name = CAPEBusDataDict[NewMidpt].name
			Volt = CAPEBusDataDict[NewMidpt].NominalVolt
			nLine = NewMidpt + ',' + Name + ',' + Volt
			#print nLine
			updatedToBeMappedLines.append(nLine)
		else:
			updatedToBeMappedLines.append(line)

# generate new lines for artificial load maps 
for file in ArtificialLoadMappingFiles:
	with open(file,'r') as f:
		filecontent = f.read()
		fileLines = filecontent.split('\n')
		for line in fileLines:
			if 'CAPE' in line or line == '':
				continue
			words = line.split('=')
			CAPESide = words[0].strip()
			planningSide = words[1]
			Bus1 = CAPESide.split(',')[0].strip()
			Bus2 = CAPESide.split(',')[1].strip()
			#cktID = CAPESide.split(',')[2].strip()
			if Bus1 in tMapDictOld:
				tfKey = tMapDictOld[Bus1]
				Bus1 = tMapDictNew[tfKey]				

			if Bus2 in tMapDictOld:
				tfKey = tMapDictOld[Bus2]
				Bus2 = tMapDictNew[tfKey]	

			nLine = Bus1.rjust(6) + ',' +  Bus2.rjust(6)  +   ' = ' + planningSide
			#print nLine
			updatedALMLines.append(nLine)


# generate new lines for artificial load bus file
with open(ArtificialLoadBusFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'List' in line or line == '':
			continue
		words = line.split(',')
		Bus = words[0].strip()
		if Bus in tMapDictOld:
			tfKey = tMapDictOld[Bus]
			Bus = tMapDictNew[tfKey]
		Name = CAPEBusDataDict[Bus].name
		Volt = CAPEBusDataDict[Bus].NominalVolt
		nLine = Bus + ',' + Name + ',' + Volt

		updatedLoadBusLines.append(nLine)

# outputs

# new output file for Artificial Load maps

with open(ArtificialLoadMapFileNew,'w') as f:
	f.write('CAPE From, CAPE To = Planning From, Planning To')
	f.write('\n')
	for line in updatedALMLines:
		f.write(line)
		f.write('\n')

with open(AllToBeMappedFileNew,'w') as f:
	f.write('List of buses which need to be mapped:')
	f.write('\n')
	for line in updatedToBeMappedLines:
		f.write(line)
		f.write('\n')


with open(ArtificialLoadBusFileNew,'w') as f:
	f.write('List of buses whose flows will be converted to loads:')
	f.write('\n')
	for line in updatedLoadBusLines:
		f.write(line)
		f.write('\n')