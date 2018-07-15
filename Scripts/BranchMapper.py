"""
function which can automate bus mapping, given the manual mappings in a file
can handle one to many mapping
"""
import sys
#sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2')

changeBusNoLog='changeBusNoLog.txt'

def MapChange(planningRaw,changeFile,BranchInput,BranchOutput,originalCase):
	
	newBranchLines = []
	OldBranchLines = []  # changing new cape to old cape numbers
	BranchImpedanceDictCAPE={}
	CAPEold2NewDict={}

	def makeBranchImpedanceDict(Raw):
		# generates a branch impedance dict from the given raw file
		# key: Bus1 + ',' + Bus2 + ',' + cktID, value = [R,X] where R and X are both strings
		with open(Raw, 'r') as f:
			BranchImpedanceDict = {}
			filecontent = f.read()
			fileLines = filecontent.split('\n')
			branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA') + 1
			branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')

			for i in range(branchStartIndex, branchEndIndex):
				line = fileLines[i]
				words = line.split(',')
				Bus1 = words[0].strip()
				Bus2 = words[1].strip()	
				cktID = words[2].strip("'").strip()
				key = Bus1 + ',' + Bus2 + ',' + cktID
				R = words[3]
				X = words[4]
				BranchImpedanceDict[key] = [R,X]	
		return BranchImpedanceDict

	BranchImpedanceDictPlanning = makeBranchImpedanceDict(planningRaw) # generate the impedance dict for planning

	#####################

	def reconstructLine2(words):
		currentLine = ''
		for word in words:
			currentLine += word
			currentLine += ','
		return currentLine[:-1]

	########

	with open(changeBusNoLog,'r') as f:
		filecontent = f.read()
		fileLines = filecontent.split('\n')

		for line in fileLines:
			if 'CAPE' in line:
				continue
			if '->' in line:
				words=line.split('->')
				CAPEold2NewDict[words[0].strip()]=words[1].strip()


	# open the file which contains the list of manual changes necessary
	with open(changeFile,'r') as f:
		filecontent = f.read()
		fileLines = filecontent.split('\n')

	i=1
	# get the branch substitution data
	for line in fileLines:
		if '->' in line:
			words=line.split('->')	
			planningPart = words[0].strip()
			panningwords = words[0].split(',')
			CAPEPart = words[1].strip()
			capewords=words[1].split(',')
			capenewwords=[]
			for word in capewords:
				if word.strip() in CAPEold2NewDict.keys():
					capenewwords.append(CAPEold2NewDict[word.strip()])
					
				else:
					capenewwords.append(word)

			CAPEPart=capenewwords[0].strip()+','+capenewwords[1].strip()+','+capenewwords[2].strip()
			

			BranchImpedanceDictCAPE[CAPEPart] =  BranchImpedanceDictPlanning[planningPart]


	

	#print len(BranchImpedanceDictCAPE)

	# generate the new raw file data
	with open(BranchInput,'r') as f:
		filecontent = f.read()
		fileLines = filecontent.split('\n')


	# change any branch data
	for line in fileLines:
		if ',' in line:
			words = line.split(',')
			Bus1 = words[0].strip()
			Bus2 = words[1].strip()	
			cktID = words[2].strip("'").strip()
			key = Bus1 + ',' + Bus2 + ',' + cktID	
			key2 = Bus2 + ',' + Bus1 + ',' + cktID	
			# change branch data if instructed to
			if key in BranchImpedanceDictCAPE.keys():
				#print key
				R = BranchImpedanceDictCAPE[key][0]
				X = BranchImpedanceDictCAPE[key][1]
				words[3] = R
				words[4] = X
				line = reconstructLine2(words)
				#print line

			if key2 in BranchImpedanceDictCAPE.keys():
				#print key
				R = BranchImpedanceDictCAPE[key2][0]
				X = BranchImpedanceDictCAPE[key2][1]
				words[3] = R
				words[4] = X
				line = reconstructLine2(words)
				#print line

			newBranchLines.append(line)


	with open(BranchOutput, 'w') as f:
		for line in newBranchLines:
			f.write(line)
			f.write('\n')	

# only execute this block of code if we are running this file
# wont be executed if we are importing this module

if __name__ == "__main__":
	planningRaw = 'hls18v1dyn_1219.raw'
	BranchInput = 'newbranchData.txt'
	BranchOutput  = 'branchout.txt'
	changeFile = 'BranchImpedanceChanges.txt'
	MapChange(planningRaw,changeFile,BranchInput,BranchOutput,'planning')

