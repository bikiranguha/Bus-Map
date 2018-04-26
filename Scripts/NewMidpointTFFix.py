"""
Generates new 2 winder sets with midpoints from 3 winder data using the fixes provided in AdvancedMidpointCases.txt

"""
import shutil

from getMidpointDatav2 import ComedMidpointSet, MidpointNeighbour, MidpointDict, MidpointTFdata, ComedMidpointBusData

MidPointFixdata = 'AdvancedMidpointCases.txt'
TFFile  = 'TFIter1.txt'
NewTFFile  = 'TFIter2.txt'
AllMapFile = 'AllMappedBusDataIter1.txt'
AllMapFileNew = 'AllMappedBusDataIter2.txt'
tf3winderchangeLog = 'tf3winderchangeLog.txt'
newLog = 'tf3winderChangeLogIter2.txt'

AdvancedMidPtSubDict = {} # key: CAPE tf, value: [Midpoint, set of neighbour buses of the midpoint of the planning tf]
TempMapDict = {} # key: CAPE Buses in MidPointFixData, values: list of all mappings in the MidPointFixData file
tfLinesIter2 = []
newMidPointLines = [] # pretty self explanatory
newLogLines = [] # updated log lines



def reconstructLine2(words):
	currentLine = ''
	for word in words:
		currentLine += word
		currentLine += ','
	return currentLine[:-1]


def reconstructMidPointData2(CAPEBusList,PSList,Midpoint):
	# if CAPE tf can be mapped to a three winder set with midpoint in PSSE, do it here
	tfData = MidpointTFdata[Midpoint] # contains 3 lists, each lists has multiple lines consisting of tf data
	newtfData = [] # new tf list, to be returned

	for tf in tfData: # tf: list of tf data
		newtf = list(tf)
		BusLineWords = newtf[0].split(',') # get words for Bus Line
		Bus1 = BusLineWords[0].strip()
		Bus2 = BusLineWords[1].strip()


		# find the phase shift index (PSIndex) and the CAPE bus number (newBus)
		if Bus1 == Midpoint:
			for b in CAPEBusList:
				if Bus2 in TempMapDict[b]:
					bNew = b
					"""
					if b in newNoDict.keys():
						bNew = newNoDict[b] 
					"""
					BusLineWords[1] = ' '*(6-len(bNew)) +  bNew
					PSindex = CAPEBusList.index(b)
					MidPtPosition = 0 # if 0, then the PSValue is inverted (+ve-> -ve or -ve -> +ve)
					break
		elif Bus2 == Midpoint:
			for b in CAPEBusList:
				if Bus1 in TempMapDict[b]:
					bNew = b
					"""
					if b in newNoDict.keys():
						bNew = newNoDict[b]
					"""
					BusLineWords[0] = ' '*(6-len(bNew)) +  bNew
					PSindex = CAPEBusList.index(b)
					MidPtPosition = 1 # if 1, then PSValue remains unchanged
					break


		newBusLine = reconstructLine2(BusLineWords)
		newtf[0] = newBusLine

		# insert the PS value
		#print PSindex
		PSValue = PSList[PSindex]
		if MidPtPosition == 0: # Midpoint is Bus1, change PSValue sign
			PSValueFloat = float(PSValue)
			if PSValueFloat != 0.0: # if 0, no need to change sign
				PSValueFloat = -PSValueFloat
			PSValue = str(PSValueFloat)

		PSLineWords = newtf[2].split(',')
		PSLineWords[2] = PSValue
		# reconstruct PSLine
		newPSLine = reconstructLine2(PSLineWords)
		newtf[2] = newPSLine

		# populate new tf data
		newtfData.append(newtf)

	return newtfData


def getPhaseShifts(i, fileLines):
	#get original tf phase shifts, to be added in to new 2 winders
	PSList = [] # ordered as primary, secondary and tertiary
	
	i+=2 #skip this line and the next line

	line = fileLines[i]
	words = line.split(',')
	PS = words[2].strip()
	PSList.append(PS)

	i+=1
	line = fileLines[i]
	words = line.split(',')
	PS = words[2].strip()
	PSList.append(PS)

	i+=1
	line = fileLines[i]
	words = line.split(',')
	PS = words[2].strip()
	PSList.append(PS)

	return PSList


