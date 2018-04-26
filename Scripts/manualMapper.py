"""
function which can automate bus mapping, given the manual mappings in a file
can handle one to many mapping
"""


def MapChange(planningRaw,changeFile,CAPERaw,newRawFile,originalCase):
	# function to change bus mapping in raw file
	# originalCase: defines whether we are using planning or CAPE raw file to get bus info
	CAPENewVoltDict = {} # key: CAPEBus whose bus volt and angle will be substituted, value: new volt and angle data
	ManualMapDict = {} # key: the bus whose data is being used, value: the bus where we superimpose bus data
	currentBusSet = set()
	CAPEBusVoltSet = set() # set of all CAPE buses whose bus data will be substituted
	planningBusSet = set()
	newRawLines = []

	def reconstructLine2(words):
		currentLine = ''
		for word in words:
			currentLine += word
			currentLine += ','
		return currentLine[:-1]

	# open the file which contains the list of manual changes necessary
	with open(changeFile,'r') as f:
		filecontent = f.read()
		fileLines = filecontent.split('\n')

	# get the bus substitution data
	for i in range(len(fileLines)):
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
		if planningBus not in ManualMapDict.keys():
			ManualMapDict[planningBus] = [CAPEBus] 
		else:
			ManualMapDict[planningBus].append(CAPEBus)

		planningBusSet.add(planningBus)
		CAPEBusVoltSet.add(CAPEBus)


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
				Vmag = words[7]
				Vang = words[8]
				#if originalCase.strip() == 'planning':
				for bus in ManualMapDict[Bus]: # done this way so that one to many mappings can be handled
					#CAPEBus = ManualMapDict[Bus]
					#else:
					#	CAPEBus = Bus
					CAPENewVoltDict[bus] = [Vmag, Vang]



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
				words[7] = NewVoltageData[0] # pu volt substitution
				words[8] = NewVoltageData[1]
				newline = reconstructLine2(words)
				newRawLines.append(newline)
		

			else:
				newRawLines.append(line)

	# add these two bus lines, for some reason they were missing
	newRawLines.append("243083,'05CAMPSS    ', 138.0000,1, 205,1251,   1,1.01145, -55.0773")
	newRawLines.append("658082,'MPSSE  7    ', 115.0000,1, 652,1624, 658,1.02055, -45.2697")

	busEndIndex = fileLines.index('0 / END OF BUS DATA, BEGIN LOAD DATA')



	# append everything else
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



# only execute this block of code if we are running this file
# wont be executed if we are importing this module
if __name__ == "__main__":
	planningRaw = 'hls18v1dyn_new.raw'
	CAPERaw = 'Raw0419_reen.raw'
	newRawFile  = 'Raw0419_reen_manual.raw'
	changeFile = 'manual_tmp.txt'
	MapChange(planningRaw,changeFile,CAPERaw,newRawFile,'CAPE')