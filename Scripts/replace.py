"""
Replace a search term with whatever you want
In files where the search term is present
"""

import os

while True:

	searchTerm = raw_input('Please enter search term:')
	replaceTerm = raw_input('Please enter replace term: ')
	cwd = os.getcwd()
	print 'Search Term appears as a file in the following locations:'
	"""
	for root, dirs, files in os.walk(cwd, topdown=True):
	   for name in files:
	   	if searchTerm in name:
	   		currentdir =  os.path.join(cwd,root)
	   		print os.path.join(currentdir, name)

	print 'Search Term appears inside the following files:'
	"""


	for root, dirs, files in os.walk(cwd, topdown=True):
		for name in files:
			if name.endswith('.py'):
				currentFile = os.path.join(root, name)
				with open(currentFile,'r') as f:
					filecontent = f.read()
					if searchTerm in filecontent:
						newFileLines = []
						# change the absolute path
						fileLines = filecontent.split('\n')
						for line in fileLines:
							if searchTerm in line:
								nLine = line.replace(searchTerm,replaceTerm)
								newFileLines.append(nLine)
							else:
								newFileLines.append(line)
							

						# generate new raw file
						with open(currentFile,'w') as f:
							for line in newFileLines:
								f.write(line)
								f.write('\n')
						print 'searchTerm replaced in ' + currentFile

