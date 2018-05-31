"""
Scan conflicts generated from autoMap345 and see whether all the conflicts are in the same CAPE 
substation
"""

from getBusNameDict import BusNum2SubNameDict

conflictsFile = 'conflicts.txt'

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

		# compare all the conflicts in the current list
		refSubName = BusNum2SubNameDict[conflictList[0]]
		for j in range(1,len(conflictList)):
			compareSubName = BusNum2SubNameDict[conflictList[j]]
			if compareSubName != refSubName: # if the conflicts are not within the same substation, print out the list
				print str(conflictList)


		i+=1
		continue
	else: # line not of any interest
		i+=1
		continue