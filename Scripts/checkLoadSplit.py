# check all LV comed buses in planning whethere is a case of load split
# load split happens when a LV load bus is connected to multiple step up transformers

planningRaw = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/' +  'hls18v1dyn_1219.raw'
#planningRaw = 'hls18v1dyn_1219.raw'
listMultTFfile = 'listMultTFfile.txt'

ComedBusSet = set() # all comed buses in the planning case
ComedLVBusSet = set() # all LV buses in comed
BusVoltDict = {} 
ComedLVLoadSet = set() # all LV buses in comed with load
NumLoadTFDict = {} # key: bus, value: number of step up tf connected to it
BusLine = {}
listMultTFLines = []
multTFLoad = set() # set of LV loads which are connected to multiple step up tf


alreadySplitList = ['273330','273331','273152','273153','273334']

# get the relevant comed bus sets
with open(planningRaw, 'r') as f:
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
		BusVolt = float(words[2].strip())
		#angle = float(words[8].strip())
		area = words[4].strip()
		#AreaDict[Bus] = area

		if area == '222':
			#BusAngleDict[Bus] = angle
			BusVoltDict[Bus] = BusVolt
			BusLine[Bus] = line
			ComedBusSet.add(Bus)
			if BusVolt < 40.0:
				ComedLVBusSet.add(Bus)


loadStartIndex = fileLines.index('0 / END OF BUS DATA, BEGIN LOAD DATA') + 1
loadEndIndex = fileLines.index('0 / END OF LOAD DATA, BEGIN FIXED SHUNT DATA')

# scan load data to populate load sets and dictionaries
for i in range(loadStartIndex,loadEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus  = words[0].strip()
	Load = float(words[5].strip())
	if Bus in ComedLVBusSet and Load > 0.0:
		ComedLVLoadSet.add(Bus)


for load in list(ComedLVLoadSet):
	NumLoadTFDict[load] = 0


tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')
i = tfStartIndex
# search tf data to see which LV load buses have multiple step up tf connected to them
while i < tfEndIndex:
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	status = words[11].strip()
	if Bus1 in ComedLVLoadSet:
		if BusVoltDict[Bus2] >40.0:
			if status == '1':
				NumLoadTFDict[Bus1] += 1
				

	elif Bus2 in ComedLVLoadSet:
		if BusVoltDict[Bus1] >40.0:
			if status == '1':
				NumLoadTFDict[Bus2] += 1


	i+=4


# get count or see the buses which matter
#count = 0	
for bus in NumLoadTFDict.keys():
	if NumLoadTFDict[bus] > 1 and bus not in alreadySplitList:
		#count +=1
		#print bus
		multTFLoad.add(bus)
		listMultTFLines.append(BusLine[bus])

#print listMultTFLines

if __name__ == "__main__":

	with open(listMultTFfile,'w') as f:
		f.write('List of loads which may have to be split:')
		f.write('\n')
		for line in listMultTFLines:
			f.write(line)
			f.write('\n')