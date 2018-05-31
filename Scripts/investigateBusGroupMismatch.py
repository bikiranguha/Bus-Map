"""
Outputs any mismatches from given bus report data
Has two modes:
	Output all the mismatch in a consolidated fashion
	Search manually for mismatch data
"""

# external functions and data
from analyzeBusReportFn import BusFlowData # organize the bus flow data into a class structure
from getBranchGroupFn import makeBranchGroups # this function will help map any ties to buses which are already mapped

flowReport = 'BusReports_RAW0530.txt'
CAPERaw = 'RAW0530.raw'
mismatchDataFile = 'mismatchData0530.txt' # contains all the current mismatch data

flowData = BusFlowData(flowReport,CAPERaw)
"""
Clues on how to access the data within flowData:
Each key of flowData contains the following class
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
"""
BranchGroupDict = makeBranchGroups(CAPERaw) # every value here is a set
##########################
#functions used here

def getMismatch(searchBus):
	# function to get the total mismatch 
	totalMWMismatch = 0.0
	totalMVARMismatch = 0.0
	try: # for bus groups
		for ties in list(BranchGroupDict[searchBus]):
			totalMWMismatch += flowData[ties].MismatchMW
			totalMVARMismatch += flowData[ties].MismatchMVAR

	except: # for single buses
		totalMWMismatch = flowData[searchBus].MismatchMW
		totalMVARMismatch = flowData[searchBus].MismatchMVAR

	return totalMWMismatch, totalMVARMismatch


################

# main body
print 'Please make a choice:'
print '1: Identify all the mismatches'
print '2: Manually check the mismatches (also can check within groups)'

choice = raw_input('Your choice: ')


if choice == '1':
	# output all the mismatches to the mismatchDataFile
	mismatchLines = []
	explored  = set()
	for Bus in flowData.keys():
		if Bus in explored:
			continue
		totalMWMismatch, totalMVARMismatch = getMismatch(Bus)

		if abs(totalMWMismatch) > 0 or abs(totalMVARMismatch) > 0:
			try: # if its a group
				currentGroupSet = BranchGroupDict[Bus]
				groupString = ''
				for x in list(currentGroupSet):
					groupString += x
					groupString += ','
					explored.add(x)
				groupString = groupString[:-1]


			except: # single bus
				explored.add(Bus)
				groupString = Bus

			line = groupString + ':' + str(totalMWMismatch) + ',' + str(totalMVARMismatch)
			mismatchLines.append(line)


	with open(mismatchDataFile,'w') as f:
		f.write('Buses:MW Mismatch, MVAR Mismatch')
		f.write('\n')
		for line in mismatchLines:
			f.write(line)
			f.write('\n')

	print 'All mismatch data in ' + flowReport + ' successfully written to ' + mismatchDataFile





if choice == '2':
	# Manually check stuff
	while True:
		searchBus = raw_input('Bus to search for: ')
		totalMWMismatch, totalMVARMismatch = getMismatch(searchBus)

		try:
			print 'Mismatch in flows in the group:'
			print 'Buses in the group: ', str(list(BranchGroupDict[searchBus]))
			print 'Mismatch MW: ', totalMWMismatch
			print 'Mismatch MVAR: ', totalMVARMismatch
			print '\n'
		except:
			print 'No ties to this bus'
			print 'Mismatch MW: ', totalMWMismatch
			print 'Mismatch MVAR: ', totalMVARMismatch
			print '\n'





