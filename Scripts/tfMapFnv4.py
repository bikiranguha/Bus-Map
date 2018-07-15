"""
Script to carry out tf maps given in changeLines
Old tf data -> New tf data
No bus substitution happens here
"""
import shutil
import sys
#sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2/Raw with only 2 winders/Island 34 system/loadSplit')
#sys.path.insert(0,'C:/Users/Bikiran/Google Drive/Bus Mapping Project Original/Donut Hole Approach/Donut Hole v2')

def doTFMaps(changeLines,oldTFLines,planningBusDataDict,CAPEBusDataDict,TFPSDict):
	# Carry out the TF Maps and implement them in newTFData
	# planningBusDataDict: class structure which contains all the relevant bus info with the bus number as key
	# CAPEBusDataDict: Similar structure, just for CAPE

	#from generatePSDataFn import getPSData # get phase shift info for all tf from given raw file
	#from analyzeLoadFlowReport import flowDict # class which 
	from generateTFDataDict import TFDataDict # dict of planning TF data dict
	#from getPhaseShifts import AngleChangeDict

	NewTFData = {} # dict whose keys are the CAPE bus keys, values are the tf data, with the phase shifts included
	NewBusData = {} # key: CAPE bus no, value: [NominalVolt, Voltpu, AngleStr] to be substituted into CAPE bus data
	newTFLines = []

	# Functions:

	def reconstructLine2(words):
		currentLine = ''
		for word in words:
			currentLine += word
			currentLine += ','
		return currentLine[:-1]





	def generateNewTFData(planningKey,CAPEKey,CAPEData,primaryHVplanning,CAPEHVplanning,NewTFData):
		# generates the new transformer data with bus numbers changed
		# populates NewTFData dictionary with tf data and the key is the CAPE tf id
		newTFList = []

		oldTFList = TFDataDict[planningKey]

		# 1st line
		line1 = oldTFList[0]
		words = line1.split(',')

		if primaryHVplanning == CAPEHVplanning:
			words[0] = ' '*(6-len(CAPEData[0])) + CAPEData[0]
			words[1] = ' '*(6-len(CAPEData[1])) + CAPEData[1]
		else: # need to switch bus numbering
			words[0] = ' '*(6-len(CAPEData[1])) + CAPEData[1]
			words[1] = ' '*(6-len(CAPEData[0])) + CAPEData[0]

		ckt = "'" +   CAPEData[2] + " '" # CAPE tf ckt id
		words[3] = ckt


		line = reconstructLine2(words)
		newTFList.append(line)

		# 2nd line, just add
		newTFList.append(oldTFList[1])


		# 3rd line, import phase shift info
		line3 = oldTFList[2]
		words = line3.split(',')
		try:
			PS = TFPSDict[CAPEKey] # float
		except:
			CAPEKeyWords = CAPEKey.split(',')
			Bus1 = CAPEKeyWords[0].strip()
			Bus2 = CAPEKeyWords[1].strip()
			cktID = CAPEKeyWords[2].strip()
			switchCAPEKeyBuses = Bus2 + ',' + Bus1 + ',' + cktID
			PS = TFPSDict[switchCAPEKeyBuses]
			CAPEKey = switchCAPEKeyBuses

		if PS == 0.0:
			PSstr = '%0.5f' %PS # convert to string
			words[2] = ' '*(8-len(PSstr)) + PSstr
			line = reconstructLine2(words)

		else:
			if primaryHVplanning != CAPEHVplanning: # change sign, since bus order is different
				PS = -PS
			
			PSstr = '%0.5f' %PS
			words[2] = ' '*(8-len(PSstr)) + PSstr
			line = reconstructLine2(words)

		newTFList.append(line)


		# 4th line, just add
		newTFList.append(oldTFList[3])

		NewTFData[CAPEKey] = newTFList




	##################################

	# implement the tf changes
	for line in changeLines:
		if line == '':
			continue
		if '->' not in line: # skip header
			continue
		words = line.split('->')
		planningData = words[0].split(',')
		CAPEData  = words[1].split(',')

		planningKey = words[0].strip() # key for TFDataDict
		CAPEKey = words[1].strip()

		primaryHVplanning = 1 # 1 means Bus1 is HV, 0 means Bus2 is HV
		# arrange the planning buses according to voltage level (HV always primary)
		#if planningBusVoltDict[planningData[0].strip()] > 40.0:
		if float(planningBusDataDict[planningData[0].strip()].NominalVolt) > 40.0:
			planningBus1 = planningData[0].strip()
			planningBus2 = planningData[1].strip()
		else:
			planningBus1 = planningData[1].strip()
			planningBus2 = planningData[0].strip()
			primaryHVplanning = 0

		# get ckt id if any
		if len(planningData) > 2:
			planningcktID  = planningData[2].strip("'")
			

		# arrange the CAPE buses according to voltage level (HV always primary)
		CAPEHVplanning = 1 # 1 means Bus1 is HV, 0 means Bus2 is HV
		if float(CAPEBusDataDict[CAPEData[0].strip()].NominalVolt) > 40.0:
			CAPEBus1 = CAPEData[0].strip()
			CAPEBus2 = CAPEData[1].strip()
		else:
			CAPEBus1 = CAPEData[1].strip()
			CAPEBus2 = CAPEData[0].strip()	
			CAPEHVplanning = 0

		# update the map dict with data here
		#ManualMapDictCAPE[CAPEBus1] = planningBus1
		#ManualMapDictCAPE[CAPEBus2] = planningBus2
		#if CAPEBus2 in LoadBusToSkip: # these load buses have already been taken care of in Raw_loadsplit.raw, so move on to next line
		#	continue

		# get ckt id if any
		if len(CAPEData) > 2:
			CAPEcktID  = CAPEData[2].strip("'")	


		generateNewTFData(planningKey,CAPEKey,CAPEData,primaryHVplanning,CAPEHVplanning,NewTFData)

		# extract the relevant info from planning bus data into NewBusData dict, these info will be substituted in the new raw file bus data
		#changeBusData(planningBus1, CAPEBus1)
		#changeBusData(planningBus2, CAPEBus2)


	 
	# generate new raw file with the new bus data, new load data and new tf data
	#with open(oldTFLines,'r') as f:
	#	filecontent = f.read()
	#	fileLines = filecontent.split('\n')



	# change tf data
	i = 0
	while i < len(oldTFLines):

		line = oldTFLines[i]
		if line == '':
			i+=1
			continue
		words = line.split(',')
		Bus1 = words[0].strip()
		Bus2 = words[1].strip()
		Bus3 = words[2].strip()
		cktID = words[3].strip("'").strip()

		if Bus3 != '0': # three winder, just add
			newTFLines.append(line)
			for j in range(4):
				i+=1
				line = oldTFLines[i]
				newTFLines.append(line)

			i+=1 # continue to next tf

		else: # two winder
			key = Bus1+','+Bus2+','+cktID
			keyBusOrderSwitched = Bus2 + ',' + Bus1 + ',' + cktID
			if key in NewTFData.keys():
				newTFList = NewTFData[key] # list containing tf data
				for ele in newTFList:
					newTFLines.append(ele)
				i+=4 # continue to next tf

			elif keyBusOrderSwitched in NewTFData.keys(): # switch bus order and try to map
				newTFList = NewTFData[keyBusOrderSwitched] # list containing tf data
				for ele in newTFList:
					newTFLines.append(ele)
				i+=4 # continue to next tf

		
			else: # tf need not be changed, add lines
				newTFLines.append(line)
				for j in range(3):
					i+=1
					line = oldTFLines[i]
					newTFLines.append(line)

				i+=1 # continue to next tf



	# generate new raw file
	#with open(newTFLines,'w') as f:
	#	for line in newTFLines:
	#		f.write(line)
	#		f.write('\n')

	return newTFLines


if __name__ == '__main__':
	from getBusDataFn import getBusData
	# test the fn
	#planningRAW = 'hls18v1dyn_1219.raw'
	#OldRAW = 'RAW0509.raw'
	#newRAW = 'RAW0509_tmp.raw'
	#changeLines = ['270797,274650,1-> 274650,5286,1']
	#planningBusDataDict = getBusData(planningRAW)
	#CAPEBusDataDict = getBusData(OldRAW)
	#doTFMaps(changeLines,OldRAW,newRAW,planningBusDataDict,CAPEBusDataDict)