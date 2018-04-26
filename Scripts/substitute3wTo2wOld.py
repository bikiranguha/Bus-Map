"""
 Script to substitute three winder -> two winder cases in FinalSolFile
"""

FinalSolFile = 'Final_sol_3w.txt' # TF substitutions which are special
PSSErawFile = 'hls18v1dyn_new.raw'
twoWinderCAPERawFile = '2wnd_RAW03222018.raw'
tmapFile = 'tmap_RAW03222018.raw'
newTFFIle = '2wnd_tf_iter2.txt'

ThreeToTwoSubDict = {}  # value: CAPE three winder id, values: ImpedanceInfo() class
planningSubSet = set() # list of planning tf whose impedance data is needed
planningTFDict = {} # key: important planning tf id, value: impedance value
findCAPEkeyPlanning = {} # used to help find CAPEKey in ThreeToTwoSubDict from planning tf id and FinalSolFile
CAPEImpBusSet = set() # Set of CAPE buses which matter in this case
newMidPtSet = set() # new MidPoints which need to be added to the Bus Data
tmapDict = {} # key: Midpoint bus, value: original CAPE three winder id
newImp2WinderLines = [] # list of all the lines in the tf file


class ImpedanceInfo(object):
	""" to organize all the needed tf data """
	def __init__(self):
		self.CAPEBus1 = ''
		self.CAPEBus2 = ''
		self.planningInfo = [] # impedance, SBASE and CZ values of equivalent planning 2 winder tf
		self.CAPEBus1Info = [] # impedance and SBASe values of Bus1 of relevant CAPE tf (transformer containing tertiary winding ignored). Since all CZ == 1, its ignored
		self.CAPEBus2Info = [] # impedance and SBASe values of Bus2 of relevant CAPE tf 
		#self.Midpoint = ''



def scaleImpedance(Z1,Z2,ZPlanning):
	# function to scale CAPE impedances to match planning impedances
	if (Z1+Z2) != 0.0:
		mismatchRatio = ZPlanning/(Z1+Z2)
		Z1new = Z1*mismatchRatio
		Z2new = Z2*mismatchRatio
	else:
		Z1new = ZPlanning/2
		Z2new = ZPlanning/2

	# convert to string with predefined precision
	Z1new = "%.5E" %Z1new 
	Z2new = "%.5E" %Z2new

	return Z1new,Z2new

def reconstructLine2(words):
	currentLine = ''
	for word in words:
		currentLine += word
		currentLine += ','
	return currentLine[:-1]

def addMultLines(i,fileLines,newtfLines,numLines):
	# for adding transformer lines which do not change
	for j in range(numLines):
		i+=1
		line = fileLines[i]
		newtfLines.append(line)	
	return i



