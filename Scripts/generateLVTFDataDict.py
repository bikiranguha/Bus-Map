"""
Generate a dict which will contain tf data for Comed LV buses in the planning file
"""


planningRaw = 'hls18v1dyn_1219.raw'
listMultTFfile = 'listMultTFfileCAPE.txt'

ComedLVBusSet = set() # all LV buses in comed
LVTFDataDict = {} # key: Bus1, Bus2, cktID (without apostrophy), value: tf data




# get the relevant comed bus sets
with open(planningRaw, 'r') as f:
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

	if Bus1 in ComedLVBusSet or Bus2 in ComedLVBusSet:
		if status == '1':
			key = Bus1 + ',' + Bus2 + ',' + cktID 
			
			tfDataList = []
			tfDataList.append(line)
			for j in range(3):
				i +=1
				line = fileLines[i]
				tfDataList.append(line)
			LVTFDataDict[key] = tfDataList

			i+=1
		else:
			i+=4

	else:
		i+=4
