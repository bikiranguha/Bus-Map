# get a list of low priority buses (CAPE or PSSE midpoints) and the fictitious buses i created
# sort all the mismatch in the Bus reports according to MVA

import sys
sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2')
from getBusDataFn import getBusData


CAPERaw = 'RAW0530.raw'
planningRaw = 'hls18v1dyn_new.raw'

planningBusDataDict = getBusData(planningRaw)
CAPEBusDataDict = getBusData(CAPERaw)


# get all the low priority buses which will be shown separately in the mismatch data
lowPriorityBusList = []
for Bus in planningBusDataDict.keys():
	if planningBusDataDict[Bus].area == '222' and planningBusDataDict[Bus].name.endswith('M'):
		lowPriorityBusList.append(Bus)

for Bus in CAPEBusDataDict.keys():
	if CAPEBusDataDict[Bus].area == '222' and CAPEBusDataDict[Bus].name.startswith('T3W'):
		lowPriorityBusList.append(Bus)