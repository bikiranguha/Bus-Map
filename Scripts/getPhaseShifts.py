"""
look at log of angle changes and generate an angle change dictionary
"""

directory = 'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders'
angleChangeFile = directory + '/' + 'logAngleChange.txt'

AngleChangeDict = {}

# Read the angle change values and generate a dict
with open(angleChangeFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'Bus' in line:
			continue

		if line == '':
			continue

		words = line.split('->')
		Bus = words[0].strip()
		Angle = float(words[1].strip()) 

		if Angle == 0.0: # Add to dictionary only if there is a phase shift
			#print Bus
			continue
		
		AngleChangeDict[Bus] = Angle