"""
Script to look at a raw file and extract all the load data within comed.
Also, outputs the total real power load in comed as the header
"""

import sys
sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2')
from getBusDataType4IncludedFn import getBusData # create a dictionary which organizes all bus data
from writeFileFn import writeToFile # function to write a list of lines to a given text file
ComedBusSet = set()
loadLines = []
#loadDataFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/loadDataScan/' + 'ComedloadData_RAW03222018.raw.txt'
#loadDataFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/loadDataScan/' + 'ComedloadData_2wnd_RAW03222018.txt'
#loadDataFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/loadDataScan/' + 'ComedloadData_FinalRAW03312018.txt'
#loadDataFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/loadDataScan/' + 'ComedloadData_RAW0501.txt'
#loadDataFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/loadDataScan/' + 'ComedloadData_Raw0414tmp_loadsplit.txt'
#loadDataFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/loadDataScan/' + 'ComedloadData_RAW0501_v2.txt'
#loadDataFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/loadDataScan/' + 'ComedloadData_RAW0620.txt'
loadDataFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/loadDataScan/' + 'ComedloadData_RAWCropped_solved.txt'
#RawFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Final Result/' + 'RAW03222018.raw'
#RawFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/' + '2wnd_RAW03222018.raw'
#RawFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/' + 'FinalRAW03312018.raw'
#RawFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/3 winder substitution/' + 'NewCAPERawClean.raw'
#RawFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/Island 34 system/' + 'Raw0414tmp_loadsplit.raw'
#RawFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/Island 34 system/' + 'Raw0414tmp.raw'
#RawFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/Island 34 system/loadSplit/' + 'RAW0501.raw'
#RawFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/Island 34 system/loadSplit/' + 'RAW0501_v2.raw'
#RawFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/Automate 345 kV mapping/Crop Raw/' + 'RAW0620.raw'
RawFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/Automate 345 kV mapping/Crop Raw/' + 'RAWCropped_solved.raw'

#RawFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/Island 34 system/' + 'tmp_island_branch_fixedv2.raw'




RawBusDataDict = getBusData(RawFile)

for Bus in RawBusDataDict.keys():
	Busarea = RawBusDataDict[Bus].area
	if Busarea == '222':
		ComedBusSet.add(Bus)


with open(RawFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split("\n")

loadStartIndex = fileLines.index('0 / END OF BUS DATA, BEGIN LOAD DATA') + 1
loadEndIndex = fileLines.index('0 / END OF LOAD DATA, BEGIN FIXED SHUNT DATA')

ComedTotalLoadMW = 0
for i in range(loadStartIndex,loadEndIndex):
	line = fileLines[i]
	words = line.split(',')
	Bus  = words[0].strip()

	if Bus in ComedBusSet:
		loadLines.append(line)
		LoadMW = float(words[5].strip())
		ComedTotalLoadMW += LoadMW


with open(loadDataFile,'w') as f:
	header = 'Total MW Load in Comed: ' +  str(ComedTotalLoadMW)
	f.write(header)
	f.write('\n')

	for line in loadLines:
		f.write(line)
		f.write('\n')
#print 'Total Load in Comed: ' +  str(ComedTotalLoadMW)