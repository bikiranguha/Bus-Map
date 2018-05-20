# look at buses having mismatch greater than a certain threshold (maybe 1000 MVA)
# Look at its mismatch and branch flows and get the branch or tf where the flow is the highest, and is comparable to the mismatch
# list the branch impedance data and bus data for all these high mismatch cases, try to navigate neighbours of mapped buses in planning to see if there are any comparable impedances



import math
import sys
sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2')
from generateNeighbourImpedanceData import getBranchTFData # helps get organized branch (and tf) impedance data
from updatedMaps import MapDictNew, MapDictOld # needed to scan mappings and compare branch data (between CAPE and planning)
from getBusDataFn import getBusData # function to all relevant bus data given the raw file
from getBranchGroupFn import makeBranchGroups # to help with identifying all the fringe buses causing mismatch
flowReport = 'BusReports_RAW0509.txt'
sortedMismatchData = 'sortedMismatchData0509.txt'
CAPERaw = 'RAW0509.raw'
planningRaw = 'hls18v1dyn_1219.raw'
getMaxFlowBranches = 'mismatchAnalysisv2.txt' # contains the mismatch info as well as some info about the branch which causes max mismatch
flowDict = {}
mismatchSet = set()
areaList = []
exploredBranchSet = set() # set of branches already identified as the main cause behind mismatches
mismatchAnalysis = [] # lines which will contain the max mismatch branch data as well as the total mismatch at the bus
BusDataCAPE = getBusData(CAPERaw) # contains all the bus data for all in-service buses in CAPE
BusDataPlanning = getBusData(planningRaw) # contains all the bus data for all in-service buses in planning
BusGroupData = makeBranchGroups(CAPERaw) # contains dict for every bus which has ties

class mismatchReport(object):
	def __init__(self):
		self.toBus = []
		self.MWList = []
		self.MVARList = []
		self.MVAList = []
		self.cktID = []
		self.MismatchMVA = 0.0
		self.MismatchMW = 0.0
		self.MismatchMVAR = 0.0


def tryMatchImpedance(CAPEZ,PlanningBus1):
	# searches for possible matches using the CAPE branch impedance and PlanningBus1
	PossibleMatchList = []
	ZList = BranchTFDataDictPlanning[PlanningBus1].Z
	for currentZ in ZList:
		error = abs((currentZ-CAPEZ)/currentZ)*100
		if error < 2:
			ZIndex = BranchTFDataDictPlanning[PlanningBus1].Z.index(currentZ)
			to = BranchTFDataDictPlanning[PlanningBus1].toBus[ZIndex]
			PossibleMatchStr = printBusData(PlanningBus1,to,BusDataPlanning)
			PossibleMatchList.append(PossibleMatchStr)

	if len(PossibleMatchList) > 0:
		for match in PossibleMatchList:
			print 'Possible Match: ' + match


def printBusData(Bus1,Bus2,BusData):
	string = Bus1 + ',' + BusData[Bus1].name + ',' + BusData[Bus1].NominalVolt + ',' + Bus2 + ',' + BusData[Bus2].name + ',' + BusData[Bus2].NominalVolt
	return string

