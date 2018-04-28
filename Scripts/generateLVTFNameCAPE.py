"""
Generate a dict which will contain tf data and tf name and key data for Comed LV buses in the CAPE file
"""


CAPERaw = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/Island 34 system/' +  'Raw0414tmp.raw'


ComedLVBusSet = set() # all LV buses in comed
tfNameDictCAPE = {} # key: LV bus, values: [transformer name, tf key (bus1, bus2, ckt id)]



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
			#BusVoltDict[Bus] = BusVolt
			if BusVolt < 40.0:
				ComedLVBusSet.add(Bus)



tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')
i = tfStartIndex
# search tf data to populate LVTFDataDict
while i < tfEndIndex:
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	cktID = words[3].strip("'").strip()
	status = words[11].strip()
	tfname = words[10].strip("'").strip()

	if Bus1 in ComedLVBusSet or Bus2 in ComedLVBusSet:
		if status == '1':
			key = Bus1 + ',' + Bus2 + ',' + cktID

			# generate tfNameDictCAPE
			if Bus1 in ComedLVBusSet:
				keyBus = Bus1 # keyBus is the LV bus
			else:
				keyBus = Bus2


			if keyBus in tfNameDictCAPE.keys():
				tfNameDictCAPE[keyBus].append([tfname,key])

			else:
				tfNameDictCAPE[keyBus] = [[tfname,key]]

		i+=4
	else:
		i+=4

