"""
Generate Bus and TF info of each line in the manual map
"""


ManualMapCS = 'Manual_Mapping0501.txt'
CAPERaw = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Help Bus Mapping/' + 'Raw0414tmp_loadsplit.raw'
planningRaw = 'hls18v1dyn_1219.raw'
BusTFInfoData = 'Manual_MappingBusTFInfo.txt'

CAPEComedBusSet = set()
planningComedBusSet = set()
CAPEBusVoltDict = {}
planningBusVoltDict = {}
CAPEBusNameDict = {}
planningBusNameDict = {}
CAPETFNameDict = {}
planningTFNameDict = {}
BusTFInfoLines = []

def getBusTFInfo(Raw,ComedBusSet,BusVoltDict,BusNameDict,TFNameDict):

	# get the relevant comed bus sets
	with open(Raw, 'r') as f:
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
			BusName = words[1].strip("'").strip()
			BusVolt = words[2].strip()
			#angle = float(words[8].strip())
			area = words[4].strip()
			#AreaDict[Bus] = area
			BusVoltDict[Bus] = BusVolt
			BusNameDict[Bus] = BusName
			if area == '222':
				ComedBusSet.add(Bus)
				
				




	tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
	tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')
	i = tfStartIndex
	# search tf data to populate LVTFDataDict
	while i < tfEndIndex:
		line = fileLines[i]
		words = line.split(',')
		Bus1 = words[0].strip()
		Bus2 = words[1].strip()
		cktID = words[3].strip("'").strip()
		status = words[11].strip()
		tfname = words[10].strip("'").strip()


		if Bus1 in ComedBusSet  or Bus2 in ComedBusSet:
			key = Bus1 + ',' + Bus2 + ',' + cktID
			TFNameDict[key] = tfname

		i+=4 # continue to next tf
#######################

getBusTFInfo(CAPERaw,CAPEComedBusSet,CAPEBusVoltDict,CAPEBusNameDict,CAPETFNameDict)
getBusTFInfo(planningRaw,planningComedBusSet,planningBusVoltDict,planningBusNameDict,planningTFNameDict)





# look at the manual maps done by the CS guys, and modified by me
with open(ManualMapCS,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:		
		if 'Format:' in line:
			continue
		if line == '':
			continue

		words = line.split('->')
		planningSide = words[0].strip()
		planningSideWords = planningSide.split(',')
		planningBus1 = planningSideWords[0].strip()
		planningBus2 = planningSideWords[1].strip()
		planningBus1Name = planningBusNameDict[planningBus1]
		planningBus1Volt = planningBusVoltDict[planningBus1]
		planningBus2Name = planningBusNameDict[planningBus2]
		planningBus2Volt = planningBusVoltDict[planningBus2]
		planningTFName = planningTFNameDict[planningSide]
		planningcktID  = planningSideWords[2].strip()
		planningSideString = planningBus1 + ',' + planningBus1Name + ',' + planningBus1Volt + ',' + planningBus2 + ',' + planningBus2Name + ',' + planningBus2Volt + ',' + planningcktID + ',' + planningTFName
		CAPESide = words[1].strip()
		if CAPESide == '': # mapping not provided
			string = planningSideString + '->'
		else:
			# eliminate any comments
			CAPESideWords = CAPESide.split(',')
			CAPESideShort = ''
			for i in range(3):
				CAPESideShort += CAPESideWords[i].strip()
				CAPESideShort += ','
			CAPESideShort = CAPESideShort[:-1]
			CAPESideWords = CAPESideShort.split(',')
			CAPEBus1 = CAPESideWords[0].strip()
			CAPEBus2 = CAPESideWords[1].strip()
			try:
				CAPEBus1Name = CAPEBusNameDict[CAPEBus1]
			except:
				CAPEBus1Name = 'Not Found'
			try:
				CAPEBus1Volt = CAPEBusVoltDict[CAPEBus1]
			except:
				CAPEBus1Volt = 'Not Found'				
			
			try:
				CAPEBus2Name = CAPEBusNameDict[CAPEBus2]
			except:
				CAPEBus2Name = 'Not Found'
			try:
				CAPEBus2Volt = CAPEBusVoltDict[CAPEBus2]
			except:
				CAPEBus2Volt = 'Not Found'
			
			CAPEcktID  = CAPESideWords[2].strip()
			try:
				CAPETFName = CAPETFNameDict[CAPESideShort]
			except:
				CAPETFName = 'Not Found'
			CAPESideString = CAPEBus1 + ',' + CAPEBus1Name + ',' + CAPEBus1Volt + ',' + CAPEBus2 + ',' + CAPEBus2Name + ',' + CAPEBus2Volt + ',' + CAPEcktID + ',' + CAPETFName
			string = planningSideString + '\t\t->\t\t' + CAPESideString
		
		BusTFInfoLines.append(string)


with open(BusTFInfoData,'w') as f:
	f.write('Format: Planning->CAPE')
	f.write('\n')
	f.write('Bus1,Bus1Name,Bus1Volt,Bus2,Bus2Name,Bus2Volt,TFCktID,TFName')
	f.write('\n')
	for line in BusTFInfoLines:
		f.write(line)
		f.write('\n')