# generates a host of data (bus, branch, load, gen, tf, shunt and misc) which does not contain tf info


PSSErawFile = 'hls18v1dyn_1219.raw'
croppedBusFile = 'croppedBusFile.txt'
croppedLoadFile = 'croppedLoadFile.txt'
croppedoutBranchFile = 'croppedBranchFile.txt'
croppedtfFile = 'croppedtfFile.txt'
croppedfsFile = 'croppedfsFile.txt'
croppedssFile = 'croppedssFile.txt'
croppedGenFile = 'croppedGenFile.txt'
BoundaryMapClean = 'BoundaryplanningMapCleaned.txt' # boundary bus mappings
boundaryFile = 'boundaryFile.txt'
BoundaryMapManual = 'BoundaryMapManual.txt' # special maps of boundary buses
PSSEBusData = 'PSSE_bus_data.txt'
changeLog = 'changeBusNoLog.txt'

comedBusSet = set()
# crop out Comed bus data
keepComed = ['272017','270886','270771','270673'] # special comed buses, which only connect to other non-comed buses
croppedBusLines = [] # contains bus data with comed cropped out
changeNameDict = {}
OldBusSet = set()



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
        #NewBusSet.add(NewBus)
        changeNameDict[OldBus] = NewBus

with open(PSSEBusData,'r') as f:
    buscontent = f.read()
    BusLines = buscontent.split('\n')
    for line in BusLines:

        words = line.split(',')
        #if len(words)<2: # continue to next iteration of loop if its a blank line
        #    continue
        #BusCode = words[3].strip()
        area = words[4].strip()
        Bus = words[0].strip()
        #AllBuses.append(Bus)
        if Bus in keepComed:
        	#comedBusSet.add(Bus)
        	croppedBusLines.append(line)
        	continue
        if area != '222':
        	if Bus != '348881':
        		croppedBusLines.append(line)
       		
        else:
        	comedBusSet.add(Bus)

with open(croppedBusFile,'w') as f:
	for line in croppedBusLines:
		f.write(line)
		f.write('\n')



with open(PSSErawFile,'r') as f:
    filecontent = f.read()
    fileLines = filecontent.split("\n")

croppedLoadLines = []
# crop out comed load data
loadStartIndex = fileLines.index('0 / END OF BUS DATA, BEGIN LOAD DATA') + 1
loadEndIndex = fileLines.index('0 / END OF LOAD DATA, BEGIN FIXED SHUNT DATA')

