"""
Outputs any mismatches from given bus report data
Has two modes:
	Output all the mismatch in a consolidated fashion
	Search manually for mismatch data
"""

# external functions and data
import sys
sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2')
import math
from getBusDataFn import getBusData


from analyzeBusReportFn import BusFlowData # organize the bus flow data into a class structure
from getBranchGroupFn import makeBranchGroups # this function will help map any ties to buses which are already mapped

flowReport = 'BusReports_RAW0602_final.txt' # CAPE bus flow report
CAPERaw = 'RAW0602.raw'
mismatchDataFile = 'mismatchDataRAW0602_check.txt' # contains all the current mismatch data
planningRaw = 'hls18v1dyn_1219.raw'
MapFile = 'blue2red345.txt' # CAPE to planning updated bus map
planningflowReport = 'BusReports_Planning.txt' # Planning bus flow report

flowData = BusFlowData(flowReport,CAPERaw)
planningflowData = BusFlowData(planningflowReport,planningRaw)
planningBusDataDict = getBusData(planningRaw)
CAPEBusDataDict = getBusData(CAPERaw)
planningBusDataDict = getBusData(planningRaw)
mismatchDictHighPriority = {}
mismatchDictLowPriority = {}
MapDict = {}
#mismatchLinesHighPriority =[]
#mismatchLinesLowPriority  = []
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



def generateBusFlowLines(totalMWMismatch,totalMVARMismatch,key,currentGroupSet,mismatchDict):
	# generate the mismatch data for the group and also the flow data for each bus in the group
	mismatchLines = []
	mismatchMVA = math.sqrt(totalMWMismatch**2 + totalMVARMismatch**2)
	mismatchString = key + ':' +  str(totalMWMismatch) + ',' + str(totalMVARMismatch)
	mismatchLines.append(mismatchString)
	#print mismatchString
	for fromBus in list(currentGroupSet):
		#print fromBus
		#print list(currentGroupSet)
		fromBusName = CAPEBusDataDict[fromBus].name
		fromBusVolt = CAPEBusDataDict[fromBus].NominalVolt
		
		for i in range(len(flowData[fromBus].toBus)):
			#print i
			
			currentToBus = flowData[fromBus].toBus[i]
			MVAFlow = flowData[fromBus].MVAList[i]
			if MVAFlow == 0.0:
				continue
			MWFlow = flowData[fromBus].MWList[i]
			MVARFlow = flowData[fromBus].MVARList[i]
			toBusName = CAPEBusDataDict[currentToBus].name
			toBusVolt = CAPEBusDataDict[currentToBus].NominalVolt
			flowString = fromBus + ',' + fromBusName + ',' + fromBusVolt + '->' + currentToBus + ',' + toBusName + ',' + toBusVolt + ':' + str(MWFlow) + ',' + str(MVARFlow)
			#print flowString
			mismatchLines.append(flowString)

	# get the planning maps and planning flows
	toGetFlow = set()
	# print the maps
	for Bus in list(currentGroupSet):
		try:
			planningBus = MapDict[Bus]
			toGetFlow.add(planningBus)
			string = Bus + '->' + planningBus
			mismatchLines.append(string)
		except:
			continue

	# print the flows
	for planningFromBus in list(toGetFlow):
		fromBusName = planningBusDataDict[planningFromBus].name
		fromBusVolt = planningBusDataDict[planningFromBus].NominalVolt	
		for j in range(len(planningflowData[planningFromBus].toBus)):
			currentToBus = 	planningflowData[planningFromBus].toBus[j]
			MVAFlow = planningflowData[planningFromBus].MVAList[j]
			if MVAFlow == 0.0:
				continue
			MWFlow = planningflowData[planningFromBus].MWList[j]
			MVARFlow = planningflowData[planningFromBus].MVARList[j]
			toBusName = planningBusDataDict[currentToBus].name
			toBusVolt = planningBusDataDict[currentToBus].NominalVolt
			flowString = planningFromBus + ',' + fromBusName + ',' + fromBusVolt + '->' + currentToBus + ',' + toBusName + ',' + toBusVolt + ':' + str(MWFlow) + ',' + str(MVARFlow)
			mismatchLines.append(flowString)







	mismatchDict[key] = [mismatchMVA,mismatchLines]

			






################

# get Mapping info
with open(MapFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		words = line.split('->')
		CAPEBus = words[0].strip()
		try:
			PlanningBus = words[2].strip()
		except:
			continue
		MapDict[CAPEBus] = PlanningBus





# main body
print 'Please make a choice:'
print '1: Identify all the mismatches'
print '2: Manually check the mismatches (also can check within groups)'

choice = raw_input('Your choice: ')


if choice == '1':
	# get all the low priority buses which will be shown separately in the mismatch data
	lowPriorityBusList = []
	for Bus in planningBusDataDict.keys():
		if planningBusDataDict[Bus].area == '222' and planningBusDataDict[Bus].name.endswith('M'):
			lowPriorityBusList.append(Bus)

	for Bus in CAPEBusDataDict.keys():
		if CAPEBusDataDict[Bus].area == '222' and CAPEBusDataDict[Bus].name.startswith('T3W'):
			lowPriorityBusList.append(Bus)


	# output all the mismatches to the mismatchDataFile
	highPriorityMismatchDict = {}
	lowPriorityMismatchDict = {}
	explored = set()
	# generate the mismatch dictionaries
	for Bus in flowData.keys():
		if Bus in explored:
			continue
		totalMWMismatch, totalMVARMismatch = getMismatch(Bus)

		if abs(totalMWMismatch) > 0 or abs(totalMVARMismatch) > 0:
			try: # if its a group
				currentGroupSet = BranchGroupDict[Bus]
				key = ''
				for x in list(currentGroupSet):
					key += x
					key += ','
					explored.add(x)		
				key = key[:-1]
				generateBusFlowLines(totalMWMismatch,totalMVARMismatch,key,currentGroupSet,mismatchDictHighPriority)

			except: # single bus
				key = Bus
				if Bus in lowPriorityBusList:
					generateBusFlowLines(totalMWMismatch,totalMVARMismatch,key,[Bus],mismatchDictLowPriority)
					#generateMisMatchValues(totalMWMismatch,totalMVARMismatch,lowPriorityMismatchDict,key)
				else:
					generateBusFlowLines(totalMWMismatch,totalMVARMismatch,key,[Bus],mismatchDictHighPriority)
				













	with open(mismatchDataFile,'w') as f:
		
		f.write('Buses:MW Mismatch, MVAR Mismatch')
		f.write('From,FromName,FromVolt->To,ToName,ToVolt:FlowMW,FlowMVAR')
		f.write('\n')
		"""
		for line in mismatchLines:
			f.write(line)
			f.write('\n')
		"""
		f.write('High priority:')
		f.write('\n')
		for key, value in sorted(mismatchDictHighPriority.iteritems(), key=lambda (k,v): v[0], reverse = True  ): 
			# sorts in descending order according to the 1st element in value (which is the MVA mismatch)
			mismatchLines = value[1]
			for line in mismatchLines:
			#line = key + ':' + mismatchString
				f.write(line)
				f.write('\n')
			f.write('\n')


		f.write('Low priority:')
		f.write('\n')
		for key, value in sorted(mismatchDictLowPriority.iteritems(), key=lambda (k,v): v[0], reverse = True  ): 
			# sorts in descending order according to the 1st element in value (which is the MVA mismatch)
			mismatchLines = value[1]
			for line in mismatchLines:
			#line = key + ':' + mismatchString
				f.write(line)
				f.write('\n')
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





