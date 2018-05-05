"""
See if any load maps had different voltage levels (voltage differs by more than 5 kV)
"""

loadBusNoChangeLog = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/' +  'LoadBusNoChangeLog.txt'
CAPERaw = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/Island 34 system/' +  'Raw0414tmp.raw'
planningRaw = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/' +  'hls18v1dyn_1219.raw'

CAPEVoltDict = {}
planningVoltDict = {}

def getVoltDict(Raw,VoltDict):
	# dictionary which looks at raw file and generates a volt dict
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
			BusVolt = float(words[2].strip())
			#angle = float(words[8].strip())
			area = words[4].strip()
			#AreaDict[Bus] = area

			if area == '222':
				#BusAngleDict[Bus] = angle
				VoltDict[Bus] = BusVolt
#####



getVoltDict(CAPERaw,CAPEVoltDict)
getVoltDict(planningRaw,planningVoltDict)







with open(loadBusNoChangeLog,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')


	for line in fileLines:
		if 'CAPE' in line:
			continue
		if line == '':
			continue
		words = line.split('->')
		planningBus = words[0].strip()
		CAPEBus = words[1].strip()
		if abs(planningVoltDict[planningBus] - CAPEVoltDict[CAPEBus]) > 5.0:
			print planningBus + ',' + CAPEBus