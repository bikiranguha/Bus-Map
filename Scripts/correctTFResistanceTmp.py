raw_file = 'FinalRAW03272018.raw'
newRawFile = 'testRAW.raw'

newRawLines = []
highImpedanceSet = set()

def reconstructLine2(words):
	currentLine = ''
	for word in words:
		currentLine += word
		currentLine += ','
	return currentLine[:-1]

def addMultLines(i,fileLines,newtfLines,numLines):
	# for adding transformer lines which do not change
	for j in range(numLines):
		i+=1
		line = fileLines[i]
		newtfLines.append(line)	
	return i

with open(raw_file,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')

# add all lines before tf data
for i in range(tfStartIndex):
	line = fileLines[i]
	newRawLines.append(line)


i = tfStartIndex 
# add 1st line, contains bus info
line = fileLines[i]
newRawLines.append(line)
i+=1

# set resistance to zero if its too high for tf
while i < tfEndIndex:
	if line == '':
		continue
	line = fileLines[i]
	words = line.split(',')
	R = words[0].strip()
	floatR = float(R)

	if floatR > 100.0:
		highImpedanceSet.add(floatR)
		if floatR == 300.0:
			print fileLines[i-1]
		# set resistance to zero, reconstruct the line and append it
		Rnew = '0.00000E+0'
		words[0] = Rnew
		line = reconstructLine2(words)
		newRawLines.append(line)
		# add the next 3 lines and increase by 1 to continue to the next tf
		i = addMultLines(i,fileLines,newRawLines,3)
		i+=1
	else:
		# add the next 3 lines and increase by 1 to continue to the next tf
		newRawLines.append(line)
		i = addMultLines(i,fileLines,newRawLines,3)
		i+=1


# add all lines after tf data
for i in range(tfEndIndex+1, len(fileLines)):
	line = fileLines[i]
	newRawLines.append(line)

# write to file
with open(newRawFile,'w') as f:
	for line in newRawLines:
		f.write(line)
		f.write('\n')

print min(highImpedanceSet)