# get the load data in load data new (raw0406) and load data old (raw0322)
# delete all the lines appearing in testraw0405 and add all the lines in load data new
load_data_old = 'loadDataOld.txt'
load_data_new = 'loadDataNew.txt'
raw_old = 'testRAW04052018.raw'
raw_new = 'testRAW04052018_fixedload.raw'
loadBusFile = 'loadBusFile.txt'

load_to_delete = set()
load_to_add = []
loadBusSet = set()


with open(load_data_old,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue

		load_to_delete.add(line)


with open(load_data_new,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		load_to_add.append(line)

		words = line.split(',')
		Bus = words[0].strip()
		loadBusSet.add(Bus)


newRawLines = []
with open(raw_old,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')


loadStartIndex = fileLines.index('0 / END OF BUS DATA, BEGIN LOAD DATA') + 1
loadEndIndex = fileLines.index('0 / END OF LOAD DATA, BEGIN FIXED SHUNT DATA')


for i in range(loadStartIndex):
	line = fileLines[i]
	newRawLines.append(line)


for i in range(loadStartIndex,loadEndIndex):
	line = fileLines[i]
	if line in load_to_delete:
		continue

	newRawLines.append(line)

for line in load_to_add:
	newRawLines.append(line)

for i in range(loadEndIndex,len(fileLines)):
	line = fileLines[i]
	newRawLines.append(line)



with open(raw_new,'w') as f:
	for line in newRawLines:
		f.write(line)
		f.write('\n')


with open(loadBusFile,'w') as f:
	f.write('List of load buses:')
	f.write('\n')
	for bus in list(loadBusSet):
		f.write(bus)
		f.write('\n')