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
		#invalidSubName = False
		if 'Substation' in line:
			continue

		subName = line[:42].strip() # these columns contain substation name
		BusNumber = line[42:48].strip() # these columns contain bus number
		BusToSubStationDictOld[BusNumber] = subName



		if subName not in SubStationDictOld.keys():
			SubStationDictOld[subName] = []

		SubStationDictOld[subName].append(BusNumber)


		if subName not in SubStationDictNew.keys():
			SubStationDictNew[subName] = []

		if BusNumber in changeOldToNewDict.keys():
			NewBusNumber = changeOldToNewDict[BusNumber]
			SubStationDictNew[subName].append(NewBusNumber)
			BusToSubStationDict[NewBusNumber] = subName
		else:
			SubStationDictNew[subName].append(BusNumber)
			BusToSubStationDict[BusNumber] = subName






if __name__ == "__main__":
	with open('tmpSubData.txt','w') as f:
		for key in SubStationDictNew.keys():
			string = key + '->' + str(SubStationDictNew[key])
			f.write(string)
			f.write('\n')

