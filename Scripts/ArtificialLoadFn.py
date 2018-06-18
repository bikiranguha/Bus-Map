# Get input CAPE from bus and to bus, get corresponding maps and generate artificial load at to bus


def artificialLoad(fromBus, toBus, MapDict, planningFlowReport):

	def reconstructLine2(words):
		currentLine = ''
		for word in words:
			currentLine += word
			currentLine += ','
		return currentLine[:-1]


	# get planning from and to bus
	planningFromBus = MapDict[fromBus]
	planningToBus = MapDict[toBus]

	# get the MW and MVAR flows
	try:
		toBusIndex = planningFlowReport[planningFromBus].toBus.index(planningToBus)
	except:
		'In planning, there is no connection between the  mapped buses of the pair ' + fromBus + ',' + toBus + '. Please check this mapping.'
	toBusMW = planningFlowReport[planningFromBus].MWList[toBusIndex]
	toBusMVAR = planningFlowReport[planningFromBus].MVARList[toBusIndex]
	toBusMW = '%.3f' % toBusMW
	toBusMVAR = '%.3f' % toBusMVAR

	sampleLoadStr = "  4355,'1 ',1, 222,  20,     1.400,     0.600,     0.000,     0.000,     0.000,     0.000, 222,1,0"
	# change load data
	words = sampleLoadStr.split(',')
	words[0] = ' '*(6-len(toBus)) + toBus.strip() # change the bus info
	words[5] = ' '*(10-len(toBusMW)) + toBusMW # new load MW
	words[6] = ' '*(10-len(toBusMVAR)) + toBusMVAR # new load MVAR
	newLoadLine  = reconstructLine2(words)
	return newLoadLine



if __name__ == '__main__':
	from analyzeBusReportFn import BusFlowData
	planningFlowReport = 'BusReports_Planning.txt'
	planningRaw = 'hls18v1dyn_1219.raw'
	planningFlowData = BusFlowData(planningFlowReport,planningRaw)
	MapDict = {}

	MapFile = 'blue2red345.txt' # CAPE to planning updated bus map

	# get Mapping info
	with open(MapFile,'r') as f:
		filecontent = f.read()
		fileLines = filecontent.split('\n')
		for line in fileLines:
			if line == '':
				continue
			words = line.split('->')
			CAPEBus = words[0].strip()
			try:
				PlanningBus = words[2].strip()
			except:
				continue
			MapDict[CAPEBus] = PlanningBus

	fromBus = '750139'
	toBus = '750033'

	artificialLoad(fromBus, toBus, MapDict, planningFlowData)



