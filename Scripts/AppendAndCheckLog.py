"""
Update 3 winder substituion log and check which 3 winders still remain to be substituted

"""



tf3winderchangeLogOld = 'tf3winderChangeLogIter2.txt' # contains subs in change3winderData and NewMidpointTFFix
tf3winderchangeLogNew = 'tf3winderChangeLogIter3.txt'
FinalSolFile = 'Final_sol_3w.txt' # TF substitutions which are special
delete4winderNoAlignMent = 'deleteOld4winderdataNoAlignment.txt' # file which consists of 3 winders which were originally 4 winders, will be subbed manually

NewMapDict = {} # for all new subs: key: cape tf id, value: planning tf sub
AllMapDict  = {} # for all 3w subs: key: cape tf id, value: planning tf sub
newLogLines = [] # all the log lines, updated
FourWinderListNoAlign = [] # list of tf which dont need to be included in the log file


# read the file and get the subs
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

		NewMapDict[CAPEPart] = planningPart

# get a set of all the tf which were originally 4 winders and which have been replaced with 2 winder data
with open(delete4winderNoAlignMent,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		FourWinderListNoAlign.append(line.strip())




# update log data with changes
with open(tf3winderchangeLogOld,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		words = line.split('->')
		CAPEPart = words[0].strip()
		# original 4 winders, will be manually changed later on
		if CAPEPart in FourWinderListNoAlign:
			continue
		# update with new subs
		if CAPEPart in NewMapDict.keys():
			nLine = CAPEPart + '->' + str(NewMapDict[CAPEPart])
			newLogLines.append(nLine)
			AllMapDict[CAPEPart] = NewMapDict[CAPEPart]
		else: # no change, just add
			planningPart = words[1].strip()
			if planningPart == "['0,0,0']":
				planningPart = '0'
			line = CAPEPart + '->' + planningPart
			AllMapDict[CAPEPart] = planningPart
			newLogLines.append(line)

# new log output
with open(tf3winderchangeLogNew,'w') as f:
	for line in newLogLines:
		f.write(line)
		f.write('\n')

# check to see if any tf subs remain
for key in AllMapDict.keys():
	if AllMapDict[key] == '':
		print 'Still No Sub: ' +  key + '->' + AllMapDict[key]


