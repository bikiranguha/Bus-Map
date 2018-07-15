nonComedOriginalFile = 'outsideComedBusesv4_original.txt'
nonComedNewFile = 'outsideComedBusesv4_test.txt'



outsideOrgSet = set()
outsideNewSet = set()
with open(nonComedOriginalFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue

		try:
			x = float(line.strip()) # line is a number
			outsideOrgSet.add(line.strip())
		except:
			continue


with open(nonComedNewFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		outsideNewSet.add(line.strip())


for Bus in list(outsideNewSet):
	if Bus not in outsideOrgSet:
		print Bus


"""
for Bus in list(outsideOrgSet):
	if Bus not in outsideNewSet:
		print Bus
"""


