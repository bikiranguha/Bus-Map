"""
	Resolves conflict where a single bus had multiple loads, by changing the cicruit id
"""


#newdir = 'Important data'
newLoadData =   'newLoadData.txt'
newLoadDatav2 =   'newLoadDataConflictResolved.txt' # outputs the new load data, with conflicts resolved
conflictResolutionLog = 'conflictResolutionLog.txt' # output log data
loadBusSet = set()
oldLines = [] #old lines which were changed
newLines = [] #new lines which were changed
loadLines = [] # updated loadLines
cktIDDict = {}

# read the old load data and change load info for conflicts
with open(newLoadData,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		words = line.split(',')
		if len(words) <2:
			continue
		Bus = words[0].strip()
		cktID = words[1].strip("'")
		#cktID = int(words[1].strip("'"))
		if Bus not in loadBusSet:
			loadBusSet.add(Bus)
			loadLines.append(line)
			if cktID.isdigit():
				cktIDDict[Bus] = int(cktID)
			else:
				cktIDDict[Bus] = 1

		else: # ckt id conflict, increment and implement ckt id
			oldLines.append(line)
			#cktID = int(words[1].strip("'"))
			newcktID = cktIDDict[Bus]+1
			cktIDDict[Bus]+=1
			words[1] = "'" + str(newcktID) + " '"
			currentline = ''
			ind = 1
			for word in words:
				currentline += word
				if ind != len(words):
					currentline +=','
					ind+=1
			loadLines.append(currentline)
			newLines.append(currentline)

# output the new load data
with open(newLoadDatav2,'w') as f:
	for line in loadLines:
		f.write(line)
		f.write('\n')

# output the new load log
with open(conflictResolutionLog,'w') as f:
	for i in range(len(oldLines)):
		oldLine = oldLines[i]
		newLine = newLines[i]
		mapStr = oldLine + '->' + newLine
		f.write(mapStr)
		f.write('\n')


