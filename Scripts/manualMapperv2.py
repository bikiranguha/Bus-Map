"""
function which can automate bus mapping, given the manual mappings in a file
can handle one to many mapping
"""
import sys
sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2')
def MapChange(planningRaw,changeFile,CAPERaw,newRawFile,originalCase):
	# function to change bus mapping in raw file
	# originalCase: defines whether we are using planning or CAPE raw file to get bus info
	angleChangeFile = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/' +  'logAngleChange.txt'
	mapping_priority1 = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/' + 'mapping_priority1.txt'
	from splitTapVoltAngleFn import splitTapVoltAngles # function which reads tap split data, performs the tap splits and generates the new raw file
	from tfMapFnv2 import doTFMaps # only do tf mapping, bus data is not changed
	from getBusDataFn import getBusData 
	planningBusDataDict = getBusData(planningRaw)
	CAPENewVoltDict = {} # key: CAPEBus whose bus volt and angle will be substituted, value: new volt and angle data
	ManualMapDict = {} # key: the bus whose data is being used, value: the bus where we superimpose bus data
	currentBusSet = set()
	CAPEBusVoltSet = set() # set of all CAPE buses whose bus data will be substituted
	planningBusSet = set()
	newRawLines = []
	AngleChangeDict = {} # dictionary of bus angle changes due to phase shift
	BranchImpedanceDictPlanning = {}
	BranchImpedanceDictCAPE = {}
	tapSplitLines = [] # lines containing tap split info
	ManualMapDictCAPE = {} # keys are CAPE buses according to new numbering system, values are planning buses
	newMapLines = []
	mappedLinesSet = set() # set to prevent any duplicate mappings
	tfMapLines = [] # map the tf data


	def makeBranchImpedanceDict(Raw):
		# generates a branch impedance dict from the given raw file
		# key: Bus1 + ',' + Bus2 + ',' + cktID, value = [R,X] where R and X are both strings
		with open(Raw, 'r') as f:
			BranchImpedanceDict = {}
			filecontent = f.read()
			fileLines = filecontent.split('\n')
			branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA') + 1
			branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')

			for i in range(branchStartIndex, branchEndIndex):
				line = fileLines[i]
				words = line.split(',')
				Bus1 = words[0].strip()
				Bus2 = words[1].strip()	
				cktID = words[2].strip("'").strip()
				key = Bus1 + ',' + Bus2 + ',' + cktID
				R = words[3]
				X = words[4]
				BranchImpedanceDict[key] = [R,X]	
		return BranchImpedanceDict


	#####################



	def reconstructLine2(words):
		currentLine = ''
		for word in words:
			currentLine += word
			currentLine += ','
		return currentLine[:-1]

	########
	
	BranchImpedanceDictPlanning = makeBranchImpedanceDict(planningRaw) # generate the impedance dict for planning



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


	# open the file which contains the list of manual changes necessary
	with open(changeFile,'r') as f:
		filecontent = f.read()
		fileLines = filecontent.split('\n')

		branchImpedanceChangeStart = fileLines.index("List of branch impedance changes:") + 1
		tfMapStart = fileLines.index("List of transformer (and corresponding bus maps):") + 1
		tapSplitStart = fileLines.index("List of split tap angles (start, end, tap):") + 1
		tapSplitEnd = fileLines.index("Other miscellaneous manual changes:")
	# get the bus substitution data
	for i in range(branchImpedanceChangeStart):
		line = fileLines[i]
		if line == '':
			continue
		if '->' not in line:
			continue
		words = line.split('->')
		if len(words) <2:
			continue
		planningBus = words[0].strip()
		CAPEBus = words[1].strip()
		# generate mapping info, can handle one to many mappings
		ManualMapDictCAPE[CAPEBus] = planningBus
		if planningBus not in ManualMapDict.keys():
			ManualMapDict[planningBus] = [CAPEBus] 
		else:
			ManualMapDict[planningBus].append(CAPEBus)

		planningBusSet.add(planningBus)
		CAPEBusVoltSet.add(CAPEBus)

	# get the branch substitution data
	for i in range(branchImpedanceChangeStart,tfMapStart):
		line = fileLines[i]
		if line == '':
			continue
		if '->' not in line:
			continue
		words = line.split('->')
		if len(words) <2:
			continue	
		planningPart = words[0].strip()
		CAPEPart = words[1].strip()
		BranchImpedanceDictCAPE[CAPEPart] =  BranchImpedanceDictPlanning[planningPart]

	# get the tf map data
	for i in range(tfMapStart,tapSplitStart):
		line = fileLines[i].strip()
		tfMapLines.append(line)

	# get tap split data
	for i in range(tapSplitStart,tapSplitEnd):
		line = fileLines[i]
		if line == '':
			continue

		words = line.split(',')
		if len(words) < 3:
			continue
		tapSplitLines.append(line.strip())




	# determine which raw file to use for bus info
	if originalCase.strip() == 'CAPE':
		originalRaw = CAPERaw
	elif originalCase.strip() == 'planning':
		originalRaw = planningRaw
	else:
		print 'Please select proper originalCase argument'


	# get the bus data to be substituted
	with open(originalRaw,'r') as f:
		filecontent = f.read()
		fileLines = filecontent.split("\n")
		for line in fileLines:
			if ('PSS' in line) or ('COMED' in line) or ('DYNAMICS' in line):
				continue
			if 'END OF BUS DATA' in line:
				break
			words = line.split(',')
			if len(words)<2: # continue to next iteration of loop if its a blank line
				continue

			Bus = words[0].strip()

				
			if Bus in planningBusSet:
				BusName = planningBusDataDict[Bus].name 
				if BusName.startswith('T3W') or BusName.endswith('M'):
					NominalVolt = 0
				else:
					NominalVolt = words[2]
					
				Vmag = words[7]
				Vang = words[8]
				#if originalCase.strip() == 'planning':
				for bus in ManualMapDict[Bus]: # done this way so that one to many mappings can be handled
					#CAPEBus = ManualMapDict[Bus]
					#else:
					#	CAPEBus = Bus
					CAPENewVoltDict[bus] = [NominalVolt,Vmag, Vang]



	# generate the new raw file data
	with open(CAPERaw,'r') as f:
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

			if Bus in currentBusSet: 
				# in CAPERaw, there are several buses which appear twice. This gets rid of that problem
				continue
			else:
				currentBusSet.add(Bus)

			if Bus in CAPEBusVoltSet:
				NewVoltageData = CAPENewVoltDict[Bus]
				if NewVoltageData[0] != 0: # only change nominal voltage when the planning bus was not a midpoint
					words[2] = NewVoltageData[0] # change the nominal voltage

				words[7] = NewVoltageData[1] # pu volt substitution

				# Apply any phase shifts
				if Bus in AngleChangeDict.keys():
					PS = AngleChangeDict[Bus]
					OldAngle = float(NewVoltageData[2].strip())
					NewAngle = OldAngle + PS
					NewAngleStr  = '%.4f' %NewAngle
					NewAngleStr = ' '*(9-len(NewAngleStr)) + NewAngleStr
					words[8] = NewAngleStr
				else:
					words[8] = NewVoltageData[2] # angle substitution

				# reconstruct line and add
				newline = reconstructLine2(words)
				newRawLines.append(newline)
		

			else:
				newRawLines.append(line)

	# add these two bus lines, for some reason they were missing
	newRawLines.append("243083,'05CAMPSS    ', 138.0000,1, 205,1251,   1,1.01145, -55.0773")
	newRawLines.append("658082,'MPSSE  7    ', 115.0000,1, 652,1624, 658,1.02055, -45.2697")

	busEndIndex = fileLines.index('0 / END OF BUS DATA, BEGIN LOAD DATA')
	branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA') + 1
	branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')


	# append everything between end of bus and start of branch
	for i in range(busEndIndex,branchStartIndex):
		line = fileLines[i]
		newRawLines.append(line)

	# change any branch data
	for i in range(branchStartIndex,branchEndIndex):
		line = fileLines[i]
		words = line.split(',')
		Bus1 = words[0].strip()
		Bus2 = words[1].strip()	
		cktID = words[2].strip("'").strip()
		key = Bus1 + ',' + Bus2 + ',' + cktID		
		# change branch data if instructed to
		if key in BranchImpedanceDictCAPE.keys():
			print key
			R = BranchImpedanceDictCAPE[key][0]
			X = BranchImpedanceDictCAPE[key][1]
			words[3] = R
			words[4] = X
			line = reconstructLine2(words)

		newRawLines.append(line)


	# append everything else
	for i in range(branchEndIndex,len(fileLines)):
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

	
	CAPEBusDataDict = getBusData(newRawFile)
	ManualMapDictCAPE =  doTFMaps(tfMapLines,newRawFile,newRawFile,planningBusDataDict,CAPEBusDataDict,ManualMapDictCAPE) # do tf mapping on the new raw file, should be done before any angle splitting
	splitTapVoltAngles(newRawFile,newRawFile,tapSplitLines) # split angles only after the bus mapping has been completed, and use the latest raw file


	# get the previous manual mappings
	with open(mapping_priority1,'r') as f:
		filecontent = f.read()
		fileLines = filecontent.split('\n')
		for line in fileLines:
			if line == '':
				continue
			if line in mappedLinesSet: # prevent the same mapping appearing multiple times
				continue
			if '->' not in line: # skip header
				continue
			words = line.split('->')
			LHSBus = words[0].strip() # planning bus
			RHSBus  = words[1].strip() # CAPE bus (new numbering system)
			# check for mapping conflicts
			if RHSBus in ManualMapDictCAPE.keys():
				if LHSBus != ManualMapDictCAPE[RHSBus]:
					print RHSBus + ' has two different manual maps.'


			newMapLines.append(line)
			mappedLinesSet.add(line)


		# append the new manual maps
		with open(mapping_priority1,'w') as f:
			f.write('Highest priority maps (This file should be consulted first before any other for mapping purposes):')
			f.write('\n')
			for line in newMapLines:
				f.write(line)
				f.write('\n')
			for CAPEBus in ManualMapDictCAPE.keys():
				string = ManualMapDictCAPE[CAPEBus] + '->' + CAPEBus
				if string not in mappedLinesSet:
					f.write(string)
					f.write('\n')
					mappedLinesSet.add(string)


# only execute this block of code if we are running this file
# wont be executed if we are importing this module

if __name__ == "__main__":
	planningRaw = 'hls18v1dyn_1219.raw'
	CAPERaw = 'RAW0602.raw'
	newRawFile  = 'RAW00604_11003.raw'
	changeFile = 'mapping_confirmed_11003.txt'
	MapChange(planningRaw,changeFile,CAPERaw,newRawFile,'planning')

