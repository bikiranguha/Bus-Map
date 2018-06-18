from findPathTo345Fn import generate345PathList

GenMapVeriFied ='C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/' +  'PSSEGenMapVerified.txt'
CAPERaw = 'Raw0602.raw'
GenList = []
with open(GenMapVeriFied,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'Manual' in line:
			continue
		words = line.split(',')
		if len(words) < 2:
			continue
		planningBus = words[0].strip()
		GenList.append(planningBus)

PathDict = generate345PathList(CAPERaw,GenList)


with open('GenPathList.txt','w') as f:
	f.write('Start Bus: Path to 345')
	f.write('\n')
	for key in PathDict.keys():
		string = PathDict[key]
		f.write(string)
		f.write('\n')