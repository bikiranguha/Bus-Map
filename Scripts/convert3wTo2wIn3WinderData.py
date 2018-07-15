# first, make sure the voltages (primary and secondary ) match on both sides
# If everything is ok, then use the tmap data to find the relevant tf and change the impedances according to planning data
from getBusDataFn import getBusData
from getTFDataFnv2 import getTFData
import math
input_file = 'Winder3To2SubInputs.txt'
#CAPERaw = 'Raw0706.raw'
planningRaw = 'hls18v1dyn_1219.raw' # use raw file which has 2 winder data only
changeLog = 'changeBusNoLog.txt'
tMapFile = 'tmap_Raw0706.raw'
latestTFFile = 'TFSubComplete.txt'
CAPEBusDataDict = getBusData(CAPERaw)
planningBusDataDict = getBusData(planningRaw)
changeDict = {} # old to new dict
tMapDict = {}
SubDict = {}
planningTFDataDict =getTFData(planningRaw)
newTFLines = []
#CAPETFDataDict =  getTFData(CAPERaw)


class SubData(object): 
	# class to store all the data
	def __init__(self):
		self.R = ''
		self.X = ''
		self.SBase = ''
		self.CZ = ''


# get old to new bus number conversions
with open(changeLog,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if 'CAPE' in line:
			continue
		words = line.split('->')
		if len(words) < 2:
			continue
		OldBus = words[0].strip()
		NewBus = words[1].strip()
		changeDict[OldBus] = NewBus


"""
# get the tmaps
with open(tMapFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		words = line.split(',')
		tfKey = words[0].strip()
		tfKeyWords = tfKey.split(',')
		Bus1 = tfKey
		MidPtBus = words[1].strip()
"""
# get the subs
print 'Verified that all the primary and secondary voltage pairs match between planning and CAPE'
with open(input_file,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	for line in fileLines:
		if line == '':
			continue
		words = line.split('->')
		CAPEWords = words[0].split(',')
		planningSide = words[1].strip()
		planningWords = words[1].split(',')
		CAPEBus1 = CAPEWords[0].strip()
		CAPEBus2 = CAPEWords[1].strip()
		CAPEBus3 = CAPEWords[2].strip()
		cktID = CAPEWords[3].strip()



		if CAPEBus1 in changeDict:
			CAPEBus1 = changeDict[CAPEBus1]

		if CAPEBus2 in changeDict:
			CAPEBus2 = changeDict[CAPEBus2]

		if CAPEBus3 in changeDict:
			CAPEBus3 = changeDict[CAPEBus3]
		CAPETFkey = CAPEBus1.rjust(6) + ',' + CAPEBus2.rjust(6) + ',' + CAPEBus3.rjust(6) + ',' + cktID


		planningBus1 = planningWords[0].strip()
		planningBus2 = planningWords[1].strip()
		# get relevant data from planning tf
		CZ = planningTFDataDict[planningSide].CZ
		R = planningTFDataDict[planningSide].R
		X = planningTFDataDict[planningSide].X
		SBase = planningTFDataDict[planningSide].SBase

		# generate key and input data
		SubDict[CAPETFkey] = SubData()
		SubDict[CAPETFkey].R = R
		SubDict[CAPETFkey].X = X
		SubDict[CAPETFkey].SBase = SBase
		SubDict[CAPETFkey].CZ = CZ

		"""
		V1CAPE = float(CAPEBusDataDict[CAPEBus1].NominalVolt)
		V2CAPE = float(CAPEBusDataDict[CAPEBus2].NominalVolt)

		V1planning = float(planningBusDataDict[planningBus1].NominalVolt)
		V2planning = float(planningBusDataDict[planningBus2].NominalVolt)
		

		if V1planning == V1CAPE and V2planning == V2CAPE:
			continue
		elif V1planning == V2CAPE and V2planning == V1CAPE:
			continue
		else:
			print line + ' V1CAPE: ' + str(V1CAPE) + ' V1planning: ' + str(V1planning) + ' V2CAPE: ' + str(V2CAPE) + ' V2planning: ' + str(V2planning)
		"""

# while substituting the tf data, make sure that the CZ data is checked and impedances changed accordingly
with open(latestTFFile,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')

i = 0
while i < len(fileLines):
	line = fileLines[i]
	words = line.split(',')
	Bus1 = words[0].strip()
	Bus2 = words[1].strip()
	Bus3 = words[2].strip()
	cktID = words[3].strip()
	key = Bus1+','+Bus2+','+Bus3+','+cktID
	if Bus3 == '0': # just add the 2 winder data
		newTFLines.append(line)
		for j in range(3):
			i+=1
			line = fileLines[i]
			newTFLines.append(line)
		i+=1
	else: # three winder
		if key in SubDict:
			# compare CZ data and change R,X values from planning as necessary
			planningCZ = SubDict[key].CZ
			R = SubDict[key].R
			X = SubDict[key].X
			SBase = SubDict[key].SBase
			CZCAPE = words[5].strip()
			if CZCAPE == planningCZ:
				finalR = R
				finalX = X
			else:
				if CZCAPE == '1':
					if planningCZ == '2':
						finalR = float(R)/float(SBase)*100.0
						finalX = float(X)/float(SBase)*100.0


					if planningCZ == '3':
						PLoss = float(R)
						Z = float(X)
						finalR = ((PLoss/10**6)*100/SBase**2)
						finalZ = Z*100.0/SBase
						finalX = math.sqrt(finalZ**2 - finalR**2)

				# convert to string
				finalR = '%.5E' %finalR
				finalX = '%.5E' %finalX




r12 = ((ploss/10^6)*sbase/bas12^2);
z12 = Z*sbase/bas12;
x12 = sqrt(z12^2 -r12^2);

		else: # thXee winder is not interesting, just add 
			newTFLines.append(line)
			for j in range(4):
				i+=1
				line = fileLines[i]
				newTFLines.append(line)
			i+=1





# From the tmap, get the midpoints
# Get the total impedance (be consistent with CZ) from primary to secondary in CAPE and get weights to scale the CAPE data, using corresponding planning impedance
# Generate a dict where all the 2 winder tf need to be changed have the new R, X values, using the old values and the weights