"""
Script to do the substitution of CAPE 3 winders to planning 2 winders
Done after all the 3 winders are converted to 2 winders
Update: Import the off nominal tap ratio from planning as well
"""
from getBusDataFn import getBusData
from getTFDataFnv2 import getTFData
import math
input_file = 'Winder3To2SubInputs.txt'
CAPERaw = 'new_Raw0706.raw'
planningRaw = 'hls18v1dyn_1219.raw'
changeLog = 'changeBusNoLog.txt'
tMapFile = 'tmap_Raw0706.raw'
newRawFile = 'new_Raw0706_3wconv.raw' # output file where all the 3w->2w subs are done
TapInput = 'tap_split_changes.txt' # original file containing tap split info
TapInput_new = 'tap_split_changes_new.txt' # updated with all the new midpoint tap split info
CAPEBusDataDict = getBusData(CAPERaw)
planningBusDataDict = getBusData(planningRaw)
changeDict = {} # old to new dict
tMapDict = {} # key: original 3 winder, value: new 2 winders, without the tertiary
planningTFDataDict =getTFData(planningRaw)
CAPETFDataDict =  getTFData(CAPERaw)
NewTFImpedanceData = {} # key: all tf whose impedances are being subbed, values: new impedance and sbase data
newRawLines = []
MidptDict = {} # key: 3 winder, value: corresponding tf
originaltapSplitLines = []
midptTapSplitLines = [] # list of new tap split lines

def reconstructLine2(words):
	currentLine = ''
	for word in words:
		currentLine += word
		currentLine += ','
	return currentLine[:-1]


# get old to new bus number conversions
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
		changeDict[OldBus] = NewBus


