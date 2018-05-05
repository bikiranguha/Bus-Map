"""
Generate Bus and TF info of each line in the manual map
"""


ManualMapCS = 'Manual_Mapping0501.txt'
correctedManualMapLines = 'Manual_Mapping0501GenIssueFixed.txt'
#CAPERaw = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Help Bus Mapping/' + 'Raw0414tmp_loadsplit.raw'
planningRaw = 'hls18v1dyn_1219.raw'
#BusTFInfoData = 'Manual_MappingBusTFInfo.txt'

#CAPEComedBusSet = set()
#planningComedBusSet = set()
BusVoltDict = {}
BusTypeDict = {}
#planningBusVoltDict = {}
newMapLines = []

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
			#BusName = words[1].strip("'").strip()
			BusVolt = float(words[2].strip())
			BusType = words[3].strip()
			#angle = float(words[8].strip())
			#area = words[4].strip()
			#AreaDict[Bus] = area
			BusVoltDict[Bus] = BusVolt
			#BusNameDict[Bus] = BusName
			BusTypeDict[Bus] = BusType


# look at the manual maps done by the CS guys, and modified by me
with open(ManualMapCS,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:		
		if 'Format:' in line:
			newMapLines.append(line)
			continue
		if line == '':
			continue

		words = line.split('->')
		planningSide = words[0].strip()
		planningSideWords = planningSide.split(',')
		planningBus1 = planningSideWords[0].strip()
		planningBus2 = planningSideWords[1].strip()

		if BusVoltDict[planningBus1] < 40.0 and BusVoltDict[planningBus2] > 40.0:
			LVBus = planningBus1
		elif BusVoltDict[planningBus2] < 40.0 and BusVoltDict[planningBus1] > 40.0:
			LVBus = planningBus2

		if BusTypeDict[LVBus] == '2':
			print line
			continue

		else:
			newMapLines.append(line)




with open(correctedManualMapLines,'w') as f:
	for line in newMapLines:
		f.write(line)
		f.write('\n')