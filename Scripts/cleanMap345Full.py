newLines = []
Map345PartiallyCleaned = 'mapping_test_0602.txt'
Map345FullCleaned = 'mapping_test_0602_flip.txt'


with open(Map345PartiallyCleaned,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue

		words = line.split('->')
		CAPESide = words[0].strip()
		planningSide = words[1].strip()
		planningSideWords = planningSide.split(',')
		
		newString = planningSideWords[-1].strip() + '->' + CAPESide.strip()

		newLines.append(newString)


with open(Map345FullCleaned,'w') as f:
	for line in newLines:
		f.write(line)
		f.write('\n')
