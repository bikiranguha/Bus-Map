"""
Function to get all Bus Data with Raw file name as input
"""


def getBusData(Raw):

	BusDataDict = {}
	class BusData(object):
		def __init__(self):
			self.name = ''
			self.NominalVolt = ''
			self.area = ''
			self.type = ''
			self.voltpu = ''
			self.angle = ''


	with open(Raw, 'r') as f:
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
			BusType =  words[3].strip()
			if BusType == '4':
				continue
			BusDataDict[Bus] = BusData()
			BusDataDict[Bus].name = words[1].strip("'")
			BusDataDict[Bus].NominalVolt = words[2].strip()
			BusDataDict[Bus].type = BusType
			BusDataDict[Bus].area = words[4].strip()
			BusDataDict[Bus].voltpu = words[7].strip()
			BusDataDict[Bus].angle = words[8].strip()
	return BusDataDict


			