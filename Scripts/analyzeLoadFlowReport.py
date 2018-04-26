"""
 Script to make a structure out of all the flow data for the LV buses which are connected to 
 multiple step up tf
"""

from checkLoadSplit import ComedBusSet
flowReport = 'log_planning_multTFLoad.txt'

flowDict = {}

class loadReport(object):
	def __init__(self):
		self.toBus = []
		self.MWList = []
		self.MVARList = []
		self.cktID = []


with open(flowReport,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

#helperLine = '  BUS# X-- NAME --X BASKV ZONE  PU/KV  ANGLE  MW/MVAR MW/MVAR MW/MVAR   BUS# X-- NAME --X BASKV AREA CKT   MW    MVAR   RATIO   ANGLE   AMPS   %  SET A'
matchingPattern = '---------------------------------------------------------------------------------'
indices = [i for i, x in enumerate(fileLines) if matchingPattern in x] # indices of the all the relevant starting lines

for ind in indices:
	# line 1
	line = fileLines[ind]
	words = line.split()
	currentBus = words[0].strip()
	flowDict[currentBus] = loadReport()
	# line 2
	ind+=1
	line = fileLines[ind]
	words = line.split()
	words = [word for word in words if word != '']
	firstToBus = words[5].strip()
	# check if i am correct about the index of the toBus
	if firstToBus not in ComedBusSet:
		print firstToBus
	#cktID = words[10].strip()
	flowDict[currentBus].toBus.append(firstToBus)
	areaIndex = words.index('222')
	cktIndex = areaIndex + 1
	MWIndex = areaIndex + 2
	MVARIndex = areaIndex + 3
	cktID = words[cktIndex].strip()
	flowDict[currentBus].cktID.append(cktID)
	
	MW = abs(float(words[MWIndex].strip()))
	MVAR = abs(float(words[MVARIndex].strip()))
	flowDict[currentBus].MWList.append(MW)
	flowDict[currentBus].MVARList.append(MVAR)

	ind +=1

	# remaining lines
	#while 'COMED 2018,  HLS18V1, N18S OUTSIDE AND 18 INTCHNG' not in fileLines[ind] or 'M I S M A T C H' not in fileLines[ind]:
	while '222' in fileLines[ind]:
		line = fileLines[ind]
		words = line.split()
		words = [word for word in words if word != '']
		toBus = words[0].strip()
		# check if i am correct about the index of the toBus
		if toBus not in ComedBusSet:
			print toBus
		#cktID = words[10].strip()
		flowDict[currentBus].toBus.append(toBus)
		areaIndex = words.index('222')
		cktIndex = areaIndex + 1
		MWIndex = areaIndex + 2
		MVARIndex = areaIndex + 3
		cktID = words[cktIndex].strip()
		flowDict[currentBus].cktID.append(cktID)
		
		MW = abs(float(words[MWIndex].strip()))
		MVAR = abs(float(words[MVARIndex].strip()))
		flowDict[currentBus].MWList.append(MW)
		flowDict[currentBus].MVARList.append(MVAR)		
		#increment index
		if ind < len(fileLines)-1:
			ind+=1
		else:
			break
	



