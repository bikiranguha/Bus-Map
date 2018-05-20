"""
Function to organize all the relevant tf data
"""

def getTFData(Raw):

	TFDataDict = {} # key: Bus no, value: class structure defined above

	class TFData(object): 
		# class to store all the data
		def __init__(self):
			self.toBus = []
			self.cktID = []
			self.CW = []
			self.CZ = []
			self.R = []
			self.X = []
			self.SBase = []
			self.name = []
			self.shift = []


	def extractData(Bus,TFDataDict,toBusIndex,i,fileLines):
		# function to extract the relevant data, given the bus number and some other info
		if Bus not in TFDataDict.keys():
			TFDataDict[Bus] = TFData()
		line = fileLines[i]
		words = line.split(',')
		TFDataDict[Bus].toBus.append(words[toBusIndex].strip())
		TFDataDict[Bus].cktID.append(words[3].strip("'").strip())
		TFDataDict[Bus].CW.append(words[4].strip())
		TFDataDict[Bus].CZ.append(words[5].strip())
		TFDataDict[Bus].name.append(words[10].strip())

		i+=1 
		line = fileLines[i]
		words = line.split(',')
		TFDataDict[Bus].R.append(words[0].strip())
		TFDataDict[Bus].X.append(words[1].strip())
		TFDataDict[Bus].SBase.append(words[2].strip())

		i+=1 
		line = fileLines[i]
		words = line.split(',')
		TFDataDict[Bus].shift.append(float(words[2].strip()))	

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
		status  = words[11].strip()

		if status != '1': #disconnected tf
			i+=4
			continue

		extractData(Bus1,TFDataDict,1,i,fileLines)
		extractData(Bus2,TFDataDict,0,i,fileLines)

		i+=4

	return TFDataDict


if __name__ == '__main__':
	Raw = 'hls18v1dyn_1219.raw'
	TFDataDict = getTFData(Raw)

