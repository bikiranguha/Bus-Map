# compiles the new raw file, using the new comed CAPE data and the non-comed planning data

#import cutoutComed

newdir = 'Final Result'

AllMapFile = 'AllMappedBusData.txt'
newGenFile = 'verifiedGenData.txt'
newLoadFile = 'newLoadDataConflictResolved.txt'
newbranchFile = 'newbranchData.txt'
newtfFile = 'TFIter3.txt'
newfsFile = 'fixedShuntData.txt'
newssFile = 'newShuntData.txt'
miscDataFile = 'miscData.txt'


PSSErawFile = 'hls18v1dyn_1219.raw'
croppedBusFile = 'croppedBusFile.txt'
croppedLoadFile = 'croppedLoadFile.txt'
croppedoutBranchFile = 'croppedBranchFile.txt'
croppedtfFile = 'croppedtfFile.txt'
croppedGenFile = 'croppedGenFile.txt'
croppedfsFile = 'croppedfsFile.txt'
croppedssFile = 'croppedssFile.txt'
#BoundaryMapClean = 'BoundaryplanningMapCleaned.txt'
#boundaryFile = 'boundaryFile.txt'
#BoundaryMapManual = 'BoundaryMapManual.txt'


godFile = 'RAW0406018.raw'
godFilePath = newdir + '/' + godFile
# Bus data

with open(AllMapFile,'r') as f:
	ComedBusData = f.read()
with open(croppedBusFile,'r') as f:
	otherBusData = f.read()


# Load data
with open(newLoadFile,'r') as f:
	ComedLoadData = f.read()

with open(croppedLoadFile,'r') as f:
	otherLoadData = f.read()	

#Fixed shunt data
with open(newfsFile,'r') as f:
	ComedfsData  = f.read()
with open(croppedfsFile,'r') as f:
	otherfsData = f.read()

# Gen data

with open(newGenFile,'r') as f:
	ComedGenData = f.read()
with open(croppedGenFile,'r') as f:
	otherGenData = f.read()

# Branch data
with open(newbranchFile,'r') as f:
	ComedBranchData = f.read()
with open(croppedoutBranchFile,'r') as f:
	otherBranchData = f.read()

# Transformer data
with open(newtfFile,'r') as f:
	ComedtfData = f.read()
with open(croppedtfFile,'r') as f:
	othertfData = f.read()

# Misc data (such as Area, zone)
with open(miscDataFile,'r') as f:
	miscData = f.read()

# switched shunt data
with open(newssFile,'r') as f:
	ComedssData = f.read()
with open(croppedssFile,'r') as f:
	otherssData = f.read()

with open('footer.txt','r') as f:
	footerData = f.read()

with open(godFile,'w') as f:
	f.write('0,   100.00, 33, 1, 1, 60.00     / PSS(R)E-33.3    TUE, DEC 13 2016  22:08')
	f.write('\n')
	f.write('COMED 2018,  HLS18V1, N18S OUTSIDE AND 18 INTCHNG')
	f.write('\n')
	f.write('DYNAMICS REVSION 01')
	f.write('\n')

	f.write(ComedBusData)
	f.write(otherBusData)
	f.write('\n')
	f.write('0 / END OF BUS DATA, BEGIN LOAD DATA')
	f.write('\n')
	f.write(ComedLoadData)
	f.write(otherLoadData)
	f.write('\n')
	f.write('0 / END OF LOAD DATA, BEGIN FIXED SHUNT DATA')
	f.write('\n')
	f.write(ComedfsData)
	f.write(otherfsData)
	f.write('\n')
	f.write('0 / END OF FIXED SHUNT DATA, BEGIN GENERATOR DATA')
	f.write('\n')
	f.write(ComedGenData)
	f.write(otherGenData)
	f.write('\n')
	f.write('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA')
	f.write('\n')
	f.write(ComedBranchData)
	f.write(otherBranchData)
	f.write('\n')
	f.write('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')
	f.write('\n')
	f.write(ComedtfData)
	f.write(othertfData)
	f.write('\n')
	f.write('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')
	f.write('\n')
	f.write(miscData)
	f.write('\n')
	f.write(ComedssData)
	f.write(otherssData)
	f.write('\n')
	f.write(footerData)




cleanLines = []
with open(godFile,'r')  as f:
	content = f.read()
	lines = content.split('\n')
	for line in lines:
		if line != '':
			cleanLines.append(line)
cleangodFile = newdir + '/' +  godFile
with open(cleangodFile,'w') as f:
	for line in cleanLines:
		f.write(line)
		f.write('\n')