# get relevant data (3w -> 2w) from this file
with open(FinalSolFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'txt' in line:
			continue
		if 'case' in line:
			continue
		words = line.split('->')
		CAPEPart = words[0].strip()
		planningPart = words[1].strip()
		planningWords = planningPart.split(',')
		if len(planningWords) > 3 and planningWords[2].strip() == '0':
			#if '#' in planningPart:
				#print line
			planningSubSet.add(planningPart)
			#ThreeToTwoSubDict[CAPEPart] = planningPart
			CAPEWords = CAPEPart.split(',')
			CAPEBus1 = CAPEWords[0].strip()
			CAPEBus2 = CAPEWords[1].strip()
			CAPEImpBusSet.add(CAPEBus1)
			CAPEImpBusSet.add(CAPEBus2)

			"""
			if CAPEBus1 in findCAPEkey.keys():
				findCAPEkey[CAPEBus1].append(CAPEPart)
			else:
				findCAPEkey[CAPEBus1] = [CAPEPart]

			if CAPEBus2 in findCAPEkey.keys():
				findCAPEkey[CAPEBus2].append(CAPEPart)
			else:
				findCAPEkey[CAPEBus2] = [CAPEPart]
			"""

			#ThreeToTwoSubDict[planningPart] = [CAPEBus1,CAPEBus2]
			ThreeToTwoSubDict[CAPEPart] = ImpedanceInfo()
			ThreeToTwoSubDict[CAPEPart].CAPEBus1 = CAPEBus1
			ThreeToTwoSubDict[CAPEPart].CAPEBus2 = CAPEBus2

			findCAPEkeyPlanning[planningPart] = CAPEPart


# tmap file info extraction
with open(tmapFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		words = line.split(',')
		Bus1 = words[0].strip()
		Bus2 = words[1].strip()
		Bus3 = words[2].strip()
		cktID = words[3].strip()
		MidPtBus = words[4].strip()
		key = Bus1+','+Bus2+','+Bus3+','+cktID

		if key in ThreeToTwoSubDict.keys():	
			#ThreeToTwoSubDict[key].Midpoint = MidPtBus
			newMidPtSet.add(MidPtBus)
			tmapDict[MidPtBus] = key
		




# get planning tf impedance data
with open(PSSErawFile,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split("\n")



tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')

# get tf data from PSSE raw file for relevant transformers
i = tfStartIndex
while i < tfEndIndex:
	line = fileLines[i]
	words = line.split(',')
	
	Bus1 = words[0]
	Bus2 = words[1]
	Bus3 = words[2]
	cktID = words[3]
	key = Bus1+','+Bus2+','+Bus3+','+cktID
	
	if Bus3.strip() == '0': # two winder
		if key in planningSubSet: # tf is important right now
			#print key
			CZ = words[5].strip()
			i+=1
			line = fileLines[i]
			words = line.split(',')
			R12 = float(words[0].strip())
			X12 = float(words[1].strip())
			SBASE12 = float(words[2].strip())
			#change values if values are not based on system MVA
			if CZ != '1':
				R12 = R12*100.0/SBASE12
				X12 = X12*100.0/SBASE12

			CAPEKey = findCAPEkeyPlanning[key]
			#print CAPEKey
			ThreeToTwoSubDict[CAPEKey].planningInfo = [R12,X12,SBASE12]


			i+=3 # continue to next TF
		else: # two winder of no interest
			i+=4
	else: # three winder, not interested
		i+=5



# get tf data from CAPE raw file which only contains two winders
with open(twoWinderCAPERawFile,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split("\n")


tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')

i = tfStartIndex
while i < tfEndIndex:
	line = fileLines[i]
	words = line.split(',')
	
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	Bus3 = words[2].strip()
	cktID = words[3]
	#key = Bus1+','+Bus2+','+Bus3+','+cktID

	# all tf are 2 winders, so no need to check if Bus3 == '0'

	# all the new midpoints are Bus2, so only check Bus 2
	if Bus1 in CAPEImpBusSet and Bus2 in newMidPtSet:
		#print line
		#CZ = words[5]
		# all the CZ  == 1, so no need to add CZ
		#if CZ != '1':
		#	print line
		i+=1
		line = fileLines[i]
		words = line.split(',')
		R = words[0]
		X = words[1]
		SBASE = words[2]

		CAPEKey = tmapDict[Bus2] 
		"""
		if len(findCAPEkey[Bus1]) == 1:
			CAPEKey = findCAPEkey[Bus1][0]
		else:
		"""




		if Bus1 == ThreeToTwoSubDict[CAPEKey].CAPEBus1:
			ThreeToTwoSubDict[CAPEKey].CAPEBus1Info = [R,X,SBASE]
		elif Bus1 == ThreeToTwoSubDict[CAPEKey].CAPEBus2:
			ThreeToTwoSubDict[CAPEKey].CAPEBus2Info = [R,X,SBASE]
		else:
			print line



		#ThreeToTwoSubDict[CAPEKey].CAPEinfo.append([R,X,SBASE])

		i+=3
	else:
		i+=4


# Make changes to match impedance
#ThreeToTwoSubDictNew = dict(ThreeToTwoSubDict) # copy where changes will be made


# get the difference between CAPE and planning impedances and scale them accordingly
for key in ThreeToTwoSubDict.keys():
	RPlanning =  ThreeToTwoSubDict[key].planningInfo[0]
	XPlanning = ThreeToTwoSubDict[key].planningInfo[1]

	R1 = float(ThreeToTwoSubDict[key].CAPEBus1Info[0])
	X1 = float(ThreeToTwoSubDict[key].CAPEBus1Info[1])

	R2 = float(ThreeToTwoSubDict[key].CAPEBus2Info[0])
	X2 = float(ThreeToTwoSubDict[key].CAPEBus2Info[1])

	# scale CAPE impedances to match planning impedances
	R1new, R2new = scaleImpedance(R1,R2,RPlanning)
	X1new, X2new = scaleImpedance(X1,X2,XPlanning)

	# replace with new values
	ThreeToTwoSubDict[key].CAPEBus1Info[0] = R1new
	ThreeToTwoSubDict[key].CAPEBus1Info[1] = X1new

	ThreeToTwoSubDict[key].CAPEBus2Info[0] = R2new
	ThreeToTwoSubDict[key].CAPEBus2Info[1] = X2new



# reconstruct relevant tf info
i = tfStartIndex
while i < tfEndIndex:
	line = fileLines[i]
	words = line.split(',')
	
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	Bus3 = words[2].strip()
	cktID = words[3]

	#key = Bus1+','+Bus2+','+Bus3+','+cktID

	# all tf are 2 winders, so no need to check Bus3
	if Bus1 in CAPEImpBusSet and Bus2 in newMidPtSet: # tf is relevant

		CAPEKey = tmapDict[Bus2] # get original three winder

		if Bus1 == ThreeToTwoSubDict[CAPEKey].CAPEBus1: # tf is that from primary to midpoint
			newImp2WinderLines.append(line)
			i+=1
			line = fileLines[i]
			words = line.split(',')
			NewR = ThreeToTwoSubDict[CAPEKey].CAPEBus1Info[0]
			NewX = ThreeToTwoSubDict[CAPEKey].CAPEBus1Info[1]

			words[0] = NewR
			words[1] = NewX

			nLine = reconstructLine2(words)
			newImp2WinderLines.append(nLine)


			# add next 2 lines
			i+=1
			newImp2WinderLines.append(fileLines[i])

			i+=1
			newImp2WinderLines.append(fileLines[i])
			#move to next tf
			i+=1
			continue


			
		elif Bus1 == ThreeToTwoSubDict[CAPEKey].CAPEBus2: # tf is that from secondary to midpoint
			newImp2WinderLines.append(line)
			i+=1
			line = fileLines[i]
			words = line.split(',')
			NewR = ThreeToTwoSubDict[CAPEKey].CAPEBus2Info[0]
			NewX = ThreeToTwoSubDict[CAPEKey].CAPEBus2Info[1]

			words[0] = NewR
			words[1] = NewX

			nLine = reconstructLine2(words)
			newImp2WinderLines.append(nLine)


			# add next 2 lines
			i+=1
			newImp2WinderLines.append(fileLines[i])

			i+=1
			newImp2WinderLines.append(fileLines[i])
			#move to next tf
			i+=1
			continue

	else: # not interested, just add lines
		newImp2WinderLines.append(line)
		i = addMultLines(i,fileLines,newImp2WinderLines,3)
		i+=1 # continue to next tf


			

with open(newTFFIle, 'w') as f:
	for line in newImp2WinderLines:
		f.write(line)
		f.write('\n')

