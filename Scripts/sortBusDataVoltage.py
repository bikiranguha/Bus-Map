# Sort Bus Data according to their voltage


#Busdata = 'AllMappedBusDataOld.txt'
#BusdataSorted = 'AllMappedBusDataSorted.txt'


def sortBusData(BusData, BusdataSorted):
	# function which takes in BusData file and outputs BusdataSorted file, where all the buses are sorted in descending order 
	# of voltage

	VoltSet = set() # set of all voltage levels
	BusLinesSorted = []


	with open(BusData,'r') as f:
		filecontent = f.read()
		fileLines = filecontent.split('\n')


	# get a set of all bus voltage levels
	for line in fileLines:
		words = line.split(',')
		if len(words) <3: # should continue to next line if no csv data present, such as for headers
			continue

		try: # in case the line is not a bus data line
			Busvoltage = float(words[2].strip())
		except: # not bus data line
			print 'Following lines do not contain bus voltage data: ', line
			continue
		
		VoltSet.add(Busvoltage)


	# change to a list with descending order of voltage
	VoltDescending = sorted(list(VoltSet),reverse = True) # sort in descending order



	# rearrange data
	for currentVolt in VoltDescending: # outer loop: add buses according to voltage, descending order
		for line in fileLines: # scan each line
			words = line.split(',')
			if len(words) <2:
				continue

			Busvoltage = float(words[2].strip())
			if Busvoltage == currentVolt:
				BusLinesSorted.append(line)



	with open(BusdataSorted,'w') as f:
		for line in BusLinesSorted:
			f.write(line)
			f.write('\n')