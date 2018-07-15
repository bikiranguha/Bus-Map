#old_input = 'CAPEToCAPEMappingInput.txt'
new_input = 'CAPEToCAPEMappingInput.txt'
tmap_file = 'tmap_Raw0706.raw'
RawFile = 'new_Raw0706_TapDone.raw' # the raw file output by TapLogChange
angleChangeFile = 'logAngleChange.txt'
NewRawFile = 'new_Raw0706_CCMapsApplied.raw'


tMapDict = {}
tMapDictReverse = {}
VoltageDict = {}
AngleChangeDict = {}
newRawLines = []
from getBusDataFn import getBusData
CAPEBusDataDict = getBusData(RawFile)


def reconstructLine2(words):
	currentLine = ''
	for word in words:
		currentLine += word
		currentLine += ','
	return currentLine[:-1]

# Read the angle change values and generate a dict
with open(angleChangeFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'Bus' in line:
			continue

		if line == '':
			continue

		words = line.split('->')
		Bus = words[0].strip()
		Angle = float(words[1].strip()) 

		if Angle == 0.0: # Add to dictionary only if there is a phase shift
			#print Bus
			continue	
		#if Bus in changeNameDictNewToOld.keys():
		#	Bus = changeNameDictNewToOld[Bus]
		AngleChangeDict[Bus] = Angle

# get the tMap Info
with open(tmap_file,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line =='':
			continue
		tfInfo = line[:25].strip()
		MidPoint = line[26:].strip()
		#print tfInfo
		#print MidPoint
		tMapDict[MidPoint] = tfInfo
		tMapDictReverse[tfInfo] = MidPoint

"""
# uncomment if need to properly format the input file so that tf midpoints are replace by their original
# 3 winder id
with open(old_input,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line =='':
			continue
		words = line.split('->')
		RHS = words[0].strip()
		LHS = words[1].strip()
		if RHS in tMapDict.keys():
			tfInfo = tMapDict[RHS]
			print tfInfo + '->' + LHS
		else:
			print line
"""


# get the new voltages and angles of the buses to be mapped
with open(new_input,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line =='':
			continue
		words = line.split('->')
		LHS = words[0].strip()
		RHS = words[1].strip()


		if ',' in LHS: # midpoint mapping
			MapBus = tMapDictReverse[LHS]
		else: # normal CAPE to CAPE mapping
			MapBus = LHS

		# get voltage and angle info, including any phase shifts
		toMapBus = RHS
		Vmag = CAPEBusDataDict[MapBus].voltpu
		Ang = float(CAPEBusDataDict[MapBus].angle)
		PhaseShift = 0.0
		if toMapBus in AngleChangeDict.keys():
			#print toMapBus
			PhaseShift = AngleChangeDict[toMapBus]
		Ang += PhaseShift
		AngStr = '%.4f' %Ang
		AngStr = AngStr.rjust(9)
		
		VoltageDict[toMapBus] = [Vmag,AngStr]

# do the mapping and generate the new raw file
with open(RawFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	# reconstruct bus status
	for line in fileLines:
		if ('PSS' in line) or ('COMED' in line) or ('DYNAMICS' in line):
			continue
		if 'END OF BUS DATA' in line:
			break
		words = line.split(',')
		if len(words) <2:
			continue
		Bus = words[0].strip()
		if Bus in VoltageDict:
			VmagStr = VoltageDict[Bus][0]
			AngStr = VoltageDict[Bus][1]
			words[7] = VmagStr
			words[8] = AngStr
		currentLine = reconstructLine2(words)
		newRawLines.append(currentLine)

# add these two bus lines, for some reason they were missing
newRawLines.append("243083,'05CAMPSS    ', 138.0000,1, 205,1251,   1,1.01145, -55.0773")
newRawLines.append("658082,'MPSSE  7    ', 115.0000,1, 652,1624, 658,1.02055, -45.2697")

# append everything else
busEndIndex = fileLines.index('0 / END OF BUS DATA, BEGIN LOAD DATA')
for i in range(busEndIndex,len(fileLines)):
	line = fileLines[i]
	newRawLines.append(line)

# output the new raw data
with open(NewRawFile,'w') as f:
	f.write('0,   100.00, 33, 1, 1, 60.00     / PSS(R)E-33.3    TUE, DEC 13 2016  22:08')
	f.write('\n')
	f.write('COMED 2018,  HLS18V1, N18S OUTSIDE AND 18 INTCHNG')
	f.write('\n')
	f.write('DYNAMICS REVSION 01')
	f.write('\n')
	for line in newRawLines:
		f.write(line)
		f.write('\n')