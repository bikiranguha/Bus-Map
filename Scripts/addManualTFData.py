TFData = 'TF3wTo3wSubv2WithMidPoints.txt'
TFDataNew = 'TFSubManualDone.txt'
manualChangeFile = 'manual_tf_data_new.txt'
doNotIncludeSet  = set()
toincludeTFLines = []
newManualTFLines = []


with open(manualChangeFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

doNotIncludeStart = fileLines.index('Do not include the following tf:') + 1
doNotIncludeEnd = fileLines.index('Add the following tf data (all the bus numbers are new bus numbers):')
addTFDataStart = fileLines.index('Add the following tf data (all the bus numbers are new bus numbers):') + 1

for i in range(doNotIncludeStart, doNotIncludeEnd):
	line = fileLines[i].strip()
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	Bus3 = words[2].strip()
	#doNotIncludeSet.add(line)
	doNotIncludeSet.add(Bus1)
	doNotIncludeSet.add(Bus2)

for i in range(addTFDataStart, len(fileLines)):
	line = fileLines[i]
	newManualTFLines.append(line)

i = addTFDataStart
while i < len(fileLines):
	# only works for 2 winder info
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	Bus3 = words[2].strip()
	cktID = words[3].strip()
	doNotIncludeSet.add(Bus1)
	doNotIncludeSet.add(Bus2)
	doNotIncludeSet.add(Bus3)
	#tfKey = line[:25]
	#doNotIncludeSet.add(tfKey)
	if Bus3 == '0':
		i+=4
	else:
		i+=5

# open old tf data and start substituting
with open(TFData,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

i=0
while i < len(fileLines):

	line = fileLines[i]
	#print line
	if line == '':
		i+=1
		continue
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	Bus3 = words[2].strip()
	cktID = words[3].strip()
	tfKey = line[:25]
	
	if  Bus3 == '0':
		if Bus1 in doNotIncludeSet and Bus2 in doNotIncludeSet: # two winder needs to be skipped
			#print tfKey
			i+=4
			continue
		else: # 2 winder needs to be same
			toincludeTFLines.append(line)
			for j in range(3):
				i+=1
				line = fileLines[i]
				toincludeTFLines.append(line)
			i+=1
	else: # three winder
		if Bus1 in doNotIncludeSet and Bus2 in doNotIncludeSet and Bus3 in doNotIncludeSet: # three winder needs to be skipped
			#print tfKey
			i+=5
			continue
		else: # needs to be same
			toincludeTFLines.append(line)
			for j in range(4):
				i+=1
				line = fileLines[i]
				toincludeTFLines.append(line)	
			i+=1	



with open(TFDataNew,'w') as f:
	for line in toincludeTFLines:
		f.write(line)
		f.write('\n')
	for line in newManualTFLines:
		f.write(line)
		f.write('\n')