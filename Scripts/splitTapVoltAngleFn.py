"""
Script to split angles of taps (which dont exist in planning) according to the impedance ratios
Also splits voltages of taps according to the same ratio
Changed to a function called by manualMapper
"""

from generateNeighbourImpedanceData import getBranchTFData
from Queue import Queue

def splitTapVoltAngles(Raw,newRawFile,tapSplitLines):
	#Raw = 'RAW0509_tmp.raw'
	#newRawFile = 'RAW0509_tmp2.raw'
	angleChangeFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/' +  'logAngleChange.txt'
	BranchTFDataDict = getBranchTFData(Raw)
	ParentDict = {} # key: origin node, value: branch node
	explored = set()
	BusAngleDict = {}
	BusVoltDict = {}
	NewBusAngleDict ={}
	AngleChangeDict = {}
	NewBusVoltDict = {}
	newRawLines = []


	def reconstructLine2(words):
		currentLine = ''
		for word in words:
			currentLine += word
			currentLine += ','
		return currentLine[:-1]


	# use BranchTFDataDict and BFS Search Algorithm to get the angle splits for any taps in between two specified endpoints
	# use ParentDict concept to keep track
	#endpoints = [750354,1701] # 1st index is the starting point, 2nd index is the endpoint
	#tap_bus = '5079' # the tap bus



	#start = str(endpoints[0]) # chosen origin node
	#end = str(endpoints[1]) # chosen endpoint node


	for j in range(len(tapSplitLines)): # tapSpliList is a list of lists, each list has the following csv values: start, end, tap

		currentSplitLine = tapSplitLines[j].strip()
		splitWords = currentSplitLine.split(',')
		start = splitWords[0]
		end = splitWords[1]
		tap_bus = splitWords[2]
		# Read the angle change values and generate a dict
		with open(angleChangeFile,'r') as f:
			filecontent = f.read()
			fileLines = filecontent.split('\n')
			for line in fileLines:
				if 'Bus' in line:
					continue

				if line == '':
					continue

				words = line.split('->')
				Bus = words[0].strip()
				Angle = float(words[1].strip()) 

				if Angle == 0.0: # Add to dictionary only if there is a phase shift
					#print Bus
					continue	
				AngleChangeDict[Bus] = Angle



		# BFS algorithm to generate a parent dict from start to end
		frontier = Queue(maxsize=0)
		frontier.put(start)

		while not frontier.empty():
			currentBus =  frontier.get()
			frontier.task_done()
			NeighbourBus = BranchTFDataDict[currentBus].toBus
			if currentBus not in explored:
				explored.add(currentBus)

			if end in NeighbourBus:
				ParentDict[end] = currentBus
				break
			for neighbour in NeighbourBus:
				if neighbour not in explored:
					ParentDict[neighbour] = currentBus
					frontier.put(neighbour)

		traceback = [end] # list will contain the path from end to start
		child = end
		Parent = ''
		while Parent != start:
			Parent = ParentDict[child]
			traceback.append(Parent)
			child = Parent
		traceback.reverse() # reverse to get start to end

		# generate impedance values in the path
		ImpStart = 0.0 # total impedance in the path from start to tap bus
		ImpEnd = 0.0 # total impedance in the path from end to tap bu

		i = 0
		j = -1
		nextBus = ''
		while nextBus != tap_bus:
			currentBus = traceback[i]
			nextBus = traceback[i+1]
			ind = BranchTFDataDict[currentBus].toBus.index(nextBus)
			Z = BranchTFDataDict[currentBus].Z[ind]
			ImpStart += Z

			i+=1
		nextBus = ''
		while nextBus != tap_bus:
			currentBus = traceback[j]
			nextBus = traceback[j-1]
			ind = BranchTFDataDict[currentBus].toBus.index(nextBus)
			Z = BranchTFDataDict[currentBus].Z[ind]
			ImpEnd += Z
			j-=1

		ImpTotal = ImpStart + ImpEnd # get the total impedance

		# get the ratios
		RatioImpStart = ImpStart/ImpTotal
		RatioImpEnd = ImpEnd/ImpTotal



		# get the angle difference between start and end bus
		with open(Raw,'r') as f:
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
				area = words[4].strip()

				if area == '222':
					BusAngle = float(words[8].strip())
					BusVolt = float(words[7].strip())
					BusVoltDict[Bus] = BusVolt
					BusAngleDict[Bus] = BusAngle


		# get the new angles of the taps
		StartAngle = BusAngleDict[start]
		EndAngle = BusAngleDict[end]

		# incorporate any phase shifts due to tf
		if start in AngleChangeDict.keys():
			StartAngle -= AngleChangeDict[start]

		if end in AngleChangeDict.keys():
			EndAngle -= AngleChangeDict[end]

		angleDiff = EndAngle -StartAngle

		TapAngleOld = BusAngleDict[start]
		TapAngleNew = TapAngleOld + angleDiff*RatioImpStart

		NewBusAngleDict[tap_bus] = '%.4f' % TapAngleNew

		# get new voltage values
		StartVoltage = BusVoltDict[start]
		EndVoltage = BusVoltDict[end]

		VoltDiff = EndVoltage - StartVoltage

		TapVoltNew = StartVoltage + VoltDiff*RatioImpStart

		NewBusVoltDict[tap_bus] = '%.5f' %TapVoltNew

		#print NewBusVoltDict
		#print NewBusAngleDict
	############
	# generate the new raw file data
	with open(Raw,'r') as f:
		filecontent = f.read()
		fileLines = filecontent.split('\n')
		# reconstruct bus status
		for line in fileLines:
			if ('PSS' in line) or ('COMED' in line) or ('DYNAMICS' in line):
				continue
			if 'END OF BUS DATA' in line:
				break
			words = line.split(',')
			if len(words) <2:
				continue
			Bus = words[0].strip()

			# put in new voltage and angle data
			if Bus in NewBusAngleDict.keys():
				angle = NewBusAngleDict[Bus]
				volt = NewBusVoltDict[Bus]
				words[7] = ' '*(7-len(volt)) + volt
				words[8] = ' '*(9-len(angle)) + angle
				line = reconstructLine2(words)

			newRawLines.append(line)

	newRawLines.append("243083,'05CAMPSS    ', 138.0000,1, 205,1251,   1,1.01145, -55.0773")
	newRawLines.append("658082,'MPSSE  7    ', 115.0000,1, 652,1624, 658,1.02055, -45.2697")

	busEndIndex = fileLines.index('0 / END OF BUS DATA, BEGIN LOAD DATA')



	# append everything between end of bus and start of branch
	for i in range(busEndIndex,len(fileLines)):
		line = fileLines[i]
		newRawLines.append(line)

	# output the new raw data
	with open(newRawFile,'w') as f:
		f.write('0,   100.00, 33, 1, 1, 60.00     / PSS(R)E-33.3    TUE, DEC 13 2016  22:08')
		f.write('\n')
		f.write('COMED 2018,  HLS18V1, N18S OUTSIDE AND 18 INTCHNG')
		f.write('\n')
		f.write('DYNAMICS REVSION 01')
		f.write('\n')
		for line in newRawLines:
			f.write(line)
			f.write('\n')