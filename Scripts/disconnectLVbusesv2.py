"""
Script to disconnect all the LV buses which are unimportant and which do not have any connections to the HV side
The important buses are in imp_bus_set
"""


from genLoadImpSet import imp_bus_set
from generateNeighbours_Disconnect import BranchConnDict, tfConnDict
# scan all the tf conn of HV buses going down to the LV side
# if the LV buses do not appear in imp_bus_set, then make a set which will disconnect them
# if the LV buses do appear in the imp_bus_set, then scan its neighbour. If neighbours are not in imp_bus_set, disconnect the neighbours

raw_file = 'RAW0406018.raw' # using this rawfile to avoid 2 winder midpoint sets
winder2_raw_fixed_load = 'testRAW04052018_fixedload.raw' # latest raw file before islanding, as of 04/10/18
toDisconnectFile = 'todisconnectv2.txt'
newRawFIle = 'tmpv2.raw'


BusVoltDict = {}
BusAngleDict = {}
BusVoltpuDict = {}
ComedBusSet = set()
disconnectSet = set()
newRawLines = []
tfLVBusSet = set() # set of LV buses which are connected to HV buses through step up transformer

def reconstructLine2(words):
	currentLine = ''
	for word in words:
		currentLine += word
		currentLine += ','
	return currentLine[:-1]




# get comed bus voltages
with open(raw_file, 'r') as f:
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
		BusVolt = float(words[2].strip())
		Voltpu = float(words[7].strip())
		BusAngle = float(words[8].strip())
		area = words[4].strip()
		if area == '222':
			ComedBusSet.add(Bus)
			BusVoltDict[Bus] = BusVolt
			BusVoltpuDict[Bus] = Voltpu
			BusAngleDict[Bus] = BusAngle


# generate a set of all LV buses which cannot be disconnected since they are on the LV side of step down tf (HV side > 40 kV)
for Bus in list(ComedBusSet):
	if BusVoltDict[Bus] > 40.0: # HV Bus
		if Bus in tfConnDict.keys(): # Bus has tf connections
			tfNeighbours = tfConnDict[Bus] # tf connections of bus
			for neighbour in tfNeighbours: # scan tf connections of HV bus
				# Update: Do not disconnect any buses connected to transformers which are connected to HV side
				if BusVoltDict[neighbour] < 40.0: # LV bus
				#	if neighbour not in imp_bus_set: # LV bus and not important
				#		disconnectSet.add(neighbour)
				#	else: #LV bus important
					tfLVBusSet.add(neighbour) # adding it to the set makes sure 

#########



for Bus in list(ComedBusSet):
	if BusVoltDict[Bus] > 40.0: # HV Bus
		if Bus in tfConnDict.keys(): # Bus has tf connections
			tfNeighbours = tfConnDict[Bus] # tf connections of bus
			for neighbour in tfNeighbours: # scan tf connections of HV bus
				# Update: Do not disconnect any buses connected to transformers which are connected to HV side
				if BusVoltDict[neighbour] < 40.0: # LV bus
				#	if neighbour not in imp_bus_set: # LV bus and not important
				#		disconnectSet.add(neighbour)
				#	else: #LV bus important
					if neighbour in BranchConnDict.keys(): # if imp LV bus has branches
						#print neighbour
						neighbourBranches = BranchConnDict[neighbour] # get all branches
						for branch in neighbourBranches: # for each branch
							if branch not in imp_bus_set and branch not in tfLVBusSet: # if branch not important, disconnect it
								disconnectSet.add(branch)

					
					tfconnD2 = [b for b in tfConnDict[neighbour] if b != Bus] # depth 2 tf conn of Bus (HV) or depth 1 tf conn of imp LV bus
					if len(tfconnD2) > 0: # other tf connections for the imp LV bus
						for conn in tfconnD2: # for each such connection
							if BusVoltDict[conn] < 40.0 and conn not in imp_bus_set: # conn is a lv bus and is not imp
								if conn not in tfLVBusSet: # conn not connected to any HV bus through transformers
									disconnectSet.add(conn)
								#else:
									#print conn

								"""
								tfconnD3 = [c for c in tfConnDict[neighbour] if c != neighbour] # get any tf connections of conn
								if len(tfconnD3) > 0: # if any other tf conn present
									if 
									doNotDisconnect = 0 # flag to determine if conn should be disconnected or not
									for conn2 in tfconnD3:
										if BusVoltDict[conn2] > 40.0: # if the other side of the tf is a HV bus, we cannot disconnect conn
											doNotDisconnect = 1
											break
									if doNotDisconnect != 1: # conn can be disconnected
											disconnectSet.add(conn)
								"""
					
							
with open(toDisconnectFile,'w') as f:
	f.write('List of buses to disconnect')
	f.write('\n')
	for bus in list(disconnectSet):
		f.write(bus)
		f.write('\n')


with open(winder2_raw_fixed_load,'r') as f:
	filecontent = f.read()
	fileLines = filecontent.split('\n')
	# reconstruct bus status
	for line in fileLines:
		if ('PSS' in line) or ('COMED' in line) or ('DYNAMICS' in line):
			continue
		if 'END OF BUS DATA' in line:
			break
		words = line.split(',')
		if len(words) <2:
			continue
		Bus = words[0].strip()

		if Bus in disconnectSet:
			if words[3] in ['2','3']:
				print 'Following bus data is swing or gen bus, dont delete:'
				print line
			words[3] = '4'
			newline = reconstructLine2(words)
			newRawLines.append(newline)

		else:
			newRawLines.append(line)

# add these two bus lines, for some reason they were missing
newRawLines.append("243083,'05CAMPSS    ', 138.0000,1, 205,1251,   1,1.01145, -55.0773")
newRawLines.append("658082,'MPSSE  7    ', 115.0000,1, 652,1624, 658,1.02055, -45.2697")

busEndIndex = fileLines.index('0 / END OF BUS DATA, BEGIN LOAD DATA')

for i in range(busEndIndex,len(fileLines)):
	line = fileLines[i]
	newRawLines.append(line)


with open(newRawFIle,'w') as f:
	f.write('0,   100.00, 33, 1, 1, 60.00     / PSS(R)E-33.3    TUE, DEC 13 2016  22:08')
	f.write('\n')
	f.write('COMED 2018,  HLS18V1, N18S OUTSIDE AND 18 INTCHNG')
	f.write('\n')
	f.write('DYNAMICS REVSION 01')
	f.write('\n')
	for line in newRawLines:
		f.write(line)
		f.write('\n')


