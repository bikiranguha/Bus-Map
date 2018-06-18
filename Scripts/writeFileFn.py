"""
	Function which writes fileLines into fileName, and adds headers, if any
"""

def writeToFile(fileName,fileLines,header):
	with open(fileName,'w') as f:
		if header != '':
			f.write(header)
			f.write('\n')

		for line in fileLines:
			f.write(line)
			f.write('\n')