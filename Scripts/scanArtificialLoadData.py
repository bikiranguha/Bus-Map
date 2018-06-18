# generate cleaned Artificial Load bus from and to info

import sys
sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2')
from getBusDataFn import getBusData

ArtificialLoadBusFile = 'ArtificialLoadBusFile.txt'
ALDict = {}
CAPERaw = 'RAW0602.raw'
ALBusList = 'ALBusList.txt' # file which contains cleaned up version of all from-to branches for artificial loads
CAPEBusDataDict = getBusData(CAPERaw)

with open(ArtificialLoadBusFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'List of buses' in line:
			continue
		if line == '':
			continue

		words = line.split(',')
		ALBus = words[0].strip()
		fromBusSet = set()
		for i in range(3,len(words)):
			word = words[i].strip()
			fromBusSet.add(word)

		ALDict[ALBus] = fromBusSet




with open('ALBusList.txt','w') as f:
	f.write('FromBus,Name,Volt=toBus(Artificial Load),Name,Volt')
	f.write('\n')
	for key in ALDict.keys():
		toBusName = CAPEBusDataDict[key].name
		toBusVolt = CAPEBusDataDict[key].NominalVolt

		fromBusSet = ALDict[key]

		for fromBus in list(fromBusSet):
			fromBusName = CAPEBusDataDict[fromBus].name
			fromBusVolt = CAPEBusDataDict[fromBus].NominalVolt
			string = fromBus + ',' + fromBusName + ',' + fromBusVolt 
			string += '=' +  key + ',' + toBusName + ',' + toBusVolt
			f.write(string)
			f.write('\n')
