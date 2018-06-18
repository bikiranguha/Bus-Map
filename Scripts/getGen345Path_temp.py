import sys
sys.path.insert(0,'C:/Users/Hemanth/OneDrive/Donut Hole v2')


from findPathTo345Fn import generate345PathList
from getBusDataFn import getBusData


GenMapVeriFied ='C:/Users/Hemanth/OneDrive/Donut Hole v2/' +  'PSSEGenMapVerified.txt'
CAPERaw = 'Raw0606.raw'
GenList = []
InserviceGen=[]
OutofserviceGen=[]


CAPEBusDataDict = getBusData(CAPERaw)
with open(CAPERaw, 'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	GenStartIndex = fileLines.index('0 / END OF FIXED SHUNT DATA, BEGIN GENERATOR DATA') + 1
	GenEndIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA')

	fileLines=fileLines[GenStartIndex:GenEndIndex]

	for line in fileLines:
		words=line.split(',')
		genbus=words[0].strip()
		status=words[14].strip()
		genbusarea=CAPEBusDataDict[genbus].area

		if genbusarea=='222':
			if status=='1':
				InserviceGen.append(genbus)
			elif status=='0':
				OutofserviceGen.append(genbus)
#---------------------------------------------------------------------------------------------------------------------------------

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




"""
for knowing genertaors with same nodes
for key in InserviceGen:
	if key in InserviceGen2:
		InserviceGen2.remove(key)
	elif key not in InserviceGen2:
		print key
"""
"""
Total generation units:         143
Out of service generator units:  19
In service generator units    : 124
In service generator nodes    : 117
Two generator nodes at same node: 7
same node generators: 274674,274675,274676,274686,274687,274836,274837
special focus: 274686(5361 and 5362 needed to be added)
"""
with open('GenPathList_Inservice.txt','w') as f:
	f.write('Start Bus: Path to 345')
	f.write('\n')
	InserviceGen=list(set(InserviceGen))
	for key in InserviceGen:
		string = PathDict[key]
		f.write(string)
		f.write('\n')

with open('GenPathList_OutOfservice.txt','w') as f:
	f.write('Start Bus: Path to 345')
	f.write('\n')
	for key in OutofserviceGen:
		string = PathDict[key]
		f.write(string)
		f.write('\n')
#-------------------------------------------------------------------------------------------------------------------------------------

