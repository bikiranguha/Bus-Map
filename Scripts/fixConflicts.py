"""
Scan conflicts generated from autoMap345 and see whether all the conflicts are in the same CAPE 
substation
"""
import sys
sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2')
# Data import from other files
from getBusDataFn import getBusData
from getBusNameDict import BusNum2SubNameDict
from getBranchGroupFnPlanning import makeBranchGroups # function to generate a group of ties (including itself) of the bus given as key
import itertools
conflictsFile = 'conflicts.txt'
planningRaw = 'hls18v1dyn_new.raw'
voltErrorList = []
angErrorList = []


# get Bus info
BusDataDict = getBusData(planningRaw)


BranchGroupDict = makeBranchGroups(planningRaw) # every value here is a set
with open(conflictsFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

# start scanning the conflicts
i=0
while i < len(fileLines):
	line = fileLines[i]

	if line == '':
		i+=1
		continue

	if 'Previous' in line: # start with the line containing previous mapping
		conflictList = []
		words = line.split(':')
		if ',' in line:
			RHS = words[1].strip()
			RHSWords = RHS.split(',')
			for Bus in RHSWords:
				conflictList.append(Bus.strip().strip("'"))
		else:
			Bus = words[1].strip().strip("'")
			conflictList.append(Bus)

		# continue to next line (containing new mapping) and do the same thing over again
		i+=1
		line  = fileLines[i]
		words = line.split(':')
		if ',' in line:
			RHS = words[1].strip()
			RHSWords = RHS.split(',')
			for Bus in RHSWords:
				conflictList.append(Bus.strip().strip("'"))
		else:
			Bus = words[1].strip().strip("'")
			conflictList.append(Bus)		

		"""
		# compare all the conflicts in the current list
		try:
			BranchGroup = list(BranchGroupDict[conflictList[0]])
			for j in range(1,len(conflictList)):
				currentBus = conflictList[j]
				if currentBus not in BranchGroup:
					print conflictList
		except:
			print 'Buses do not belong in group'
		
		# see if conflicts are within the same substation
		refSubName = BusNum2SubNameDict[conflictList[0]]
		for j in range(1,len(conflictList)):
			compareSubName = BusNum2SubNameDict[conflictList[j]]
			if compareSubName != refSubName: # if the conflicts are not within the same substation, print out the list
				print str(conflictList)
		"""
		# get the max mismatch in voltage
		for conflictPair in itertools.combinations(conflictList,2):
			Volt1 = float(BusDataDict[conflictPair[0]].voltpu)
			Volt2 = float(BusDataDict[conflictPair[1]].voltpu)
			VoltError = abs(Volt1 - Volt2)
			voltErrorList.append(VoltError)

			Ang1 = float(BusDataDict[conflictPair[0]].angle)
			Ang2 = float(BusDataDict[conflictPair[1]].angle)
			angError = abs(Ang1 - Ang2)
			angErrorList.append(angError)



		i+=1
		continue
	else: # line not of any interest
		i+=1
		continue

maxVoltDiff  = max(voltErrorList)
maxAngDiff = max(angErrorList)

print 'Max Volt difference: ', maxVoltDiff
print 'Max Ang difference: ', maxAngDiff