# carries out the normal 2w->2w transformer substitutions specified in tf2tfmaps_2winder_cleaned.txt 

from tfMapFnv3 import doTFMaps
from getBusDataFn import getBusData
planningRaw = 'hls18v1dyn_1219.raw'
newRawFile = 'RAW0620.raw'
oldTFData = 'TFSubManualDone.txt'
newTFData = 'TFSubGenTFFixRemaining.txt'
#BusDataDicts are needed for nominal voltage info only
planningBusDataDict = getBusData(planningRaw)
CAPEBusDataDict = getBusData(newRawFile)


input_file = 'tf2tfmaps_2winder_cleaned.txt'
tfSubLines = []
with open(input_file,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

# get the relevant inputs
startIndex = fileLines.index('Normal two winder substitutions from mapping_confirmed_0606:') + 1
for i in range(startIndex,len(fileLines)):
	line = fileLines[i]
	tfSubLines.append(line)


# do the tf subs on the old tf data to get new tf data
doTFMaps(tfSubLines,oldTFData,newTFData,planningBusDataDict,CAPEBusDataDict)