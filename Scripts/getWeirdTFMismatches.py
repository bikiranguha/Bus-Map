# find all the 40 kV or lower buses which are causing significant mismatch ( > 500 MVA) and which have step up tf connections
# also these tf cannot be mapped initially (by the CS guys)
import sys
sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2')
from getTFDataFn import getTFData
from getBusDataFn import getBusData
CAPERaw = 'RAW0509.raw'
manualMapFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/' +  'mapped_buses_cleaned0407.csv'
sortedMismatchData = 'sortedMismatchData0509.txt'
TFDataDict = getTFData(CAPERaw) # get TF data
BusDataDict = getBusData(CAPERaw) #  get Bus data
ManualMapDict = {}

# get the manual maps
with open(manualMapFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		words = line.split(',')
		if len(words) <2:
			continue
		PSSEBus = words[0].strip()
		CAPEBus = words[5].strip()
		PSSEBusCode = words[2].strip()
		if 'M' in PSSEBusCode:
		    continue
		if PSSEBus in ['NA','']:
		    continue
		if CAPEBus in ['NA','']:
		    continue

		ManualMapDict[CAPEBus] = PSSEBus

# get the mismatch data
with open(sortedMismatchData,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'Bus' in line:
			continue
		if line == '':
			continue
		words = line.split(',')
		Bus = words[0].strip()
		mismatchMVA = float(words[3].strip())
		BusVolt  = float(BusDataDict[Bus].NominalVolt)
		if BusVolt < 40.0 and Bus in TFDataDict.keys():
			if mismatchMVA > 500:
				print Bus

