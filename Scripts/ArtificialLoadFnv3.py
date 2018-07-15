# Get input CAPE from bus and to bus, get corresponding maps and generate artificial load at from bus


def artificialLoad(fromBus, planningFromBus, planningToBus,  planningFlowReport):

	def reconstructLine2(words):
		currentLine = ''
		for word in words:
			currentLine += word
			currentLine += ','
		return currentLine[:-1]




	# get the MW and MVAR flows
	try:
		toBusIndex = planningFlowReport[planningFromBus].toBus.index(planningToBus)
	except:
		print 'In planning, there is no connection between the pair ' + planningFromBus + ',' + planningToBus + '. Please check this input.'
		return
	toBusMW = planningFlowReport[planningFromBus].MWList[toBusIndex]
	toBusMVAR = planningFlowReport[planningFromBus].MVARList[toBusIndex]
	toBusMW = '%.3f' % toBusMW
	toBusMVAR = '%.3f' % toBusMVAR

	sampleLoadStr = "  4355,'1 ',1, 222,  20,     1.400,     0.600,     0.000,     0.000,     0.000,     0.000, 222,1,0"
	# change load data
	words = sampleLoadStr.split(',')
	words[0] = ' '*(6-len(fromBus)) + fromBus.strip() # change the bus info
	words[5] = ' '*(10-len(toBusMW)) + toBusMW # new load MW
	words[6] = ' '*(10-len(toBusMVAR)) + toBusMVAR # new load MVAR
	newLoadLine  = reconstructLine2(words)
	return newLoadLine



if __name__ == '__main__':
	from analyzeBusReportFn import BusFlowData
	planningFlowReport = 'BusReports_Planning.txt'
	planningRaw = 'hls18v1dyn_1219.raw'
	planningFlowData = BusFlowData(planningFlowReport,planningRaw)

	toBus = '3286'
	planningFromBus = '272273'
	planningToBus = '272035'

	print artificialLoad(toBus, planningFromBus, planningToBus, planningFlowData)



