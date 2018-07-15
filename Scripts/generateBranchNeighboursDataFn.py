"""
Provides a function which organizes the branch impedance and tf impedance data into a class
"""

import math


def generateNeighbours(Raw):

	class BranchData(object):
		def __init__(self):
			self.toBus = []
			self.R = []
			self.X = []
			#self.cktID = []
			self.Z = []


	BranchNeighbourDict = {}
	BranchDataDict = {}
	ComedBusSet = set()

	def BusAppend(Bus,NeighbourBus,NeighbourDict):
		if Bus not in NeighbourDict.keys():
			NeighbourDict[Bus] = []
		NeighbourDict[Bus].append(NeighbourBus)

	def parallel(Z1,Z2):
		# calculate parallel impedance
		if Z1 == 0.0:
			Zp = Z2
		elif Z2 == 0.0:
			Zp = Z1
		else:
			Zp = (Z1*Z2)/(Z1+Z2)
		return Zp


	def generateBranchData(BranchDataDict,Bus1,Bus2,R,X,Z):
		if Bus1 not in BranchDataDict.keys():
			BranchDataDict[Bus1] = BranchData()

		if Bus2 not in BranchDataDict[Bus1].toBus:
			BranchDataDict[Bus1].toBus.append(Bus2)
			BranchDataDict[Bus1].R.append(R)
			BranchDataDict[Bus1].X.append(X)
			BranchDataDict[Bus1].Z.append(Z)
		else: # parallel branch
			Bus2Index = BranchDataDict[Bus1].toBus.index(Bus2)
			OldR = BranchDataDict[Bus1].R[Bus2Index]
			OldX = BranchDataDict[Bus1].X[Bus2Index]
			OldZ = BranchDataDict[Bus1].Z[Bus2Index]

			Rp = parallel(OldR,R)
			Xp = parallel(OldX,X)
			Zp = parallel(OldZ,Z)

			BranchDataDict[Bus1].R[Bus2Index] = Rp
			BranchDataDict[Bus1].X[Bus2Index] = Xp
			BranchDataDict[Bus1].Z[Bus2Index] = Zp

		return BranchDataDict





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
					#cktID = words[2].strip("'")
					R = float(words[3].strip())
					X = float(words[4].strip())
					Z = math.sqrt(R**2 + X**2)

					BusAppend(Bus1,Bus2,BranchNeighbourDict)
					BusAppend(Bus2,Bus1,BranchNeighbourDict)
					BranchDataDict = generateBranchData(BranchDataDict,Bus1,Bus2,R,X,Z)
					BranchDataDict = generateBranchData(BranchDataDict,Bus2,Bus1,R,X,Z)


	return BranchNeighbourDict, BranchDataDict

	



