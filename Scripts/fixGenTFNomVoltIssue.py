"""
Manually change the tf WINDV and NOMV values for all the gen buses
"""


verifiedMapFile = 'PSSEGenMapVerified.txt' # verified mapping of the gen data'
NeedToFixVoltSet = set() # set of planning gen buses which need to have the nominal voltage changed in the tf data
NeedToFixVoltSSetPart2 = set()
latestTFFIle =  'TFTwoWinderSubDone.txt'
newTFFile = 'TFSubComplete.txt' 
TFFixFile = 'fixedGenTFNominalVoltData.txt' # all the relevant tf volt (WIND and NOM) info manually fixed
TFFixFileP2 = 'fixedOtherTFNominalVoltDataPart2.txt' # other tf nominal volt fixes
newTFLines = [] # list of all tf data where the nom volt and wind volt may need to be changed
# open up the verified gen map file and extract the info into a set and a dictionary
with open(verifiedMapFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'Manual' in line:
			continue
		words = line.split(',')
		if len(words) < 2:
			continue
		PSSEBus = words[0].strip()
		CAPEBus = words[5].strip()
		PSSENomVolt = words[3].strip()
		CAPENomVolt = words[7].strip()

		if PSSENomVolt != CAPENomVolt and PSSEBus != '274848': # This particular bus has no tf in CAPE
			#print line
			NeedToFixVoltSet.add(PSSEBus)


# open fix part 2, get the relevant gen ids
with open(TFFixFileP2,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	FixPart2Data = filecontent
# generate new tf lines 
i = 0
while i < len(fileLines):
	line = fileLines[i]
	if line == '':
		i+=1
		continue
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	Bus3 = words[2].strip()
	cktID = words[3].strip()
	key = Bus1.rjust(6) + ',' + Bus2.rjust(6) + ',' + Bus3.rjust(6) + ',' + cktID
	NeedToFixVoltSSetPart2.add(key)
	#print key
	if Bus3 == '0':
		i+=4
	else:
		i+=5


# open latest tf data and get relevant tf info
#print 'Relevant tf data:\n\n'
with open(latestTFFIle,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

# generate new tf lines 
i = 0
while i < len(fileLines):
	line = fileLines[i]
	if line == '':
		i+=1
		continue
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	Bus3 = words[2].strip()
	cktID = words[3].strip()
	key = Bus1.rjust(6) + ',' + Bus2.rjust(6) + ',' + Bus3.rjust(6) + ',' + cktID
	if key in NeedToFixVoltSSetPart2 or Bus1 in NeedToFixVoltSet or Bus2 in NeedToFixVoltSet or Bus3 in NeedToFixVoltSet : # skip data
		if Bus3 == '0':
			i+=4

		else:
			i+=5
	else: # add data
		if Bus3 == '0':
			newTFLines.append(line)
			for j in range(3):
				i+=1
				line = fileLines[i]
				newTFLines.append(line)
			i+=1
		else:
			newTFLines.append(line)
			for j in range(4):
				i+=1
				line = fileLines[i]
				newTFLines.append(line)
			i+=1

# get the fixed tf data for the relevant gen
with open(TFFixFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		newTFLines.append(line)


# generate the sub complete tf data
with open(newTFFile,'w') as f:
	for line in newTFLines:
		f.write(line)
		f.write('\n')
	f.write(FixPart2Data)
	f.write('\n')
