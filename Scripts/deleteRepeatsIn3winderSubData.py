ThreeWToThreeWSubFile = 'All3wTo3wSubData.txt'
cleanSubSet = set()

with open(ThreeWToThreeWSubFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if '->' not in line:
			continue
		words = line.split('->')
		CAPEPart = words[0].strip()
		planningPart = words[1].strip()
		CAPEBuses = CAPEPart.split(',')
		planningBuses = planningPart.split(',')
		Bus1 = CAPEBuses[0]
		Bus2 = CAPEBuses[1]
		Bus3 = CAPEBuses[2]
		cktID = CAPEBuses[3]

		planningBus1 = planningBuses[0]
		planningBus2 = planningBuses[1]
		planningBus3 = planningBuses[2]
		planningcktID = planningBuses[3]

		NewCAPEPart = Bus1.rjust(6) + ',' + Bus2.rjust(6) + ',' + Bus3.rjust(6) + ',' +  cktID
		NewPlanningPart = planningBus1.rjust(6) + ',' + planningBus2.rjust(6) + ',' + planningBus3.rjust(6) + ',' +  planningcktID
		nLine = NewCAPEPart + '->' + NewPlanningPart
		cleanSubSet.add(nLine)

for line in list(cleanSubSet):
	print line