for i in range(loadStartIndex,loadEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus = words[0].strip()
	#area = words[3].strip()
	if Bus not in comedBusSet:
		if Bus != '272017': # Load already included in comed gen data
			croppedLoadLines.append(line)

with open(croppedLoadFile,'w') as f:
	for line in croppedLoadLines:
		f.write(line)
		f.write('\n')

####################

# crop tf data
croppedtfLines = []
tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')

i = tfStartIndex

while i<tfEndIndex:
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	Bus3 = words[2].strip()
	if Bus1 not in comedBusSet :
		if Bus3 == '0':
			for j in range(4):
				croppedtfLines.append(line)
				i+=1
				line = fileLines[i]
		else:
			for j in range(5):
				croppedtfLines.append(line)
				i+=1
				line = fileLines[i]	
	else:
		if Bus3 == '0':
			i+=4
		else:
			i+=5


with open(croppedtfFile,'w') as f:
	for line in croppedtfLines:
		f.write(line)
		f.write('\n')




#########
# crop out comed fixed shunt and switched shunt data
croppedfsLines = []

fixedShuntStartIndex = fileLines.index('0 / END OF LOAD DATA, BEGIN FIXED SHUNT DATA') + 1
fixedShuntEndIndex = fileLines.index('0 / END OF FIXED SHUNT DATA, BEGIN GENERATOR DATA')
for i in range(fixedShuntStartIndex,fixedShuntEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus = words[0].strip()
	if Bus not in comedBusSet:
		croppedfsLines.append(line)

with open(croppedfsFile,'w') as f:
	for line in croppedfsLines:
		f.write(line)
		f.write('\n')




croppedssLines = []
switchedShuntStartIndex = fileLines.index('0 / END OF FACTS DEVICE DATA, BEGIN SWITCHED SHUNT DATA') + 1
switchedShuntEndIndex = fileLines.index('0 / END OF SWITCHED SHUNT DATA, BEGIN GNE DATA')

for i in range(switchedShuntStartIndex,switchedShuntEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus = words[0].strip()
	if Bus not in comedBusSet:
		croppedssLines.append(line)

with open(croppedssFile,'w') as f:
	for line in croppedssLines:
		f.write(line)
		f.write('\n')

#############
# get boundary branches
BoundaryMapDict = {}
boundaryLines = []
BoundaryPSSE = set()
with open(BoundaryMapClean,'r') as f:
    boundaryfilecontent = f.read()
    boundaryfileLines = boundaryfilecontent.split("\n")
    for line in boundaryfileLines:
    	words = line.split('->')
    	if len(words)<2:
    		continue
    	PSSEBus = words[0].strip()
    	CAPEBus = words[1].strip()
    	BoundaryMapDict[PSSEBus] = CAPEBus
    	BoundaryPSSE.add(PSSEBus)


def changeBus(Bus,words,MapDict,busChangeDict):
	#print Bus
	newLine = ''
	newBus = MapDict[Bus]
	# change bus number if necessary
	if newBus in changeNameDict.keys():
		newBus = changeNameDict[newBus]

	lennewBus = len(newBus)
	newBus = ' '*(6 - lennewBus) + newBus
	for word in words:
		if word.strip() == Bus:
			word = newBus
			newLine += word
			newLine += ','
		else:
			newLine += word
			newLine += ','
	#print newLine
	return newLine[:-1]

branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA') + 1
branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')

for i in range(branchStartIndex, branchEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	if Bus1 in BoundaryPSSE:
		if Bus2 not in comedBusSet:
			newLine = changeBus(Bus1,words,BoundaryMapDict,changeNameDict)
			boundaryLines.append(newLine)
			continue
	if Bus2 in BoundaryPSSE:
		if Bus1 not in comedBusSet:
			newLine = changeBus(Bus2,words,BoundaryMapDict,changeNameDict)
			boundaryLines.append(newLine)
			continue


# Now manually do the remaining 4 boundary mappings
specialBoundary = {}
with open(BoundaryMapManual,'r') as f:
	content = f.read()
	lines = content.split('\n')
	for line in lines:
		words = line.split('->')
		org = words[0].strip()
		new = words[1].strip()
		specialBoundary[org] = new



for i in range(branchStartIndex, branchEndIndex):
	line = fileLines[i]
	for key in specialBoundary.keys():
		if key in line:
			#print line
			newBranch = specialBoundary[key]
			newBranchsplit = newBranch.split(',')
			words = line.split(',')
			Bus1 = newBranchsplit[0]
			Bus2 = newBranchsplit[1]
			words[0] = ' '*(6-len(Bus1)) + Bus1
			words[1] = ' '*(6-len(Bus2)) + Bus2

			if len(newBranchsplit) >2 : # special case where ckt id needs to be kept as '1 '
				words[2] = '1 ' 
			currentLine = ''
			for word in words:
				currentLine +=word
				currentLine += ','
			boundaryLines.append(currentLine[:-1])


# Then add boundaryLines to all other branch lines (No Bus in branch belong to comed or bus 348881)
comedBusSet.add('348881') # Special case which needs to be excluded from the cropped out region
branchLines = []
for i in range(branchStartIndex, branchEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	if (Bus1 not in comedBusSet) and (Bus2 not in comedBusSet):
		branchLines.append(line)

with open(croppedoutBranchFile,'w') as f:
	for line in boundaryLines:
		f.write(line)
		f.write('\n')

	for line in branchLines:
		f.write(line)
		if branchLines.index(line) != (len(branchLines)-1):
			f.write('\n')


# Generator data cropping
genLines = []
genStartIndex = fileLines.index('0 / END OF FIXED SHUNT DATA, BEGIN GENERATOR DATA')+1
genEndIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA')

for i in range(genStartIndex, genEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus = words[0].strip()
	if Bus not in comedBusSet:
		genLines.append(line)

with open(croppedGenFile,'w') as f:
	for line in genLines:
		f.write(line)
		if genLines.index(line) != (len(genLines)-1):
			f.write('\n')

