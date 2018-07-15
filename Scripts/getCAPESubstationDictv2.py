"""
Script to generate CAPE substation dictionaries where the key are the substation names and the values are list of buses belonging to that substation
"""

substationFile = 'Substation_Report.TXT'
changeLog = 'changeBusNoLog.txt'
# get substation data for the buses
notSubNames = ['Unassigned','LINE BUS', 'Generic tap Busses', 'Invalid Substation', 'Tap Busses']
subNameSet = set()
SubStationDictOld = {} # key: substation name, value: list of all buses belonging to the substation
SubStationDictNew = {}
changeOldToNewDict = {}
BusToSubStationDict = {} # key: New bus numbers, value: Substation name
BusToSubStationDictOld = {} # key: Old bus numbers, value: Substation name

def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False


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


with open(substationFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		invalidSubName = False
		ifHeader = line.find('Substation')

		if ifHeader != -1:
			continue

		"""
		for name in notSubNames:
			if name in line:
				invalidSubName = True
				break

		if invalidSubName == True:
			continue
		"""
		words = line.split(" ")
		lessWords = []
		for word in words:
			if word != '':
				lessWords.append(word)

		subName = ''

		for word in lessWords:
			if is_number(word): # string is a number
				if word == lessWords[1]:# string is the 2nd element, likely part of the subName
					subName += word
					subName += ' '
				else:
					BusNumber = word
					break
			else: # string is not a number, likely subName
				subName += word
				subName += ' '

		subName = subName[:-1]
		#print BusNumber
		if subName != '':
			subNameSet.add(subName)

		if subName not in SubStationDictOld.keys():
			SubStationDictOld[subName] = []

		SubStationDictOld[subName].append(BusNumber)
		BusToSubStationDictOld[BusNumber] = subName
		if subName not in SubStationDictNew.keys():
			SubStationDictNew[subName] = []

		if BusNumber in changeOldToNewDict.keys():
			NewBusNumber = changeOldToNewDict[BusNumber]
			SubStationDictNew[subName].append(NewBusNumber)
			BusToSubStationDict[NewBusNumber] = subName
		else:
			SubStationDictNew[subName].append(BusNumber)
			BusToSubStationDict[BusNumber] = subName


		# Bus to Substation Dict





if __name__ == "__main__":
	with open('tmpSubData.txt','w') as f:
		for key in SubStationDictNew.keys():
			string = key + '->' + str(SubStationDictNew[key])
			f.write(string)
			f.write('\n')

