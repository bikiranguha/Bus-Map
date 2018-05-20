"""
Generate SubStationDict whose key is the CAPE substation name and value are all the CAPE buses belonging to the substation
"""

substationFile = 'Substation_Report.TXT'
changeLog = 'changeBusNoLog.txt'
# get substation data for the buses
notSubNames = ['Unassigned','LINE BUS', 'Generic tap Busses', 'Invalid Substation', 'Tap Busses']
subNameSet = set()
SubStationDictOld = {} # key: substation name, value: list of all buses belonging to the substation
SubStationDictNew = {}
changeOldToNewDict = {}

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
        changeOldToNewDict[NewBus] = OldBus


with open(substationFile,'r') as f:
	    filecontent = f.read()
	    fileLines = filecontent.split("\n")
	    for line in fileLines:
	    	invalidSubName = False
    		ifHeader = line.find('Substation')
    		if ifHeader != -1:
    			continue

    		for name in notSubNames:
    			if name in line:
    				invalidSubName = True
    				break

    		if invalidSubName == True:
    			continue
    		words = line.split(" ")
    		lessWords = []
    		for word in words:
    			if word !='':
    				lessWords.append(word)
    		subName = ''
    		#print lessWords
    		for word in lessWords:
    			#while not (is_number(word) and word != lessWords[1]) :
    			if is_number(word): # string is a number
    				if word == lessWords[1]: # string is the 2nd element, likely part of the subName
    					subName += word
    					subName += ' '
    				else: # string is likely the bus number
    					BusNumber = word
    					break
    			else: # string not a number, likely subName
    				subName += word
    				subName += ' '
    		
    		subName = subName[:-1]
    		if subName != '':
    			subNameSet.add(subName)

    		if subName not in SubStationDictOld.keys():
    			SubStationDictOld[subName] = []
                SubStationDictNew[subName] = []

    		SubStationDictOld[subName].append(BusNumber)

            if BusNumber in changeOldToNewDict.keys():
                NewBusNumber = changeOldToNewDict[BusNumber]
                SubStationDictNew[subName].append(NewBusNumber)
            else:
                SubStationDictNew[subName].append(BusNumber)
    		#print subName