import math

def getBranchTFData(Raw):
	# generates a structure which stores all the branch and tf impedance info

	ComedBusSet = set()
	BranchTFDataDict = {}

	class BranchTFData(object):
		def __init__(self):
			self.toBus = []
			self.R = []
			self.X = []
			self.Z = []

	def parallel(Z1,Z2):
		# calculate parallel impedance
		if Z1 == 0.0:
			Zp = Z2
		elif Z2 == 0.0:
			Zp = Z1
		else:
			Zp = (Z1*Z2)/(Z1+Z2)
		return Zp


	def getBranchTFInfo(Bus1,Bus2,R,X,BranchTFDataDict):
		# generate branch impedance info structure
		Z = math.sqrt(R**2 + X**2)
		if Bus1 not in BranchTFDataDict.keys():
			BranchTFDataDict[Bus1] = BranchTFData()
		if Bus2 not in BranchTFDataDict[Bus1].toBus:
			BranchTFDataDict[Bus1].toBus.append(Bus2)
			BranchTFDataDict[Bus1].R.append(R)
			BranchTFDataDict[Bus1].X.append(X)
			BranchTFDataDict[Bus1].Z.append(Z)
		else: # Bus 2 already had another branch connection to Bus 1
			print Bus1 + ',' + Bus2
			ind = BranchTFDataDict[Bus1].toBus.index(Bus2)
			OldR = BranchTFDataDict[Bus1].R[ind]
			OldX = BranchTFDataDict[Bus1].X[ind]
			OldZ = BranchTFDataDict[Bus1].Z[ind]
			Rp = parallel(R,OldR)
			Xp = parallel(X,OldX)
			Zp = parallel(Z,OldZ)
			BranchTFDataDict[Bus1].R[ind] = Rp
			BranchTFDataDict[Bus1].X[ind] = Xp
			BranchTFDataDict[Bus1].Z[ind] = Zp


	##############

	with open(Raw, 'r') as f:
		filecontent = f.read()
		fileLines = filecontent.split('\n')


	for line in fileLines:
		if ('PSS' in line) or ('COMED' in line):
			continue
		if 'END OF BUS DATA' in line:
			break
		words = line.split(',')
		if len(words) <2:
			continue
		Bus = words[0].strip()
		area = words[4].strip()
		if area == '222':
			ComedBusSet.add(Bus)
		#AreaDict[Bus] = area


	print 'List of branches or tf which constitute parallel connections between two buses:'
	# extract branch impedance data
	branchStartIndex = fileLines.index('0 / END OF GENERATOR DATA, BEGIN BRANCH DATA') + 1
	branchEndIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA')

	for i in range(branchStartIndex, branchEndIndex):
		line = fileLines[i]
		words = line.split(',')
		Bus1 = words[0].strip()
		Bus2 = words[1].strip()
		status = words[-5].strip()

		if Bus1 in ComedBusSet or Bus2 in ComedBusSet:
			if status == '1':
				R = float(words[3].strip())
				X = float(words[4].strip())
				getBranchTFInfo(Bus1,Bus2,R,X,BranchTFDataDict)
				getBranchTFInfo(Bus2,Bus1,R,X,BranchTFDataDict)


	# extract tf impedance data
	tfStartIndex = fileLines.index('0 / END OF BRANCH DATA, BEGIN TRANSFORMER DATA') + 1
	tfEndIndex = fileLines.index('0 / END OF TRANSFORMER DATA, BEGIN AREA DATA')
	i = tfStartIndex
	while i < tfEndIndex:
		line = fileLines[i]
		words = line.split(',')
		Bus1 = words[0].strip()
		Bus2 = words[1].strip()
		Bus3 = words[2].strip()
		status = words[11].strip()
		CZ = words[5].strip()


		if Bus1 not in ComedBusSet: # non-comed tf, increment i and continue
			i+=4
			continue

		if status == '1': # get tf data
			i+=1
			line = fileLines[i]
			words = line.split(',')
			R = float(words[0].strip())
			X = float(words[1].strip())

			if CZ == '1':
				Sbase = 100.0
			else:
				Sbase = float(words[2].strip())

			R = R*100.0/Sbase # convert to a base of 100 MVA
			X = X*100.0/Sbase # convert to a base of 100 MVA

			getBranchTFInfo(Bus1,Bus2,R,X,BranchTFDataDict)
			getBranchTFInfo(Bus2,Bus1,R,X,BranchTFDataDict)
			i+=3
		else: # tf is off
			i+=4


	return BranchTFDataDict