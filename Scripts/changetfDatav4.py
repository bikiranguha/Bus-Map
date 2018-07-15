"""
	Changes the tf data by updating the bus numbers and also skipping any transformer data which includes buses outside of comed
	Also sets  winding voltage to nominal voltage if difference greater than 20%

Following changes should be implemented manually
Log of latest substitutions of 4 winders and other special cases:
We are trying to equate impedance data of CAPE and planning transformers
4 winders:
Case 984,1717,1718,4113:
   984,400116,     0,'1 ' + 100000,400116,     0,'1 '  = 272352,275152,     0,'1 '
100000,400239,     0,'1 ' + 1717,400239,     0,'1 ' =  275152,273089,     0,'1 '
100000,  1718,     0,'1 ' = 275152,273090,     0,'1 '
Case 989,1717,1718,7380:
   989,400117,     0,'1 ' + 100006,400117,     0,'1 ' =  272353,275153,     0,'1 '
100006,400242,     0,'1 ' +   1717,400242,     0,'1 ' = 275153,273089,     0,'1 '
100006,  1718,     0,'1 ' = 275153,273090,     0,'1 '
Case 993,1717,1718,4233:
   993,400118,     0,'2 ' + 100008,400118,     0,'2 ' = 272353,275159,     0,'1 '
100008,400243,     0,'2 '  +   1717,400243,     0,'2 ' = 275159,273089,     0,'1 '
100008,  1718,     0,'1 ' =  275159,273090,     0,'1 '
Case  1205,1213, 1221,1222:
  1205,400129,     0,'1 ' + 100002,400129,     0,'1 ' + 100002,400240,     0,'1 ' +   1213,400240,     0,'1 ' = 271310,272990,     0,'1 '
Case 1201,1209, 1220,1223:
  1201,400128,     0,'1 ' + 100004,400128,     0,'1 ' + 100004,400241,     0,'1 ' +   1209,400241,     0,'1 ' = 271311,272991,     0,'1 '

Other special cases detailed in Final_Sol_3w:
Case 750391,1727,2517,'1 ':
750391,400084,     0,'1 ' = 272432,275236,     0,'1 '
  1727,400084,     0,'1 ' = 273108,275236,     0,'1 '
Case 750392,1728,2518,'1 '
750392,400085,     0,'1 ' = 272433,275235,     0,'1 ' 
  1728,400085,     0,'1 ' = 273109,275235,     0,'1 '
Case 750156,750165,750166,'1 ':
750156,400031,     0,'1 ' = 270716,   338,     0,'86'
750165,400031,     0,'1 ' = 275650,   338,     0,'86'
750166,400031,     0,'1 ' = 275950,   338,     0,'86'
Case 750206[352]:
  3782,750206,     0,'1 ' = 274769,   374,     0,'1 '
  3783,750206,     0,'1 ' = 274769,   375,     0,'1 '
  3784,750206,     0,'1 ' = 274769,   376,     0,'1 '
  3785,750206,     0,'1 ' = 274769,   377,     0,'1 '

At the end of this script, implement all the 3 winder sub scripts
"""

#CAPERaw = 'CAPE_RAW1116v33.raw'
#newdir = 'Important data'
changeLog = 'changeBusNoLog.txt'
CAPERaw = 'MASTER_CAPE_Fixed.raw'


newtfData = 'newtfData.txt' # outputs the new tf data
outsideComedFile = 'outsideComedBusesv4.txt' # list of buses in CAPE case which are outside comed
isolatedCAPEBusList = 'isolatedCAPEBusList_All.txt' # list of buses which are isolated in cape
BusData = 'AllMappedBusData.txt'

OldBusSet = set() # old bus numbers
NewBusSet = set() # new bus numbers
#changeDict = {}
#GenDict = {}
changeDict = {} # map of old bus numbers to new bus numbers
noNeedtoMapSet = set() # set of buses which do not need to be mapped in CAPE
BusVoltageDict = {} # dictionary of bus voltages


def checkWindingVoltage(line,currentBusList,BusIndex):
	"""
	function to set proper winding voltage if it deviates
	by more than 20% of the nominal voltage
	"""

	words = line.split(',')
	WindVolt = words[0].strip()
	NomVolt = words[1].strip()
	Bus = currentBusList[BusIndex]
	if Bus in OldBusSet:
		Bus = changeDict[Bus]
	if float(NomVolt) == 0.0: 
		NomVolt = BusVoltageDict[Bus]
	percentDiff = abs(float(WindVolt) - float(NomVolt))/float(NomVolt)

	if percentDiff > 0.2: # if difference greater than 20%, set to nominal voltage
		words[0] = NomVolt
		currentLine = ''
		for word in words:
			currentLine +=word
			currentLine += ','
		tfLines.append(currentLine[:-1])
	else:
		tfLines.append(line)


