"""
Find errors in the Manual Map by the CS guys
"""


ManualMapCS = 'Manual_Mapping0501.txt'
CAPERaw = 'RAW0501.raw'
mappedCAPETFSet = set()
ComedLVTFSet = set()
ComedLVBusSet = set()
issueMappingTFSet = set()
# look at the manual maps done by the CS guys, and modified by me
with open(ManualMapCS,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:		
		if 'Format:' in line:
			continue
		if line == '':
			continue

		words = line.split('->')
		planningSide = words[0].strip()
		CAPESide = words[1].strip()
		if CAPESide == '': # mapping not provided
			continue

		CAPESideWords = CAPESide.split(',')
		CAPESideShort = ''
		# eliminate any comments
		for i in range(3):
			CAPESideShort += CAPESideWords[i].strip()
			CAPESideShort += ','
		CAPESideShort = CAPESideShort[:-1]

		if CAPESideShort not in mappedCAPETFSet:
			mappedCAPETFSet.add(CAPESideShort)
		else:
			issueMappingTFSet.add(CAPESideShort)


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
			ComedLVTFSet.add(key)

	i+=4 # continue to next tf


for tf in list(mappedCAPETFSet):
	if tf not in ComedLVTFSet:
		issueMappingTFSet.add(tf)