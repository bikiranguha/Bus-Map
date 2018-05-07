"""
Generates a dictionary of comed planning bus data
"""

planningRaw = 'hls18v1dyn_1219.raw'

planningBusDataDict = {}


# get the relevant comed bus sets
with open(planningRaw, 'r') as f:
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

		if area == '222':
			planningBusDataDict[Bus] = line