# get a set of all the cape comed buses which show mismatch
with open(sortedMismatchData,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		if 'Mismatch' in line: # header, skip
			continue
		words = line.split(',')
		Bus = words[0].strip()
		mismatchSet.add(Bus)

# get all the area codes
with open(CAPERaw,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	areaStartIndex = fileLines.index("0 / END OF TRANSFORMER DATA, BEGIN AREA DATA") + 1
	areaEndIndex = fileLines.index("0 / END OF AREA DATA, BEGIN TWO-TERMINAL DC DATA")

	for i in range(areaStartIndex,areaEndIndex):
		line = fileLines[i]
		words = line.split(',')
		area = words[0].strip()
		areaList.append(area)

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
	if currentBus not in mismatchSet: # no mismatch, so we dont care
		continue
	flowDict[currentBus] = mismatchReport()
	# line 2
	ind+=1
	line = fileLines[ind]
	words = line.split()
	words = [word for word in words if word != ''] # exclude all elements which are blanks
	firstToBus = words[5].strip()
	#cktID = words[10].strip()
	flowDict[currentBus].toBus.append(firstToBus)
	try:
		areaIndex = words.index('222')
	except:
		for area in areaList:
			if area in words:
				areaIndex = words.index(area)
	cktIndex = areaIndex + 1
	MWIndex = areaIndex + 2
	MVARIndex = areaIndex + 3
	cktID = words[cktIndex].strip()
	flowDict[currentBus].cktID.append(cktID)
	
	try: # not lumped together
		MW = float(words[MWIndex].strip())
		MVAR = float(words[MVARIndex].strip())
	except: # lumped together
		splitMWMVARWords = words[MWIndex].strip().split('-') # split the MW and MVAR info, since they are lumped together
		if splitMWMVARWords[0] != '': # only MVAR value is negative
			MW = float(splitMWMVARWords[0].strip())
			MVAR = -float(splitMWMVARWords[1].strip())
		else: # both MW and MVAR values are negative
			MW = -float(splitMWMVARWords[1].strip())
			MVAR = -float(splitMWMVARWords[2].strip())
	
	MVA = math.sqrt(MW**2 + MVAR**2)
	flowDict[currentBus].MWList.append(MW)
	flowDict[currentBus].MVARList.append(MVAR)
	flowDict[currentBus].MVAList.append(MVA)


	ind +=1
	nextLineWords = fileLines[ind].split()
	nextLineWords = [word for word in nextLineWords if word != ''] # exclude all elements which are blanks
	# remaining lines
	while '222' in nextLineWords:
		line = fileLines[ind]
		words = line.split()
		words = [word for word in words if word != '']
		toBus = words[0].strip()
		# check if i am correct about the index of the toBus
		#cktID = words[10].strip()
		flowDict[currentBus].toBus.append(toBus)
		areaIndex = words.index('222')
		cktIndex = areaIndex + 1
		MWIndex = areaIndex + 2
		MVARIndex = areaIndex + 3
		cktID = words[cktIndex].strip()
		flowDict[currentBus].cktID.append(cktID)
		
		try: # not lumped together
			MW = float(words[MWIndex].strip())
			MVAR = float(words[MVARIndex].strip())
		except: # lumped together
			splitMWMVARWords = words[MWIndex].strip().split('-') # split the MW and MVAR info, since they are lumped together
			if splitMWMVARWords[0] != '': # only MVAR value is negative
				MW = float(splitMWMVARWords[0].strip())
				MVAR = -float(splitMWMVARWords[1].strip())
			else: # both MW and MVAR values are negative
				MW = -float(splitMWMVARWords[1].strip())
				MVAR = -float(splitMWMVARWords[2].strip())
		MVA = math.sqrt(MW**2 + MVAR**2)
		flowDict[currentBus].MWList.append(MW)
		flowDict[currentBus].MVARList.append(MVAR)
		flowDict[currentBus].MVAList.append(MVA)		
		#increment index
		if ind < len(fileLines)-1:
			ind+=1
			line  = fileLines[ind]
			nextLineWords = line.split()
			nextLineWords = [word for word in nextLineWords if word != ''] # exclude all elements which are blanks

			# get the mismatch info
			if 'M I S M A T C H' in line:
				words = line.split('M I S M A T C H')
				rightSide = words[1].strip()
				rightSideWords = rightSide.split()
				# Deal with cases where the MW and MVAR values are lumped together (when MVAR or both MW and MVAR are negative)
				try: # not lumped together
					MW = float(rightSideWords[0].strip())
					MVAR = float(rightSideWords[1].strip())
				except: # lumped together
					rightSideWordsTogether = rightSideWords[0].strip().split('-')
					if rightSideWordsTogether[0] != '': # only MVAR value is negative
						MW = float(rightSideWordsTogether[0].strip())
						MVAR = -float(rightSideWordsTogether[1].strip())
					else: # both MW and MVAR values are negative
						MW = -float(rightSideWordsTogether[1].strip())
						MVAR = -float(rightSideWordsTogether[2].strip())
				MVA = math.sqrt(MW**2 + MVAR**2)
				flowDict[currentBus].MismatchMVA = MVA
				flowDict[currentBus].MismatchMW = MW
				flowDict[currentBus].MismatchMVAR = MVAR


		else:
			break

"""
# analyse the mismatch and get the branch which has the highest MVA
for Bus in flowDict.keys():
	if flowDict[Bus].MismatchMVA < 1000:
		continue

	maxMismatch = max(flowDict[Bus].MVAList)
	if maxMismatch/flowDict[Bus].MismatchMVA > 0.6:
		maxMismatchInd  = flowDict[Bus].MVAList.index(maxMismatch)
		to = flowDict[Bus].toBus[maxMismatchInd]
		currentBranch = Bus+','+to
		currentBranchReverse = to+','+Bus
		if currentBranch in exploredBranchSet or currentBranchReverse in exploredBranchSet: # branch already included
			continue
		exploredBranchSet.add(currentBranch)
		string = Bus + ',' + to + ',' + str(maxMismatch) + ',' + str(flowDict[Bus].MismatchMVA)
		mismatchAnalysis.append(string)
"""

for Bus in flowDict.keys():
	if flowDict[Bus].MismatchMVA < 1000:
		continue
	toBusList = flowDict[Bus].toBus

	for nBus in toBusList:
		if nBus in flowDict.keys():
			nBusInd = flowDict[Bus].toBus.index(nBus)
			if flowDict[Bus].MVAList[nBusInd] > 1000 and flowDict[nBus].MismatchMVA > 500:
				currentBranch = Bus + ',' + nBus
				currentBranchReverse = nBus + ',' + Bus
				if currentBranch in exploredBranchSet or currentBranchReverse in exploredBranchSet: # branch already included
					continue
				exploredBranchSet.add(currentBranch)
				string = Bus + ',' + nBus + ',' + str(flowDict[Bus].MVAList[nBusInd]) + ',' + str(flowDict[Bus].MismatchMVA)
				mismatchAnalysis.append(string)
		else: # no mismatch seen at this nBus
			continue



# get the mapping dict (including all manual mapping)
# list all the branches where the impedances dont match
# try to find other branches which do match

BranchTFDataDictCAPE = getBranchTFData(CAPERaw)
BranchTFDataDictPlanning = getBranchTFData(planningRaw)

print 'Comparison of all the mismatch branches which could be automated:'
#print 'Format:CAPEBus1,CAPEBus2,CAPEZ,planningBus1,planningBus2,planningZ'
print 'Format:CAPEBus1,CAPEBus1Name, CAPEBus1Volt,CAPEBus2,CAPEBus2Name, CAPEBus2Volt,planningBus1,planningBus1Name, planningBus1Volt,planningBus2,planningBus2Name, planningBus2Volt,CAPEZ,planningZ'
for branch in list(exploredBranchSet):
	branchWords = branch.split(',')
	CAPEBus1 = branchWords[0].strip()
	CAPEBus2 = branchWords[1].strip()
	IsBranch =  BranchTFDataDictCAPE
	toBusIndex = BranchTFDataDictCAPE[CAPEBus1].toBus.index(CAPEBus2)
	IsBranch = BranchTFDataDictCAPE[CAPEBus1].IsBranch[toBusIndex]
	if IsBranch == 0: # branch is a tf
		continue
	#try:
	planningBus1 = MapDictNew[CAPEBus1]
	planningBus2 = MapDictNew[CAPEBus2]
	#except: # for branches constituting midpoints, may have to deal with myself
	#	continue

	# get CAPE branch impedance
	
	CAPEZ = BranchTFDataDictCAPE[CAPEBus1].Z[toBusIndex]

	# get CAPE branch impedance
	try:
		toBusIndex = BranchTFDataDictPlanning[planningBus1].toBus.index(planningBus2)
		planningZ = BranchTFDataDictPlanning[planningBus1].Z[toBusIndex]	
	except: # no direct branch connection in planning
		partialString = printBusData(CAPEBus1,CAPEBus2,BusDataCAPE)
		partialString += ',' + printBusData(planningBus1,planningBus2,BusDataPlanning)
		string = partialString + ',' + 'No direct branch connection in planning'
		if CAPEBus1 in BusGroupData.keys() or CAPEBus2 in BusGroupData.keys():
			string += ',One of the CAPE Buses has ties'
		print string
		tryMatchImpedance(CAPEZ,planningBus1)
		tryMatchImpedance(CAPEZ,planningBus2)

		continue

	impedanceMismatch = abs((planningZ-CAPEZ)/planningZ)*100 
	if impedanceMismatch > 2:
		partialString = printBusData(CAPEBus1,CAPEBus2,BusDataCAPE)
		partialString += ',' +  printBusData(planningBus1,planningBus2,BusDataPlanning)
		string = partialString + ',' + str(CAPEZ) + ',' + str(planningZ)
		if CAPEBus1 in BusGroupData.keys() or CAPEBus2 in BusGroupData.keys():
			string += ',One of the CAPE Buses has ties'
		print string
		tryMatchImpedance(CAPEZ,planningBus1)
		tryMatchImpedance(CAPEZ,planningBus2)



# now match bus names, if there is a high degree of correlation between CAPE bus name (or bus substation) and planning bus name, then there is a good prob that mapping is correct
# single out all mismatch cases which are due to fringe buses, ie, only one non-zero branch flow, and the other branches are just ties

with open(getMaxFlowBranches,'w') as f:
	f.write('FromBus,toBus,branchMismatchMVA,totalMismatchMVA')
	f.write('\n')
	for line in mismatchAnalysis:
		f.write(line)
		f.write('\n')
