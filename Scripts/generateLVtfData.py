"""
Generate NumLVTFDictCAPE, TFPSDict
NumLVTFDictCAPE: key: LV bus, value: number of step up tf connected to it
TFPSDict key: TF Bus1, Bus2, cktID, value: float containing phase shift info
"""

CAPERaw = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/Island 34 system/' +  'Raw0414tmp.raw'
listMultTFfile = 'listMultTFfileCAPE.txt'

ComedBusSet = set() # all comed buses in the planning case
ComedLVBusSet = set() # all LV buses in comed
BusVoltDict = {} 
NumLVTFDictCAPE = {} # key: LV bus, value: number of step up tf connected to it
TFPSDict = {} # key: TF Bus1, Bus2, cktID, value: float containing phase shift info



def getImpTFData(Bus1, Bus2, cktID, i, fileLines):
	# get phase shift info for step up tf
	key = Bus1 + ',' + Bus2 + ',' + cktID 

	i+=2 #skip this line and the next line
	line = fileLines[i]
	words = line.split(',')
	PS = float(words[2].strip())
	TFPSDict[key] = PS

########

# get the relevant comed bus sets
with open(CAPERaw, 'r') as f:
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
		BusVolt = float(words[2].strip())
		#angle = float(words[8].strip())
		area = words[4].strip()
		#AreaDict[Bus] = area

		if area == '222':
			#BusAngleDict[Bus] = angle
			BusVoltDict[Bus] = BusVolt
			ComedBusSet.add(Bus)
			if BusVolt < 40.0:
				ComedLVBusSet.add(Bus)



for bus in list(ComedLVBusSet):
	NumLVTFDictCAPE[bus] = 0


tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')
i = tfStartIndex
# search tf data to see which LV load buses have multiple step up tf connected to them
while i < tfEndIndex:
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	cktID = words[3].strip("'").strip()
	status = words[11].strip()

	if Bus1 in ComedLVBusSet or Bus2 in ComedLVBusSet:
		getImpTFData(Bus1, Bus2, cktID, i, fileLines)

	if Bus1 in ComedLVBusSet:
		if BusVoltDict[Bus2] >40.0:
			if status == '1':
				NumLVTFDictCAPE[Bus1] += 1
				

	elif Bus2 in ComedLVBusSet:
		if BusVoltDict[Bus1] >40.0:
			if status == '1':
				NumLVTFDictCAPE[Bus2] += 1


	i+=4









