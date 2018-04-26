"""
	Script updates the special cases related to tf which were originally 4 winders in CAPE and had some sort of substitution in planning
	Also runs substitute3wTo2w.py and uses the tf data generated there to build the final raw file
"""
from substitute3wTo2w import newImp2WinderLines # all the tf data in the 2 winder raw file, with relevant 3 winders converted to 2 winders

tfSkipFile = 'TFToSkip.txt'
newTFDataFile = 'newTFDataToSubstitute.txt'
old2winderRawFile = '2wnd_RAW03222018.raw'
newRawFile = 'FinalRAW03272018Old.raw'

skipLineSet = []
newtfLines = []
newRawLines = []

with open(tfSkipFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'Case' in line:
			continue
		if line == '':
			continue
		skipLineSet.append(line.strip())

with open(newTFDataFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'Case' in line:
			continue
		if line == '':
			continue
		newtfLines.append(line)	


with open(old2winderRawFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')

for i in range(tfStartIndex):
	line = fileLines[i]
	newRawLines.append(line)




#i = tfStartIndex
i = 0

while i < len(newImp2WinderLines):
	#line = fileLines[i]
	line = newImp2WinderLines[i]
	if line == '':
		continue
	skiptffound= 0
	for tf in skipLineSet:
		if tf in line:
			skiptffound = 1
			break
	if skiptffound == 1:
		i+=4
		continue

	newRawLines.append(line)
	i+=1

for line in newtfLines:
	newRawLines.append(line)

for i in range(tfEndIndex, len(fileLines)):
	line = fileLines[i]
	newRawLines.append(line)


with open(newRawFile,'w') as f:
	for line in newRawLines:
		f.write(line)
		f.write('\n')

#import changeBusAngleTree # implements phase shift of branches of original buses through BFS