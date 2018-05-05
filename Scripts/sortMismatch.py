"""
Script to sort CAPE comed buses according to their mismatch MVA (descending) in the given raw file
"""
import math

flowReport = 'log_allCAPEComedBusReports.txt'
latestRaw = 'RAW0501.raw' # latest raw file
flowDict = {}
ComedBusSet = set()
MismatchDict = {}
sortedMismatchLines = []
sortedMismatchData = 'sortedMismatchData.txt'
BusNameDict = {}
BusVoltDict = {}
"""
class loadReport(object):
	def __init__(self):
		self.toBus = []
		self.MWList = []
		self.MVARList = []
		self.cktID = []
"""

# Generate a set of all comed buses in the CAPE model

with open(latestRaw, 'r') as f:
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
		area = words[4].strip()

		if area == '222':
			#BusAngleDict[Bus] = angle
			ComedBusSet.add(Bus)
			BusVolt = words[2].strip()
			BusVoltDict[Bus] =BusVolt
			BusNameDict[Bus] = words[1].strip("'").strip()
####





with open(flowReport,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

#helperLine = '  BUS# X-- NAME --X BASKV ZONE  PU/KV  ANGLE  MW/MVAR MW/MVAR MW/MVAR   BUS# X-- NAME --X BASKV AREA CKT   MW    MVAR   RATIO   ANGLE   AMPS   %  SET A'
matchingPattern = '---------------------------------------------------------------------------------'
indices = [i for i, x in enumerate(fileLines) if matchingPattern in x] # indices of the all the relevant starting lines

for ind in indices:
	# line 1
	line = fileLines[ind]
	words = line.split()
	currentBus = words[0].strip()
	#flowDict[currentBus] = loadReport()
	# line 2
	ind+=1
	mismatchLineFound = 0
	# remaining lines
	#while 'COMED 2018,  HLS18V1, N18S OUTSIDE AND 18 INTCHNG' not in fileLines[ind] or 'M I S M A T C H' not in fileLines[ind]:
	while mismatchLineFound == 0:
		line = fileLines[ind]
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
			MismatchDict[currentBus] = [MVA,MW,MVAR]
			mismatchLineFound = 1
		else:
			if 'PTI INTERACTIVE POWER SYSTEM SIMULATOR' in line:
				break
			ind +=1

for key, value in sorted(MismatchDict.iteritems(), key=lambda (k,v): v[0], reverse = True  ):
	MVA = '%.2f' %MismatchDict[key][0]
	string = key + ',' +  BusNameDict[key] + ',' + BusVoltDict[key] + ',' + MVA + ',' + str(MismatchDict[key][1]) + ',' + str(MismatchDict[key][2])
	#if BusVoltDict[key] == '345.0000':
		#print string
	sortedMismatchLines.append(string)
	
with open(sortedMismatchData,'w') as f:
	f.write('Bus, Bus Name, Bus Voltage, Mismatch MVA, Mismatch MW, Mismatch MVAR')
	f.write('\n')
	for line in sortedMismatchLines:
		f.write(line)
		f.write('\n')



