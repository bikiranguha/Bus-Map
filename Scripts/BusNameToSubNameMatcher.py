"""
Name matcher: Planning Bus Name to CAPE substation names
Names are listed according to match in descending order
"""

from difflib import SequenceMatcher
from string import punctuation

special_symbols = set(punctuation)

planningRaw = 'hls18v1dyn_new.raw'
similarityThreshold = 0.5
NameMatchSorted = 'NameMatchResultsSorted' + str(int(similarityThreshold*100)) +  '.txt' # sorted according to similarity in descending order

latestRawCAPE = 'RAW0501.raw'
BusLines345CAPE = 'BusLines345CAPE.txt'
BusLines345Planning = 'BusLines345Planning.txt'
SubStationDict = {} # key: substation name, value: list of all buses belonging to the substation
lines345CAPE = []
lines345Planning = []
subNameSet = set()
substationFile = 'Substation_Report.TXT'
NameMatchDictPlanning = {}
NameMatchDictCAPE = {}


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def getCompactString(s):
	compSList = [x for x in s if not (x == ' ' or x in special_symbols)]
	compS = ''
	for ele in compSList:
		compS += ele
	return compS



def get345BusData(Raw,lines345, BusLinesFile, NameMatchDict):

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
			area = words[4].strip()
			BusType = words[3].strip()
			name = words[1].strip("'")
			if area == '222':
				#BusAngleDict[Bus] = angle
				#ComedBusSet.add(Bus)
				BusVolt = float(words[2].strip())
				if BusVolt >= 345.0 and not name.startswith('T3W'):
					lines345.append(line)
					NameMatchDict[name] = []


	with open(BusLinesFile,'w') as f:
		f.write('345 Bus Data:')
		f.write('\n')
		for line in lines345:
			f.write(line)
			f.write('\n')

get345BusData(latestRawCAPE,lines345CAPE,BusLines345CAPE, NameMatchDictCAPE)
get345BusData(planningRaw,lines345Planning,BusLines345Planning, NameMatchDictPlanning)


# get substation data for the buses
notSubNames = ['Unassigned','LINE BUS', 'Generic tap Busses', 'Invalid Substation', 'Tap Busses']


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

    		if subName not in SubStationDict.keys():
    			SubStationDict[subName] = []

    		SubStationDict[subName].append(BusNumber)
    		#print subName

"""
with open('subList.txt','w') as f:
	for name in list(subNameSet):
		f.write(name)
		f.write('\n')
"""

for planningBusName in NameMatchDictPlanning.keys():
	similarityDict = {}
	for CAPEsubName in list(subNameSet):
		planningBusNameCompact = getCompactString(planningBusName)
		CAPEsubNameCompact = getCompactString(CAPEsubName)
		similarity =  SequenceMatcher(None,planningBusNameCompact, CAPEsubNameCompact).ratio()
		if similarity > similarityThreshold:
			similarityDict[CAPEsubName] = similarity
		

	similarityDictSorted = sorted(similarityDict, key=similarityDict.get, reverse=True) # gets the dictionary keys in descending order of the values
		
	NameMatchDictPlanning[planningBusName] = similarityDictSorted


# output the sorted name match list
with open(NameMatchSorted,'w') as f:
	for planningBusName in NameMatchDictPlanning.keys():
		string = planningBusName + ' -> '
		for CAPEsubName in NameMatchDictPlanning[planningBusName]:
			string += str(CAPEsubName)
			string += ','
		string = string[:-1]
		f.write(string)
		f.write('\n')
