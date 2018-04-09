planningRaw = 'hls18v1dyn_new.raw'


voltOptions = set() # all the diff voltages present in the comed system
lines34 = []
set34 = set()
# generate NeighbourDict for branches
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
		BusVolt = float(words[2].strip())
		angle = float(words[8].strip())
		area = words[4].strip()
		#AreaDict[Bus] = area
		if area == '222':
			#voltOptions.add(BusVolt)
			if BusVolt > 30.0 and BusVolt < 40.0:
				set34.add(Bus)
				lines34.append(line)


#print voltOptions
with open('list34.txt','w') as f:
	for line in lines34:
		f.write(line)
		f.write('\n')

branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA') + 1
branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')


for i in range(branchStartIndex,branchEndIndex):

	line = fileLines[i]

	words = line.split(',')

	Bus1 = words[0].strip()
	Bus2 = words[1].strip()

	status = words[-5].strip()
	if Bus1 in set34 or Bus2 in set34:
		if status == '1':
			print line