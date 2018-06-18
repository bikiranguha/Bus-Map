import sys
sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/Automate 345 kV mapping')
sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2')
from getBusDataFn import getBusData
CAPERaw  = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/Automate 345 kV mapping/' +  'RAW0602.raw'

toIncludeBusSet = set() # important set of buses
BusLines = [] # list of important buses
BranchLines = [] # list of important branches
LoadLines = [] # list of important loads
tfLines = [] # list of important tf
genLines = [] # list of important generators
CAPEBusDataDict = getBusData(CAPERaw)


for Bus in CAPEBusDataDict.keys():
	if CAPEBusDataDict[Bus].area != '222':
		toIncludeBusSet.add(Bus)
	elif float(CAPEBusDataDict[Bus].NominalVolt) >= 345.0:
		toIncludeBusSet.add(Bus)
	elif CAPEBusDataDict[Bus].type == '2':
		toIncludeBusSet.add(Bus)




with open(CAPERaw,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

	# grab bus data
	for line in fileLines:
		if ('PSS' in line) or ('COMED' in line) or ('DYNAMICS' in line):
			continue
		if 'END OF BUS DATA' in line:
			break
		words = line.split(',')
		if len(words) <2:
			continue
		
		Bus = words[0].strip()
		if Bus in toIncludeBusSet:
			BusLines.append(line)


# grab load data
loadStartIndex = fileLines.index('0 / END OF BUS DATA, BEGIN LOAD DATA') + 1
loadEndIndex = fileLines.index('0 / END OF LOAD DATA, BEGIN FIXED SHUNT DATA')

for i in range(loadStartIndex,loadEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus = words[0].strip()
	if Bus in toIncludeBusSet:
		LoadLines.append(line)


# grab line data
branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA') + 1
branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')

for i in range(branchStartIndex, branchEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	if Bus1 in toIncludeBusSet or Bus2 in toIncludeBusSet:
		BranchLines.append(line)

# grab gen data
genStartIndex = fileLines.index('0 / END OF FIXED SHUNT DATA, BEGIN GENERATOR DATA')+1
genEndIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA')

for i in range(genStartIndex, genEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus = words[0].strip()
	if Bus in toIncludeBusSet:
		genLines.append(line)

# grab tf data
tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')

i = tfStartIndex

while i<tfEndIndex:
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()

	if Bus1 in toIncludeBusSet or Bus2 in toIncludeBusSet:
		for j in range(4):
			tfLines.append(line)
			i+=1
			line = fileLines[i]		

	else:
		i+=4


with open('GenData.txt','w') as f:
	for line in genLines:
		f.write(line)
		f.write('\n')