# get the tmaps
with open(tMapFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		words = line.split(',')
		#tfKeyWords = tfKey.split(',')
		Bus1 = words[0].strip()
		Bus2 = words[1].strip()
		Bus3 = words[2].strip()
		cktID = words[3].strip()
		tfKey = line[:25]
		#print tfKey
		MidPtBus = words[4].strip()
		NewTF1 = Bus1.rjust(6) + ',' + MidPtBus + ',' + '     0' + ',' + cktID
		NewTF2 = Bus2.rjust(6) + ',' + MidPtBus + ',' + '     0' + ',' + cktID
		#NewTF3 = Bus3.rjust(6) + ',' + MidPtBus + ',' + '     0' + ',' + cktID
		tMapDict[tfKey] = [NewTF1,NewTF2]
		MidptDict[tfKey] = MidPtBus


print 'Verified that all the primary and secondary voltage pairs match between planning and CAPE'
with open(input_file,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if '->' not in line:
			continue
		words = line.split('->')
		CAPEWords = words[0].split(',')
		planningTFKey = words[1].strip()
		planningWords = words[1].split(',')
		CAPEBus1 = CAPEWords[0].strip()
		CAPEBus2 = CAPEWords[1].strip()
		CAPEBus3 = CAPEWords[2].strip()
		planningBus1 = planningWords[0].strip()
		planningBus2 = planningWords[1].strip()
		planningBus3 = planningWords[2].strip()		
		cktID = CAPEWords[3].strip()

		# renumber, if necessary
		if CAPEBus1 in changeDict:
			CAPEBus1 = changeDict[CAPEBus1]

		if CAPEBus2 in changeDict:
			CAPEBus2 = changeDict[CAPEBus2]

		if CAPEBus3 in changeDict:
			CAPEBus3 = changeDict[CAPEBus3]

		# get the new 2 winders
		CAPETFKey = CAPEBus1.rjust(6) + ',' + CAPEBus2.rjust(6) + ',' + CAPEBus3.rjust(6) + ',' + cktID
		NewTF1 = tMapDict[CAPETFKey][0]
		NewTF2 = tMapDict[CAPETFKey][1]

		# get the tap split lines
		MidPtBus = MidptDict[CAPETFKey]
		tapLine = CAPEBus1.rjust(6) + ',' + CAPEBus2.rjust(6) + ',' + MidPtBus.rjust(6)
		#print tapLine
		midptTapSplitLines.append(tapLine)

		# get the primary impedance and the MVA base
		CZ1 = CAPETFDataDict[NewTF1].CZ
		R1 = float(CAPETFDataDict[NewTF1].R)
		X1 = float(CAPETFDataDict[NewTF1].X)
		SBase1 = CAPETFDataDict[NewTF1].SBase	
		# Verified that all the CZ == 1
		#if CZ1 == '1':
		#	print NewTF1	

		# get the secondary impedance and the MVA base
		CZ2 = CAPETFDataDict[NewTF2].CZ
		R2 = float(CAPETFDataDict[NewTF2].R)
		X2 = float(CAPETFDataDict[NewTF2].X)
		SBase2 = CAPETFDataDict[NewTF2].SBase
		#if CZ2 == '3':
		#	print NewTF1

		# get ratios and total Impedance
		Rtot = R1 + R2
		Xtot = X1 + X2
		if Rtot != 0.0:
			R1Ratio = R1/Rtot
			R2Ratio = R2/Rtot
		else:
			R1Ratio = 0.5
			R2Ratio = 0.5

		X1Ratio = X1/Xtot
		X2Ratio = X2/Xtot


		# get the planning tf values
		CWPlanning = planningTFDataDict[planningTFKey].CW
		CZPlanning = planningTFDataDict[planningTFKey].CZ
		RPlanning = float(planningTFDataDict[planningTFKey].R)
		XPlanning = float(planningTFDataDict[planningTFKey].X)
		SBasePlanning = float(planningTFDataDict[planningTFKey].SBase)
		# get the WINDV1,2 and NOMV1,2
		WINDV1 = planningTFDataDict[planningTFKey].WINDV1
		WINDV2 = planningTFDataDict[planningTFKey].WINDV2

		NOMV1 = planningTFDataDict[planningTFKey].NOMV1
		NOMV2 = planningTFDataDict[planningTFKey].NOMV2

		planningBus1V = float(planningBusDataDict[planningBus1].NominalVolt)
		planningBus2V = float(planningBusDataDict[planningBus2].NominalVolt)

		# format WINDV1 and WINDV2 accordingly
		if CWPlanning == '1':
			# convert to str
			WINDV1 = '%.5f' %WINDV1
			WINDV2 = '%.5f' %WINDV2			
		elif CWPlanning == '2':
			# winding voltage in kV, need to convert to pu in terms of planning bus nom volt
			WINDV1 = WINDV1/planningBus1V
			WINDV2 = WINDV2/planningBus2V
			# convert to string
			WINDV1 = '%.5f' %WINDV1
			WINDV2 = '%.5f' %WINDV2

		elif CWPlanning == '3':
			# winding voltage in pu of NOMV, need to convert to bus nom volt
			if NOMV1 == 0.0:
				TempNOMV1 = planningBus1V
			else:
				TempNOMV1 = NOMV1

			if NOMV2 == 0.0:
				TempNOMV2 = planningBus2V
			else:
				TempNOMV2 = NOMV2

			WINDV1 = WINDV1*TempNOMV1/planningBus1V
			WINDV2 = WINDV2*TempNOMV2/planningBus2V

			# convert to string
			WINDV1 = '%.5f' %WINDV1
			WINDV2 = '%.5f' %WINDV2


		# get the impedances
		if CZPlanning == '2': # convert to CZ = 1
			#print planningTFKey
			RPlanning = RPlanning/SBasePlanning*100.0
			XPlanning = XPlanning/SBasePlanning*100.0
		elif CZPlanning == '3': # convert to CZ = 2
			PLoss = float(RPlanning)
			Z = float(XPlanning)
			RPlanning = ((PLoss/10**6)*100/SBasePlanning**2)
			ZPlanning = Z*100.0/SBasePlanning
			XPlanning = math.sqrt(ZPlanning**2 - RPlanning**2)	
			#print RPlanning, XPlanning		


		# generate new Z1 and Z2 values
		NewR1 = R1Ratio*RPlanning
		NewR2 = R2Ratio*RPlanning

		NewX1 = X1Ratio*XPlanning
		NewX2 = X2Ratio*XPlanning

		NewTFImpedanceData[NewTF1] = [NewR1,NewX1,planningTFDataDict[planningTFKey].SBase,WINDV1,NOMV1]
		NewTFImpedanceData[NewTF2] = [NewR2,NewX2,planningTFDataDict[planningTFKey].SBase,WINDV2,NOMV2]
		#planningBus1 = planningWords[0].strip()
		#planningBus2 = planningWords[1].strip()

		"""
		V1CAPE = float(CAPEBusDataDict[CAPEBus1].NominalVolt)
		V2CAPE = float(CAPEBusDataDict[CAPEBus2].NominalVolt)

		V1planning = float(planningBusDataDict[planningBus1].NominalVolt)
		V2planning = float(planningBusDataDict[planningBus2].NominalVolt)
		if V1planning == V1CAPE and V2planning == V2CAPE:
			continue
		elif V1planning == V2CAPE and V2planning == V1CAPE:
			continue
		else:
			#print line + ' V1CAPE: ' + str(V1CAPE) + ' V1planning: ' + str(V1planning) + ' V2CAPE: ' + str(V2CAPE) + ' V2planning: ' + str(V2planning)
		"""


# extract the tf data from the raw file and then sub the impedance wherever necessary
with open(CAPERaw,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')


tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')

for i in range(tfStartIndex):
	line = fileLines[i]
	newRawLines.append(line)

i = tfStartIndex
while i < tfEndIndex:
	line = fileLines[i]
	words = line.split(',')
	tfKey = line[:25]
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	Bus3 = words[2].strip()
	cktID = words[3].strip()
	status  = words[11].strip()

	if tfKey in NewTFImpedanceData:
		#print tfKey
		newRawLines.append(line)
		i+=1
		line = fileLines[i]
		words = line.split(',')
		NewR = '%.5E' %NewTFImpedanceData[tfKey][0]
		NewX = '%.5E' %NewTFImpedanceData[tfKey][1]
		SBase = NewTFImpedanceData[tfKey][2]
		WINDV = NewTFImpedanceData[tfKey][3]
		NOMV = NewTFImpedanceData[tfKey][4]
		NOMV = '%.3f' % NOMV
		words[0] = NewR.rjust(11)
		words[1] = NewX.rjust(11)
		words[2] = SBase
		line = reconstructLine2(words)
		newRawLines.append(line)

		# append next 2 lines
		i+=1
		line = fileLines[i]
		words = line.split(',')
		words[0] = WINDV
		words[1] = NOMV.rjust(8)
		line = reconstructLine2(words)
		newRawLines.append(line)

		# this is WINDV and NOMV of midpoint, no need to change
		i+=1
		line = fileLines[i]
		newRawLines.append(line)
		# continue to next tf
		i+=1

	else: # no need to change, just add
		newRawLines.append(line)
		for j in range(3):
			i+=1
			line = fileLines[i]
			newRawLines.append(line)	
		i+=1	



# append everything after the tf data
for i in range(tfEndIndex,len(fileLines)):
	line = fileLines[i]
	newRawLines.append(line)

# the output of this file
with open(newRawFile,'w') as f:
	for line in newRawLines:
		f.write(line)
		f.write('\n')

# update the tap split info
with open(TapInput,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line != '':
			originaltapSplitLines.append(line)

with open(TapInput_new,'w') as f:
	for line in originaltapSplitLines:
		f.write(line)
		f.write('\n')

	f.write('Tap splits involving midpoint:')
	f.write('\n')
	for line in midptTapSplitLines:
		f.write(line)
		f.write('\n')
