"""
Organizes all the important data in bus flow reports into a dictionary with the from Bus as key and the value is a class structure holding all mismatch info
"""

def BusFlowData(flowReport,Raw):
	# flowReport: Bus flow report
	# Raw: Raw file you want to read
	import math
	flowDict = {}
	areaList = []


	class mismatchReport(object):
		def __init__(self):
			self.toBus = []
			self.MWList = []
			self.MVARList = []
			self.MVAList = []
			self.cktID = []
			self.MismatchMVA = 0.0
			self.MismatchMW = 0.0
			self.MismatchMVAR = 0.0



	# get all the area codes
	with open(Raw,'r') as f:
		filecontent = f.read()
		fileLines = filecontent.split('\n')
		areaStartIndex = fileLines.index("0 / END OF TRANSFORMER DATA, BEGIN AREA DATA") + 1
		areaEndIndex = fileLines.index("0 / END OF AREA DATA, BEGIN TWO-TERMINAL DC DATA")

		for i in range(areaStartIndex,areaEndIndex):
			line = fileLines[i]
			words = line.split(',')
			area = words[0].strip()
			areaList.append(area)
	# get the flow data
	with open(flowReport,'r') as f:
		filecontent = f.read()
		fileLines = filecontent.split('\n')

	#print areaList
	#helperLine = '  BUS# X-- NAME --X BASKV ZONE  PU/KV  ANGLE  MW/MVAR MW/MVAR MW/MVAR   BUS# X-- NAME --X BASKV AREA CKT   MW    MVAR   RATIO   ANGLE   AMPS   %  SET A'
	matchingPattern = '---------------------------------------------------------------------------------'
	indices = [i for i, x in enumerate(fileLines) if matchingPattern in x] # indices of the all the relevant starting lines

	for ind in indices:
		# line 1
		line = fileLines[ind]
		words = line.split()
		currentBus = words[0].strip()
		flowDict[currentBus] = mismatchReport()
		# line 2
		ind+=1
		line = fileLines[ind]
		words = line.split()
		words = [word for word in words if word != ''] # exclude all elements which are blanks
		firstToBus = words[5].strip()
		#cktID = words[10].strip()
		flowDict[currentBus].toBus.append(firstToBus)
		try:
			areaIndex = words.index('222')
		except:
			for area in areaList:
				if area in words:
					areaIndex = words.index(area)
		cktIndex = areaIndex + 1
		MWIndex = areaIndex + 2
		MVARIndex = areaIndex + 3
		cktID = words[cktIndex].strip()
		flowDict[currentBus].cktID.append(cktID)
		
		try: # not lumped together
			MW = float(words[MWIndex].strip())
			MVAR = float(words[MVARIndex].strip())
		except: # lumped together
			splitMWMVARWords = words[MWIndex].strip().split('-') # split the MW and MVAR info, since they are lumped together
			if splitMWMVARWords[0] != '': # only MVAR value is negative
				MW = float(splitMWMVARWords[0].strip())
				MVAR = -float(splitMWMVARWords[1].strip())
			else: # both MW and MVAR values are negative
				MW = -float(splitMWMVARWords[1].strip())
				MVAR = -float(splitMWMVARWords[2].strip())
		
		MVA = math.sqrt(MW**2 + MVAR**2)
		flowDict[currentBus].MWList.append(MW)
		flowDict[currentBus].MVARList.append(MVAR)
		flowDict[currentBus].MVAList.append(MVA)


		ind +=1
		nextLineWords = fileLines[ind].split()
		nextLineWords = [word for word in nextLineWords if word != ''] # exclude all elements which are blanks

		# remaining lines
		while nextLineWords[2] in areaList or nextLineWords[3] in areaList or nextLineWords[4] in areaList or nextLineWords[5] in areaList: # continue till we can find the area info in line
			# get current area
			if nextLineWords[2] in areaList:
				currentArea = nextLineWords[2]
			elif nextLineWords[3] in areaList:
				currentArea = nextLineWords[3]
			elif nextLineWords[4] in areaList:
				currentArea = nextLineWords[4]
			elif nextLineWords[5] in areaList:
				currentArea = nextLineWords[5]
			line = fileLines[ind]
			#if currentArea != '222':
			#	print line


			words = line.split()
			words = [word for word in words if word != '']
			toBus = words[0].strip()
			# check if i am correct about the index of the toBus
			#cktID = words[10].strip()
			flowDict[currentBus].toBus.append(toBus)
			areaIndex = words.index(currentArea)
			cktIndex = areaIndex + 1
			MWIndex = areaIndex + 2
			MVARIndex = areaIndex + 3
			cktID = words[cktIndex].strip()
			flowDict[currentBus].cktID.append(cktID)
			
			try: # not lumped together
				MW = float(words[MWIndex].strip())
				MVAR = float(words[MVARIndex].strip())
			except: # lumped together
				splitMWMVARWords = words[MWIndex].strip().split('-') # split the MW and MVAR info, since they are lumped together
				if splitMWMVARWords[0] != '': # only MVAR value is negative
					MW = float(splitMWMVARWords[0].strip())
					MVAR = -float(splitMWMVARWords[1].strip())
				else: # both MW and MVAR values are negative
					MW = -float(splitMWMVARWords[1].strip())
					MVAR = -float(splitMWMVARWords[2].strip())
			MVA = math.sqrt(MW**2 + MVAR**2)
			flowDict[currentBus].MWList.append(MW)
			flowDict[currentBus].MVARList.append(MVAR)
			flowDict[currentBus].MVAList.append(MVA)		
			#increment index
			if ind < len(fileLines)-1:
				ind+=1
				line  = fileLines[ind]
				nextLineWords = line.split()
				nextLineWords = [word for word in nextLineWords if word != ''] # exclude all elements which are blanks



				# get the mismatch info
				if 'M I S M A T C H' in line:
					words = line.split('M I S M A T C H')
					rightSide = words[1].strip()
					rightSideWords = rightSide.split()
					# Deal with cases where the MW and MVAR values are lumped together (when MVAR or both MW and MVAR are negative)
					try: # not lumped together
						MW = float(rightSideWords[0].strip())
						MVAR = float(rightSideWords[1].strip())
					except: # lumped together
						rightSideWordsTogether = rightSideWords[0].strip().split('-')
						if rightSideWordsTogether[0] != '': # only MVAR value is negative
							MW = float(rightSideWordsTogether[0].strip())
							MVAR = -float(rightSideWordsTogether[1].strip())
						else: # both MW and MVAR values are negative
							MW = -float(rightSideWordsTogether[1].strip())
							MVAR = -float(rightSideWordsTogether[2].strip())
					MVA = math.sqrt(MW**2 + MVAR**2)
					flowDict[currentBus].MismatchMVA = MVA
					flowDict[currentBus].MismatchMW = MW
					flowDict[currentBus].MismatchMVAR = MVAR


			else:
				break

	return flowDict


# testing
if __name__ == "__main__":
	flowReport = 'BusReports_RAW0602_final.txt'
	CAPERaw = 'RAW0509.raw' 
	flowDict = BusFlowData(flowReport,CAPERaw)
