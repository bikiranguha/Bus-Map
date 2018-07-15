# organize the 3 winder transformer changes. Generate a tmap file to be used by the 3 winder to 2 winder zero seq converter


import sys
sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2')
sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/Automate 345 kV mapping')

from getBusDataType4IncludedFn import getBusData # create a dictionary which organizes all bus data
from getTFDataFn import getTFData # get tf data
CAPERaw = 'RAW0620.raw' # most updated merged raw file, with all verified mappings applied
ZeroSeqFile = 'CAPENewSeq.seq'
changeLog = 'changeBusNoLog.txt'
CAPEBusDataDict = getBusData(CAPERaw)
TFDataDict = getTFData(CAPERaw)
changeOldToNewDict = {}
tMapDict = {}
winder3Set = set()
CAPEMidPtDict = {}
keySet = set()
latestMapFile = 'latestMapFile.txt'
manualtMapFile = 'tmap_manual.txt'
tMapDictManual = {} # dict of all the manual maps
# construct a dictionary of all comed midpoints, with the midpoint as the key and the tf connection set as value



with open(manualtMapFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if '->' not in line:
			continue
		words = line.split('->')
		tfID = words[0].strip()
		mid = words[1].strip()
		tMapDictManual[tfID] = mid


#print tMapDictManual

# get midpoint dict, to find tmaps
for Bus in CAPEBusDataDict.keys():
	if CAPEBusDataDict[Bus].area != '222':
		continue

	BusName = CAPEBusDataDict[Bus].name

	if Bus in TFDataDict.keys():
		if BusName.startswith('T3W') or BusName.endswith('M'):
			CAPEMidPtDict[Bus] = set()
			toBuses = TFDataDict[Bus].toBus
			#midPtSet = set()
			for n in toBuses:
				CAPEMidPtDict[Bus].add(n)
				#midPtSet.add(n)
			#CAPEMidPtDict[midPtSet] = Bus




with open(changeLog,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'CAPE' in line:
			continue

		words = line.split('->')

		if len(words) < 2:
			continue

		OldBus = words[0].strip()
		NewBus = words[1].strip()
		changeOldToNewDict[OldBus] = NewBus



with open(ZeroSeqFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')


tfStartIndex = fileLines.index("0/ End of Zero Sequence Mutual Impedance Data; Begin Zero Sequence Transformer Data") + 1
tfEndIndex = fileLines.index("0/ End of Zero-Sequence Transformer data; Begin Area Data")
print 'Multiple transformer connections, need ckt id info for the following set:'
for i in range(tfStartIndex, tfEndIndex):
	line = fileLines[i]
	#words = line.split(',')
	Bus1 = line[:6]
	Bus2 = line[7:13]
	Bus3 = line[14:20]
	cktID = line[21:25]

	RestOfLine = line[20:]


	if Bus1.strip() in changeOldToNewDict.keys():
		Bus1 = changeOldToNewDict[Bus1.strip()]
		Bus1 = ' '*(6-len(Bus1)) + Bus1

	if Bus2.strip() in changeOldToNewDict.keys():
		Bus2 = changeOldToNewDict[Bus2.strip()]
		Bus2 = ' '*(6-len(Bus2)) + Bus2

	if Bus3.strip() in changeOldToNewDict.keys():
		Bus3 = changeOldToNewDict[Bus3.strip()]
		Bus3 = ' '*(6-len(Bus3)) + Bus3

	# ignore 2 winders
	if Bus3.strip() == '0':
		continue

	#winder3 = Bus1.strip() + ',' + 	Bus2.strip() + ',' + Bus3.strip()
	#winder3Set.add(winder3)

	#if Bus1.strip() in CAPEBusDataDict.keys() and Bus2.strip() in CAPEBusDataDict.keys() and Bus3.strip() in CAPEBusDataDict.keys():
	try:
		Bus1Name = CAPEBusDataDict[Bus1.strip()].name
		Bus2Name = CAPEBusDataDict[Bus2.strip()].name
		Bus3Name = CAPEBusDataDict[Bus3.strip()].name
	except: # Buses outside comed, not necessary
		key = Bus1.strip() + ',' + 	Bus2.strip() + ',' + Bus3.strip() + ',' + cktID
		#print key
		continue

	if 'T3W' in Bus1Name or 'T3W' in Bus2Name or 'T3W' in Bus3Name:
		continue

	# if multiple tf exist between these three, print it here
	key = Bus1.strip() + ',' + 	Bus2.strip() + ',' + Bus3.strip() + ',' + cktID
	if key not in keySet:
		keySet.add(key)
	else:
		print key


	current3winderSet = set()
	current3winderSet.add(Bus1.strip())
	current3winderSet.add(Bus2.strip())
	current3winderSet.add(Bus3.strip())
	tMapDict[key] = ''
	for midpt in CAPEMidPtDict.keys():
		m  = CAPEMidPtDict[midpt]
		if m == current3winderSet:
			tMapDict[key] = midpt
			break


"""
# could not find the midpoints automatically, found them manually
for key in tMapDict.keys():
	val = tMapDict[key]
	if val == '':
		print key


"""
with open(latestMapFile,'w') as f:
	f.write('Auto tMaps:')
	f.write('\n')

	for key in tMapDict.keys():
		val = tMapDict[key]
		if val == '':
			continue

		string = key + ',' + val
		f.write(string)
		f.write('\n')

	# Add manual maps	
	f.write('Manually added tMaps:')
	f.write('\n')

	for key in tMapDictManual.keys():
		val = tMapDictManual[key]
		if val == '':
			continue


		string = key + ',' + val
		f.write(string)
		f.write('\n')


# Now read the latestMapFile in convert3wto2w0seqv3.py to get the new zero seq file with all the 3 winders converted to 2 winders. If the three winder does not appear in the dict, skip it 