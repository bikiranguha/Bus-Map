"""
Check if there is any duplication of the bus data
"""

#raw_file = 'testRAW04052018_fixedload.raw'
raw_file = 'tmp_island_branch_fixedv2.raw'
BusSet = set()

# get comed bus voltages
with open(raw_file, 'r') as f:
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
		if Bus not in BusSet:
			BusSet.add(Bus)
		else:
			print Bus