def changeBus(Bus,words,changeDict):
	#print Bus
	newLine = ''
	newBus = changeDict[Bus]
	lennewBus = len(newBus)
	newBus = ' '*(6 - lennewBus) + newBus
	for word in words:
		if word.strip() == Bus:
			word = newBus
			newLine += word
			newLine += ','
		#elif word == words[-1]:
		#	newLine += word
		else:
			newLine += word
			newLine += ','
	#print newLine
	return newLine[:-1]


# gets the bus voltage info
with open(BusData,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		words = line.split(',')
		if len(words) <2:
			continue
		Bus = words[0].strip()
		Volt = words[2].strip()
		BusVoltageDict[Bus] = Volt



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
		OldBusSet.add(OldBus)
		NewBusSet.add(NewBus)
		changeDict[OldBus] = NewBus


# get a set of buses which dont need to be included in the branch data
with open(outsideComedFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'Manually' in line:
			continue
		if line.strip() != '':
			noNeedtoMapSet.add(line.strip())
			#CAPEMappedSet.add(line.strip())

# get the set of isolated buses and add them to no need to Map Set
with open(isolatedCAPEBusList,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'isolated' in line:
			continue
		noNeedtoMapSet.add(line.strip())	

tfLines = []
with open(CAPERaw, 'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
	tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')
	i = tfStartIndex
	while i < tfEndIndex:
		line = fileLines[i]
		words = line.split(',')
		Bus1 = words[0].strip()
		Bus2 = words[1].strip()
		Bus3 = words[2].strip()
		
		# currentBusList contains a list of all the buses in the transformer, 
		# needed for checkWindingVoltage()
		currentBusList = []
		for j in range(3):
			currentBusList.append(words[j].strip())

		if Bus3 == '0': # two winder
			if Bus1 in noNeedtoMapSet:
				i+=4
				continue
			elif Bus2 in noNeedtoMapSet:
				i+=4
				continue
				

			if Bus1 in OldBusSet:
				#print line
				line = changeBus(Bus1,words,changeDict)
				words = line.split(',')

			if Bus2 in OldBusSet:
				#print line
				line = changeBus(Bus2,words,changeDict)
				words = line.split(',')

			tfLines.append(line)
			# next line (just append)
			i+=1
			line = fileLines[i]
			tfLines.append(line)

			# next line (compare Bus1 winding and nominal voltage)
			i+=1
			line = fileLines[i]
			checkWindingVoltage(line,currentBusList,0)


			# next line (compare Bus2 winding and nominal voltage)
			i+=1
			line = fileLines[i]
			checkWindingVoltage(line, currentBusList, 1)


			i+=1 # go to next line



		else: # three winder
			if Bus1 in noNeedtoMapSet:
				i+=5
				continue
			elif Bus2 in noNeedtoMapSet:
				i+=5
				continue
			elif Bus3 in noNeedtoMapSet:
				i+=5
				continue

			if Bus1 in OldBusSet:
				#print line
				line = changeBus(Bus1,words,changeDict)
				words = line.split(',')

			if Bus2 in OldBusSet:
				#print line
				line = changeBus(Bus2,words,changeDict)
				words = line.split(',')

			if Bus3 in OldBusSet:
				#print line
				line = changeBus(Bus3,words,changeDict)
				words = line.split(',')

			tfLines.append(line)

			# next line (just append)
			i+=1
			line = fileLines[i]
			tfLines.append(line)

			# next line (compare Bus1 winding and nominal voltage)
			i+=1
			line = fileLines[i]
			checkWindingVoltage(line,currentBusList,0)


			# next line (compare Bus2 winding and nominal voltage)
			i+=1
			line = fileLines[i]
			checkWindingVoltage(line,currentBusList,1)

			# next line (compare Bus3 winding and nominal voltage)
			i+=1
			line = fileLines[i]
			checkWindingVoltage(line,currentBusList,2)


			i+=1



with open(newtfData, 'w') as f:
	for line in tfLines:
		f.write(line)
		f.write('\n')





# scripts to carry out tf substitutions
#import Winder3To3Substitution # carry out all the 3 winder to 3 winder subs in '3 winder substitution' folder and 'mapping_confirmed_0606'
import Winder3To3Substitutionv2 # carry out all the 3 winder to 3 winder subs in '3 winder substitution' folder and 'mapping_confirmed_0606', with NOMV1 and WINDV1 properly ordered
import NewMidPointSub # add all the planning tf midpoint sets added with the phase shifts included
import addManualTFData # add all the manual tf changes specified in manual_tf_data_new.txt
import twoWinderSubsv2 # carries out the normal 2w->2w transformer substitutions specified in tf2tfmaps_2winder_cleaned.txt 
import fixGenTFNomVoltIssue # fix gen tf WINDV and NOMV values