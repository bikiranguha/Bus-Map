# read the CAPE side of autoTFMap0628 and see if any of the transformers are present in the cropped raw file
load_split_input = 'autoTFMap0628_cleaned.txt'
croppedRaw = 'RAWCropped_0711.raw'
tfSet = set() # set of tf in CAPE cropped raw
load_split_tfSet = [] # set of CAPE tf involved in load split
load_split_dict = {}
with open(load_split_input,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if '->' not in line:
			continue
		words = line.split('->')
		CAPESide = words[1].strip()
		CAPESideWords = CAPESide.split(',')
		Bus1 = CAPESideWords[0].strip()
		Bus2 = CAPESideWords[1].strip()
		cktID = CAPESideWords[2].strip()

		tfKey = Bus1.rjust(6) + ',' + Bus2.rjust(6) + ',' + '     0' + ',' + "'" + cktID + " '"
		#print tfKey
		load_split_tfSet.append(tfKey)
		load_split_dict[tfKey] = line


with open(croppedRaw,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')


tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')

i = tfStartIndex
while i<tfEndIndex:
	line = fileLines[i]
	words = line.split(',')
	tfKey = line[:25]
	#Bus1 = words[0].strip()
	#Bus2 = words[1].strip()
	#status  = words[11].strip()
	tfSet.add(tfKey)
	i+=4


for tf in load_split_tfSet:
	if tf in tfSet:
		print load_split_dict[tf]
		#print tf
