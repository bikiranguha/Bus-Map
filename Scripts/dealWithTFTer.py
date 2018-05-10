"""
Script which deals with the tertiary of transformers
By dealing, i mean they are mapped to the tf primary if they do not have load or any other branches
"""
import shutil

latestRaw = 'RAW0501.raw'
tertiaryMap = 'tertiaryMap.txt'
tertiaryTFList = [] # list of tertiary tf buses
tertiaryBusLines = [] # list of bus data for the tertiary buses
BusVoltDict = {}
BusNameDict = {}
ComedBusSet = set()
BranchConnDict = {} # branch connection dict of all comed buses
MaptoTFDict = {} # key: tertiary tf bus, value: HV side of tf, bus to map to
mappedtoTFSet = set() # set of all the tertiaries which have been mapped
with open(latestRaw, 'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if ('PSS' in line) or ('COMED' in line) or ('DYNAMICS' in line):
			continue
		if 'END OF BUS DATA' in line:
			break
		words = line.split(',')
		if len(words) <2:
			continue
		Bus = words[0].strip()
		area = words[4].strip()
		BusType = words[3].strip()
		if area == '222':
			#BusAngleDict[Bus] = angle
			ComedBusSet.add(Bus)
			BusVolt = float(words[2].strip())
			BusVoltDict[Bus] =BusVolt
			name = words[1].strip("'").strip()
			BusNameDict[Bus] = name
			#if BusVolt < 40.0:
			#	ComedLVBusSet.add(Bus)
			if name.endswith('TER') and BusType != '4':
				tertiaryBusLines.append(line)
				tertiaryTFList.append(Bus)


loadStartIndex = fileLines.index('0 / END OF BUS DATA, BEGIN LOAD DATA') + 1
loadEndIndex = fileLines.index('0 / END OF LOAD DATA, BEGIN FIXED SHUNT DATA')

# scan load data to populate load sets and dictionaries
for i in range(loadStartIndex,loadEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus  = words[0].strip()
	Load = float(words[5].strip())

	# check if load connected to tertiary bus
	if Bus in tertiaryTFList and Load > 0.0:
		print 'Load connected to tertiary Bus ' +  Bus

# see if any tertiary bus has in-service branches
def BusAppend(Bus,NeighbourBus,NeighbourDict):
	if Bus not in NeighbourDict.keys():
		NeighbourDict[Bus] = []
	NeighbourDict[Bus].append(NeighbourBus)


branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA') + 1
branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')

for i in range(branchStartIndex, branchEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	status = words[-5].strip()

	if Bus1 in ComedBusSet or Bus2 in ComedBusSet:
		if status == '1':
			BusAppend(Bus1,Bus2,BranchConnDict)
			BusAppend(Bus2,Bus1,BranchConnDict)

for Bus in tertiaryTFList:
	if Bus in BranchConnDict.keys():
		print 'Bus ' + Bus + ' has in-service branches'


# checked that no load or branches connected to any of the tertiary buses
# map them to the HV side of the transformer
# but before that, check if only one tf is connected to the bus


tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')
i = tfStartIndex
# search tf data to populate LVTFDataDict
while i < tfEndIndex:
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	status = words[11].strip()
	#tfname = words[10].strip("'").strip()

	if Bus1 in tertiaryTFList:
		if status == '1':
			if Bus1 not in mappedtoTFSet:
				MaptoTFDict[Bus1] = Bus2
				mappedtoTFSet.add(Bus1)
			else:
				print 'Bus ' + Bus1 + ' is connected to multiple transformers.'
 
	elif Bus2 in tertiaryTFList:
		if status == '1':
			if Bus2 not in mappedtoTFSet:
				MaptoTFDict[Bus2] = Bus1
				mappedtoTFSet.add(Bus2)
			else:
				print 'Bus ' + Bus2 + ' is connected to multiple transformers.'

	i+=4

# Investigate why Bus 5418 is connected to two midpoints and why Bus 275174 is connected to so many tf
print 'Issues with Bus 5418 and 275174 verified.'
print 'Bus 5418 case has been checked. It was originally connected to multiple three winders, so its ok.'
print 'Bus 275174 has been mapped to two three winders. Since the original 3 winders in CAPE had the same parameters, substituting with the same parameters is OK'
# check if all the tertiaries have been mapped
for Bus in tertiaryTFList:
	if Bus not in mappedtoTFSet:
		print 'Bus ' + Bus + ' not mapped yet'



with open(tertiaryMap,'w') as f:
	f.write('Primary of TF mapped to its Tertiary:')
	f.write('\n')
	for Bus in MaptoTFDict.keys():
		string = MaptoTFDict[Bus] + '->' + Bus
		f.write(string)
		f.write('\n')

from manualMapper import MapChange
planningRaw = 'hls18v1dyn_1219.raw'
CAPERaw = 'RAW0501.raw'
newRawFile = 'RAW0501.raw'
originalCase = 'CAPE'
changeFile = tertiaryMap
MapChange(planningRaw,changeFile,CAPERaw,newRawFile,originalCase)

# copy to the given location
destTFData = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders\Automate 345 kV mapping/'
shutil.copy(newRawFile,destTFData)