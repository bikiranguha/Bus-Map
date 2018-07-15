"""
Get all the buses which are connected directly to 345 comed buses and are not tf midpoints
"""

import sys
from getFringeBusesv3 import * # ImpBusPathSet, necessaryMidpointSet and ArtificialLoadBusSet are imported from here
sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2')
sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/Automate 345 kV mapping')
from getBusDataFn import getBusData # create a dictionary which organizes all bus data
from getTFDataFn import getTFData
from writeFileFn import writeToFile
from GenDataFn import getGenData
CAPERaw = 'RAW0602.raw'
stepDown345File = 'stepDown345File.txt'
CAPEBusDataDict = getBusData(CAPERaw)
TFDataDict = getTFData(CAPERaw)
GenDataDict = getGenData(CAPERaw)
stepDownLines = []
for Bus in CAPEBusDataDict.keys():
	Area = CAPEBusDataDict[Bus].area 
	Name = CAPEBusDataDict[Bus].name
	Volt = float(CAPEBusDataDict[Bus].NominalVolt)
	if Area == '222' and Volt >= 345.0 and Bus in TFDataDict.keys():
		if Name.startswith('T3W') or Name.endswith('M'):
			continue
		toBusList = TFDataDict[Bus].toBus

		for tfN in toBusList:
			tfVolt = float(CAPEBusDataDict[tfN].NominalVolt)
			if tfN not in ImpBusPathSet and tfN not in necessaryMidpointSet and tfN not in ArtificialLoadBusSet and tfVolt < 345.0:
				print tfN
			"""
			tfName = CAPEBusDataDict[tfN].name
			tfVolt = CAPEBusDataDict[tfN].NominalVolt
			string = tfN + ',' + tfName + ',' + tfVolt
			stepDownLines.append(string)
			"""

for Bus in CAPEBusDataDict.keys():
	Area = CAPEBusDataDict[Bus].area 
	BusType = 	CAPEBusDataDict[Bus].type 
	 
	if Area == '222' and BusType == '2':
		GenStatus = GenDataDict[Bus].status
		if Bus not in ImpBusPathSet and GenStatus == '1':
			print Bus 
#writeToFile(stepDown345File,stepDownLines,'')
