"""
Function to organize all the relevant tf data, output is a dictionary with the tf id as key
Please note: The raw file should have two winders only
"""

def getTFData(Raw):

	TFDataDict = {} # key: Bus no, value: class structure defined above

	class TFData(object): 
		# class to store all the data
		def __init__(self):
			self.Bus1 = ''
			self.Bus2 = ''
			self.cktID = ''
			self.CW = ''
			self.CZ = ''
			self.R = ''
			self.X = ''
			self.SBase = ''
			self.name = ''
			self.shift = ''
			self.NOMV1 = 0.0
			self.WINDV1 = 0.0
			self.NOMV2 = 0.0
			self.WINDV2 = 0.0


	def extractData(key,Bus1,Bus2,Bus3,cktID,i):
		# function to extract the relevant data, given the bus number and some other info

		TFDataDict[key] = TFData()
		line = fileLines[i]
		words = line.split(',')
		TFDataDict[key].Bus1 = Bus1
		TFDataDict[key].Bus2 = Bus2
		TFDataDict[key].cktID = cktID
		TFDataDict[key].CW = words[4].strip()
		TFDataDict[key].CZ = words[5].strip()
		TFDataDict[key].name = words[10].strip()

		i+=1 
		line = fileLines[i]
		words = line.split(',')
		TFDataDict[key].R = words[0].strip()
		TFDataDict[key].X = words[1].strip()
		TFDataDict[key].SBase = words[2].strip()

		i+=1 
		line = fileLines[i]
		words = line.split(',')
		TFDataDict[key].shift = float(words[2].strip())
		TFDataDict[key].WINDV1 = float(words[0].strip())
		TFDataDict[key].NOMV1 = float(words[1].strip())

		i+=1 
		line = fileLines[i]
		words = line.split(',')
		TFDataDict[key].WINDV2 = float(words[0].strip())
		TFDataDict[key].NOMV2 = float(words[1].strip())	

	######	



	with open(Raw,'r') as f:
		filecontent = f.read()
		fileLines = filecontent.split('\n')

	tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
	tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')


	i = tfStartIndex
	while i < tfEndIndex:
		line = fileLines[i]
		words = line.split(',')
		Bus1 = words[0].strip()
		Bus2 = words[1].strip()
		Bus3 = words[2].strip()
		cktID = words[3].strip()
		status  = words[11].strip()
		key = Bus1.rjust(6) + ',' + Bus2.rjust(6) + ',' + Bus3.rjust(6) + ',' + cktID

		if Bus3 == '0':
			if status != '1': #disconnected tf
				i+=4
				continue

			#extractData(key,TFDataDict,1,i,fileLines)
			extractData(key,Bus1,Bus2,Bus3,cktID,i)
			#extractData(Bus2,TFDataDict,0,i,fileLines)

			i+=4
		else:
			i+=5

	return TFDataDict


if __name__ == '__main__':
	Raw = 'hls18v1dyn_1219.raw'
	TFDataDict = getTFData(Raw)