def generateTempMapDict(CAPEBus, planningList,  planningListIndex):
	# to help with populating TempMapDict
	if CAPEBus not in TempMapDict.keys(): # first encounter of CAPEBus
		TempMapDict[CAPEBus] = [planningList[planningListIndex].strip()]
	else: # not first encounter
		if TempMapDict[CAPEBus] == [planningList[planningListIndex].strip()]: # previous map same as this map
			pass
		else: # append
			TempMapDict[CAPEBus].append(planningList[planningListIndex].strip())	


def addMultLines(i,fileLines,newtfLines,numLines):
	# for adding transformer lines which do not change
	for j in range(numLines):
		i+=1
		line = fileLines[i]
		newtfLines.append(line)	
	return i



# get midpoint data from the file and re-organize it so that reconstructMidPointData2 fn can be used
with open(MidPointFixdata,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'cases' in line:
			continue
		if line == '':
			continue
		words = line.split('->')
		CAPEPart = words[0].strip()
		planningPart = words[1].strip()
		if '#' in planningPart: # leave out any comments
			tmp = planningPart.split('#')
			planningPart = tmp[0].strip()
		#print planningPart
		planningWords = planningPart.split(',')
		planningList = []

		for word in planningWords:
			if word.strip() in ComedMidpointSet:
				MidPt = word.strip()
				continue
			if word in ['     0', "'1 '"]:
				continue
			planningList.append(word)
		
		# all sets should have a len of 3, if not print the set
		if len(planningList) != 3:
			print planningList
		AdvancedMidPtSubDict[CAPEPart] = [MidPt,planningList]
		CAPEWords = CAPEPart.split(',')
		CAPEBus1 = CAPEWords[0].strip()
		CAPEBus2 = CAPEWords[1].strip()
		CAPEBus3 = CAPEWords[2].strip()
		generateTempMapDict(CAPEBus1,planningList,0)
		generateTempMapDict(CAPEBus2,planningList,1)
		generateTempMapDict(CAPEBus3,planningList,2)




# read old TFFile and reconstruct the 3 winders which can be mapped into 2 winder set using AdvancedMidpointCases.txt
with open(TFFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')


# generate new tf lines based on changed midpoint data
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
	if Bus3 == '0': # two winder, add lines and continue
		tfLinesIter2.append(line)
		i = addMultLines(i,fileLines,tfLinesIter2,3)
		i+=1
		continue

	else: # three winder
		key = Bus1+','+Bus2+','+Bus3+','+cktID
		if key in AdvancedMidPtSubDict.keys(): # transformer in AdvancedMidpointCases.txt
			#print key
			CAPEBusList = [Bus1,Bus2,Bus3]
			Midpoint = AdvancedMidPtSubDict[key][0]
			PSList = getPhaseShifts(i, fileLines) # get phase shifts from CAPE tf data
			newtfData = reconstructMidPointData2(CAPEBusList,PSList,Midpoint) # reconstruct tf
			#### Add new tf lines here (remember it is a nested list)
			for tf in newtfData:
				for line in tf:
					tfLinesIter2.append(line)

			# Add midpoint buses in bus data
			newMidPointLines.append(ComedMidpointBusData[Midpoint])
			i+=5 # next tf

		else: # no change needed in three winding tf
			tfLinesIter2.append(line)
			i = addMultLines(i,fileLines,tfLinesIter2,4)
			i+=1
			continue



# Outputs
with open(NewTFFile,'w') as f:
	for line in tfLinesIter2:
		f.write(line)
		f.write('\n')


with open(AllMapFile,'r') as f:
	oldBusData = f.read()

with open(AllMapFileNew,'w') as f:
	f.write(oldBusData)
	#f.write('\n')
	for line in newMidPointLines:
		f.write(line)
		f.write('\n')

# update log data with changes
with open(tf3winderchangeLog,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		words = line.split('->')
		CAPEPart = words[0].strip()
		if CAPEPart in AdvancedMidPtSubDict.keys():
			nLine = CAPEPart + '->' + str(AdvancedMidPtSubDict[CAPEPart][1])
			newLogLines.append(nLine)
		else:
			newLogLines.append(line)

with open(newLog,'w') as f:
	for line in newLogLines:
		f.write(line)
		f.write('\n')


# make a copy in Donut Hole v2
dest = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/AllMappedBusData.txt'
shutil.copyfile(AllMapFileNew,dest)


# this copy will be used in correctBusAngles.py to fix the phase angle shifts
dest = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/AllMappedBusDataIter2.txt'
shutil.copy(AllMapFileNew,dest)