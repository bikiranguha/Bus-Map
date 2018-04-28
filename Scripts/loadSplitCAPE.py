"""
Determines the number of step up tf connected to CAPE comed LV buses
Generates a comparison file of the number of step up tf connected to mapped LV load buses (in planning and CAPE)
Also gets the bus zone info, to be used in other scripts
"""


from checkLoadSplit import NumLoadTFDict, multTFLoad
from tryAutomateLoadSplit import loadMapDict

CAPERaw = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/Island 34 system/' +  'Raw0414tmp.raw'
listMultTFfile = 'listMultTFfileCAPE.txt'
compFile = 'compFile.txt' # csv file containing comparison info on number of tf connections

ComedBusSet = set() # all comed buses in the planning case
ComedLVBusSet = set() # all LV buses in comed
BusVoltDict = {} 
ComedLVLoadSet = set() # all LV buses in comed with load
NumLoadTFDictCAPE = {} # key: bus, value: number of step up tf connected to it
BusLine = {}
listMultTFLines = []
noMatchNumTF = set() # set of CAPE loads whose number of connected step up tf do not match that of planning
compLines = [] # lines which contain comparison info about the number of step up tf connected to CAPE and planning loads
BusZoneDict = {} # should be pretty self explanatory
BusNameDict = {} # dictionary which contains bus names in its values
BusTypeDict = {} # dictionary of Bus Type for all comed buses
#multTFLoad = set() # set of LV loads which are connected to multiple step up tf


# get the relevant comed bus sets
with open(CAPERaw, 'r') as f:
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
			BusZoneDict[Bus] = words[5].strip()
			BusNameDict[Bus] = words[1].strip("'").strip()
			BusTypeDict[Bus] = words[3].strip()
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
	NumLoadTFDictCAPE[load] = 0


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
				NumLoadTFDictCAPE[Bus1] += 1
				

	elif Bus2 in ComedLVLoadSet:
		if BusVoltDict[Bus1] >40.0:
			if status == '1':
				NumLoadTFDictCAPE[Bus2] += 1


	i+=4

for planningBus in list(multTFLoad):
	CAPEBus = loadMapDict[planningBus]
	if NumLoadTFDict[planningBus] != NumLoadTFDictCAPE[CAPEBus]:
		noMatchNumTF.add(CAPEBus)



"""
# get count or see the buses which matter
#count = 0	
for bus in NumLoadTFDictCAPE.keys():
	if NumLoadTFDictCAPE[bus] > 1:
		#count +=1
		print bus
		#multTFLoad.add(bus)
		listMultTFLines.append(BusLine[bus])

#print listMultTFLines
"""
if __name__ == "__main__":

	# comparison of number of step up tf
	for planningBus in list(multTFLoad):
		CAPEBus = loadMapDict[planningBus]
		if NumLoadTFDict[planningBus] != NumLoadTFDictCAPE[CAPEBus]:
			line = CAPEBus + ',' + planningBus + ',' + str(NumLoadTFDictCAPE[CAPEBus]) + ',' + str(NumLoadTFDict[planningBus])
			compLines.append(line)


		with open(compFile,'w') as f:
			header = 'CAPEBus,planningBus,NumLoadTFDictCAPE[CAPEBus],NumLoadTFDict[planningBus]'
			f.write(header)
			f.write('\n')
			for line in compLines:
				f.write(line)
				f.write('\n')


