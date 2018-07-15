# write a function which will match up all the non-midpoint bus data in Raw_cropped and output before 3w -> 2w conversion
# this function should be called after tap splits
# also write a function which compares tf data

from getBusDataFn import getBusData
scriptOutputRaw = 'Raw0706.raw'
croppedRaw = 'RAWCropped_latest.raw'
AllToBeMappedFile = 'AllToBeMappedFile.txt'
AllToBeMappedSet = set()
scriptOutputBusDataDict = getBusData(scriptOutputRaw)
croppedRawBusDataDict = getBusData(croppedRaw)
#scriptOutputBusDataDict = {}
#croppedRawBusDict = {}

# get the necessary comed buses whose voltage value is less than 345 kV
with open(AllToBeMappedFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

	# grab bus data
	for line in fileLines:
		if line == '':
			continue
		if 'List of buses' in line: # skip the header file
			continue
		words = line.split(',')
		Bus = words[0].strip()
		AllToBeMappedSet.add(Bus)

for Bus in croppedRawBusDataDict:
	if Bus in AllToBeMappedSet:
		BusName = croppedRawBusDataDict[Bus].name
		if 'T3W' not in BusName:
			V1 = float(croppedRawBusDataDict[Bus].voltpu)
			A1 = float(croppedRawBusDataDict[Bus].angle)
			N1 = float(croppedRawBusDataDict[Bus].NominalVolt)

			V2 = float(scriptOutputBusDataDict[Bus].voltpu)
			A2 = float(scriptOutputBusDataDict[Bus].angle)
			N2 = float(scriptOutputBusDataDict[Bus].NominalVolt)

			errorV = abs(V1-V2)/V1*100
			errorA = abs(A1-A2)/A1*100

			if errorV > 0.1 or errorA > 0.1 or N1 != N2:
				print 'Cropped: ' + Bus + ',' + str(N1) + ',' + str(V1) + ',' + str(A1)
				print 'Script: ' + Bus + ',' +  str(N2) + ',' + str(V2) + ',' + str(A2)

"""
# get bus lines from script output raw
with open(scriptOutputRaw,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

	# grab bus data
	for line in fileLines:
		if ('PSS' in line) or ('COMED' in line) or ('DYNAMICS' in line):
			continue
		if 'END OF BUS DATA' in line:
			break
		words = line.split(',')
		if len(words) <2:
			continue
		
		Bus = words[0].strip()
		
		if Bus in AllToBeMappedSet :
			scriptOutputBusDataDict[Bus] = line
# get bus lines from cropped raw
with open(croppedRaw,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

	# grab bus data
	for line in fileLines:
		if ('PSS' in line) or ('COMED' in line) or ('DYNAMICS' in line):
			continue
		if 'END OF BUS DATA' in line:
			break
		words = line.split(',')
		if len(words) <2:
			continue
		
		Bus = words[0].strip()
		name = words[1].strip()
		if Bus in AllToBeMappedSet:
			if 'T3W' not in name:
				#print name
				croppedRawBusDict[Bus] = line


for Bus in croppedRawBusDict:
	croppedLine = croppedRawBusDict[Bus]
	scriptLine = scriptOutputBusDataDict[Bus]

	if croppedLine != scriptLine:
		print 'Cropped line: ' + croppedLine
		print 'Script Line: ' + scriptLine
"""




